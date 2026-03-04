"""
indexing.py — Offline pipeline: build table, create vector index, insert embeddings.

Supported index modes:
  - ivfflat : IVFFlat (inverted file, approximate, good for large datasets)
  - hnsw    : HNSW (Hierarchical Navigable Small World, fast query, higher memory)

Usage (CLI):
    python indexing.py --data 0000.parquet --mode ivfflat
    python indexing.py --data 0000.parquet --mode hnsw
"""

import argparse
import pickle

import numpy as np
import pandas as pd
import psycopg2
from pgvector.psycopg2 import register_vector
from psycopg2.extras import execute_values

from feature_extraction import build_vector, normalize_feature_columns, process_dataset

SKIP_META_COLS = {"label", "file_id", "duration_s", "sample_rate"}

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "dbname": "mydb",
    "user": "admin",
    "password": "admin123",
}

VECTOR_DIM = 108  # Phải khớp với số chiều vector từ build_vector()
INDEX_NAME = "bird_sounds_embedding_idx"

def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    register_vector(conn)
    return conn

def create_tables(conn, feature_cols: list[str]):
    """
    Tạo 2 bảng:

    bird_sounds  — metadata + embedding vector (dùng cho ANN search)
        id, file_id, label, duration_s, sample_rate, embedding

    bird_features — giá trị từng feature scalar gốc (dùng để inspect / filter)
        id, bird_id FK→bird_sounds.id, <108 feature columns>
    """
    # Sinh DDL cho 108 cột feature của bảng bird_features
    feature_col_defs = ",\n                ".join(f'"{col}" FLOAT' for col in feature_cols)

    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Bảng 1: siêu dữ liệu + embedding
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS bird_sounds (
                id          SERIAL PRIMARY KEY,
                file_id     INT,
                label       TEXT,
                duration_s  FLOAT,
                sample_rate INT,
                embedding   vector({VECTOR_DIM})
            );
        """)

        # Bảng 2: giá trị feature scalar (raw, trước normalize)
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS bird_features (
                id      SERIAL PRIMARY KEY,
                bird_id INT REFERENCES bird_sounds(id) ON DELETE CASCADE,
                {feature_col_defs}
            );
        """)

        conn.commit()
    print("Tables bird_sounds + bird_features created (or already exist.)")

def drop_index(conn):
    """Xóa index cũ nếu tồn tại (để tạo lại với mode khác)."""
    with conn.cursor() as cur:
        cur.execute(f"DROP INDEX IF EXISTS {INDEX_NAME};")
        conn.commit()
    print(f"Dropped index '{INDEX_NAME}' (if existed).")


def create_index(
    conn,
    mode: str = "ivfflat",
    # IVFFlat params
    lists: int = 40,
    # HNSW params
    m: int = 16,
    ef_construction: int = 64,
):
    """
    Tạo vector index cho bảng bird_sounds.

    Args:
        mode           : "ivfflat" hoặc "hnsw"
        lists          : (IVFFlat) số cluster, thường ~ sqrt(n_records)
        m              : (HNSW) số liên kết mỗi node, tăng -> chính xác hơn / tốn RAM hơn
        ef_construction: (HNSW) kích thước beam khi xây đồ thị, lớn hơn -> chậm build / chính xác hơn
    """
    mode = mode.lower()
    if mode not in ("ivfflat", "hnsw"):
        raise ValueError(f"Unsupported index mode: '{mode}'. Choose 'ivfflat' or 'hnsw'.")

    with conn.cursor() as cur:
        if mode == "ivfflat":
            sql = f"""
                CREATE INDEX IF NOT EXISTS {INDEX_NAME}
                ON bird_sounds
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = {lists});
            """
            print(f"Creating IVFFlat index (lists={lists}) ...")
        else:  # hnsw
            sql = f"""
                CREATE INDEX IF NOT EXISTS {INDEX_NAME}
                ON bird_sounds
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = {m}, ef_construction = {ef_construction});
            """
            print(f"Creating HNSW index (m={m}, ef_construction={ef_construction}) ...")

        cur.execute(sql)
        conn.commit()

    print(f"Index '{INDEX_NAME}' ({mode}) created successfully.")

