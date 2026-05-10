"""
api.py — FastAPI backend cho hệ thống tìm kiếm tiếng chim hót.

Endpoints:
    POST /search          — upload file âm thanh, trả về top-K kết quả giống nhất
    GET  /birds           — danh sách loài chim trong DB
    GET  /birds/{id}      — thông tin chi tiết 1 loài
    GET  /health          — kiểm tra kết nối DB

Usage:
    uvicorn api:app --reload --port 8000
"""

import pickle
from contextlib import asynccontextmanager
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from process_data.database import get_connection
from process_data.feature_extraction import process_single_audio
from retriever import run_query

STATS_PATH = Path(__file__).parent.parent / "data" / "feature_stats.pkl"

# Load from samples folder hoặc parquet tùy vào data source
# Hiện tại dùng samples folder nên không cần load parquet
DATA_PATH  = None  # Deprecated - không còn dùng parquet bytes

# ---------------------------------------------------------------------------
# App state
# ---------------------------------------------------------------------------

app_state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load feature normalization stats từ indexing pipeline
    with open(STATS_PATH, "rb") as f:
        app_state["stats"] = pickle.load(f)
    # Không cần load parquet nữa - dùng real files từ samples folder
    yield
    app_state.clear()


app = FastAPI(
    title="Bird Sound Retrieval API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class SearchResult(BaseModel):
    rank: int
    audio_id: int
    species_name: str
    similarity: float


class BirdInfo(BaseModel):
    id: int
    species_name: str
    family: str | None
    description: str | None


class SearchResponse(BaseModel):
    results: list[SearchResult]
    intermediate: dict | None = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health")
def health():
    """Kiểm tra kết nối tới PostgreSQL."""
    try:
        conn = get_connection()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search(
    file: UploadFile = File(...),
    top_k: int = Query(default=5, ge=1, le=20),
    mode: str = Query(default="ivfflat", pattern="^(ivfflat|hnsw)$"),
    filter_species: str | None = Query(default=None),
    verbose: bool = Query(default=False),
):
    """
    Upload file âm thanh, trả về top-K kết quả giống nhất.

    - **file**           : file âm thanh (wav, mp3, ogg, flac, ...)
    - **top_k**          : số kết quả trả về (1–20, mặc định 5)
    - **mode**           : ivfflat hoặc hnsw
    - **filter_species** : giới hạn tìm trong một loài cụ thể (optional)
    - **verbose**        : nếu True, trả kèm kết quả trung gian từng bước xử lý
    """
    audio_bytes = await file.read()
    try:
        result = process_single_audio(audio_bytes, app_state["stats"], verbose=verbose)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Feature extraction failed: {e}")

    query_vec = np.array(result["embedding"], dtype=np.float32) if verbose else result

    hits = run_query(query_vec, top_k=top_k, filter_label=filter_species, mode=mode)

    search_results = [
        SearchResult(
            rank=i + 1,
            audio_id=r["audio_id"],
            species_name=r["label"],
            similarity=r["similarity"],
        )
        for i, r in enumerate(hits)
    ]

    return SearchResponse(
        results=search_results,
        intermediate=result["steps"] if verbose else None,
    )


@app.get("/birds", response_model=list[BirdInfo])
def list_birds():
    """Danh sách tất cả loài chim trong CSDL."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, species_name, family, description FROM birds ORDER BY species_name;")
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        BirdInfo(id=r[0], species_name=r[1], family=r[2], description=r[3])
        for r in rows
    ]


@app.get("/birds/{bird_id}", response_model=BirdInfo)
def get_bird(bird_id: int):
    """Thông tin chi tiết một loài chim theo ID."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, species_name, family, description FROM birds WHERE id = %s;",
                (bird_id,),
            )
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Bird id={bird_id} not found.")
    return BirdInfo(id=row[0], species_name=row[1], family=row[2], description=row[3])


@app.get("/audio/{audio_id}")
def get_audio(audio_id: int):
    """Lấy raw audio bytes của một file âm thanh theo audio_files.id."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT file_path FROM audio_files WHERE id = %s;", (audio_id,))
            row = cur.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Audio id={audio_id} not found.")

    file_path = row[0]
    
    try:
        # file_path là real file path (ví dụ: "data/samples/Turdus_merula/bird_001.wav")
        # hoặc fallback format (ví dụ: "parquet/0")
        
        if file_path.startswith("parquet/"):
            # Legacy: file từ parquet - không hỗ trợ nữa
            raise HTTPException(
                status_code=501, 
                detail=f"Audio from parquet format ({file_path}) not supported. Please re-index with samples folder."
            )
        else:
            # Real file path - load từ disk
            audio_file = Path(file_path)
            if not audio_file.exists():
                raise FileNotFoundError(f"Audio file not found: {file_path}")
            
            audio_bytes = audio_file.read_bytes()
            return Response(content=audio_bytes, media_type="audio/wav")
            
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Audio file not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load audio: {e}")
# uvicorn api:app --reload --port 8000