def insert_records(conn, records: list[dict], feature_cols: list[str]):
    """
    Bulk-insert vào 2 bảng bird_sounds và bird_features.

    records: list of dict với keys:
        file_id    (int)
        label      (str)
        duration_s (float)  — độ dài audio sau preprocess (giây)
        sample_rate(int)    — sample rate sau preprocess
        embedding  (np.ndarray float32) — L2-normalized vector
        features   (dict)   — raw scalar values {col: float} trước normalize
    """
    # ── Step 1: insert bird_sounds, lấy lại id vừa tạo ──────────────────────
    sound_rows = [
        (r["file_id"], r["label"], r["duration_s"], r["sample_rate"], r["embedding"])
        for r in records
    ]
    with conn.cursor() as cur:
        ids = execute_values(
            cur,
            """
            INSERT INTO bird_sounds (file_id, label, duration_s, sample_rate, embedding)
            VALUES %s
            RETURNING id
            """,
            sound_rows,
            template="(%s, %s, %s, %s, %s::vector)",
            fetch=True,          # trả về RETURNING rows
        )
    bird_ids = [row[0] for row in ids]

    # ── Step 2: insert bird_features với raw scalar values ──────────────────
    col_names = ", ".join(f'"{c}"' for c in feature_cols)
    value_placeholders = ", ".join(["%s"] * len(feature_cols))

    feature_rows = [
        [bird_id] + [float(r["features"][col]) for col in feature_cols]
        for bird_id, r in zip(bird_ids, records)
    ]
    with conn.cursor() as cur:
        execute_values(
            cur,
            f"INSERT INTO bird_features (bird_id, {col_names}) VALUES %s",
            feature_rows,
            template=f"(%s, {value_placeholders})",
        )
        conn.commit()

    print(f"Inserted {len(records)} records into bird_sounds + bird_features.")

# ---------------------------------------------------------------------------
# End-to-end offline pipeline
# ---------------------------------------------------------------------------

def run_indexing(
    data_path: str,
    mode: str = "ivfflat",
    stats_path: str = "feature_stats.pkl",
    # IVFFlat
    lists: int = 40,
    # HNSW
    m: int = 16,
    ef_construction: int = 64,
):
    """
    Full offline pipeline:
      1. Load parquet
      2. Extract features
      3. Normalize (StandardScaler) + save stats
      4. Build L2-normalized vectors
      5. Connect DB → create table → drop old index → create new index → insert
    """
    # ----- 1. Load -----
    print(f"\n[1/5] Loading data from '{data_path}' ...")
    df = pd.read_parquet(data_path)
    print(f"      Loaded {len(df)} records.")

    # ----- 2. Extract features -----
    print("[2/5] Extracting features ...")
    feature_df = process_dataset(df)
    print(f"      Extracted {len(feature_df)} records, {len(feature_df.columns)} columns.")

    # ----- 3. Normalize -----
    print("[3/5] Normalizing feature columns (StandardScaler) ...")
    feature_df_norm, stats = normalize_feature_columns(feature_df)
    with open(stats_path, "wb") as f:
        pickle.dump(stats, f)
    print(f"      Stats saved to '{stats_path}'.")

    # ----- 4. Build vectors -----
    print("[4/5] Building L2-normalized embedding vectors ...")
    feature_cols = [c for c in feature_df_norm.columns if c not in SKIP_META_COLS]

    records = []
    for (_, raw_row), (_, norm_row) in zip(feature_df.iterrows(), feature_df_norm.iterrows()):
        vec = build_vector(norm_row, feature_cols)
        records.append({
            "file_id":     int(raw_row["file_id"]),
            "label":       raw_row["label"],
            "duration_s":  float(raw_row.get("duration_s", 0.0)),
            "sample_rate": int(raw_row.get("sample_rate", 22050)),
            "embedding":   vec,
            "features":    {col: float(raw_row[col]) for col in feature_cols},  # raw, trước normalize
        })

    print(f"      Vector dim    : {records[0]['embedding'].shape[0]}")
    print(f"      Feature cols  : {len(feature_cols)}")
    print(f"      Sample duration_s: {records[0]['duration_s']:.3f}s")

    # ----- 5. Database -----
    print(f"[5/5] Connecting to database and indexing (mode={mode}) ...")
    conn = get_connection()
    try:
        create_tables(conn, feature_cols)
        drop_index(conn)
        insert_records(conn, records, feature_cols)
        create_index(conn, mode=mode, lists=lists, m=m, ef_construction=ef_construction)
    finally:
        conn.close()

    print("\nIndexing complete.")

if __name__ == "__main__":

    DATA_PATH = "/home/ducpham/workspace/PTIT-CSDLDPT/data/0000.parquet"
    STATS_PATH = "/home/ducpham/workspace/PTIT-CSDLDPT/data/feature_stats.pkl"

    parser = argparse.ArgumentParser(description="Offline indexing pipeline for bird_sounds.")
    parser.add_argument("--data", default=DATA_PATH, help="Path to parquet file")
    parser.add_argument(
        "--mode",
        default="ivfflat",
        choices=["ivfflat", "hnsw"],
        help="Vector index type (default: ivfflat)",
    )
    parser.add_argument("--stats", default=STATS_PATH, help="Output path for feature stats")
    # IVFFlat
    parser.add_argument("--lists", type=int, default=40, help="[IVFFlat] number of lists (clusters)")
    # HNSW
    parser.add_argument("--m", type=int, default=16, help="[HNSW] max connections per node")
    parser.add_argument("--ef-construction", type=int, default=64, help="[HNSW] ef_construction")

    args = parser.parse_args()

    run_indexing(
        data_path=args.data,
        mode=args.mode,
        stats_path=args.stats,
        lists=args.lists,
        m=args.m,
        ef_construction=args.ef_construction,
    )
