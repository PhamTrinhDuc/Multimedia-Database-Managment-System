"""
indexing.py — Offline pipeline: insert data và build vector index.

Supported index modes:
  - ivfflat : IVFFlat (inverted file, approximate, good for large datasets)
  - hnsw    : HNSW (Hierarchical Navigable Small World, fast query, higher memory)

Supported data sources:
  - Parquet file: Load audio bytes từ parquet, extract features, file_path fallback to "parquet/{file_id}"
  - Samples folder: Load WAV files từ folder, extract features, file_path là real file paths

Usage (CLI):
    # Từ samples folder (WAV files thực) — recommended
    python indexing.py --data data/samples --mode ivfflat
    
    # Từ parquet file (audio bytes)
    python indexing.py --data data/index.parquet --mode ivfflat
    
    # Với HNSW index
    python indexing.py --data data/samples --mode hnsw
"""

import argparse
import os
import pickle
from pathlib import Path

import pandas as pd
from psycopg2.extras import execute_values
from tqdm import tqdm

import io
import librosa
import numpy as np

from process_data.database import (
    create_index,
    create_tables,
    drop_index,
    get_connection,
    FEATURE_ARRAYS,
)
from process_data.feature_extraction import (
    build_vector,
    normalize_feature_columns,
    process_dataset,
    preprocess_audio,
    extract_features,
    flatten_features,
)

SKIP_META_COLS = {"label", "file_id", "duration_s", "sample_rate", "file_path"}


def flatten_arrays_to_scalars(raw_features: dict) -> dict:
    """
    Convert dict of arrays → flat dict of scalars (1-indexed to match flatten_features).
    Ví dụ:
        {'mfcc_mean': np.array([v1, v2, ...])} → {'mfcc_mean_1': v1, 'mfcc_mean_2': v2, ...}
    """
    flat = {}
    for key, value in raw_features.items():
        if isinstance(value, np.ndarray):
            for i, val in enumerate(value.tolist()):
                flat[f"{key}_{i + 1}"] = float(val)  # 1-indexed to match flatten_features()
        else:
            flat[key] = float(value)
    return flat


def scalars_to_arrays(flat_dict: dict, feature_arrays: dict = FEATURE_ARRAYS) -> dict:
    """
    Convert flat dict of scalars → dict of arrays.
    
    Xử lý cả 2 trường hợp:
    1. Arrays (fdim > 1): Tìm key_1, key_2, ..., key_N (1-indexed)
    2. Scalars (fdim == 1): Tìm key (không có suffix), hoặc key_1 nếu được flattened
    
    Ví dụ:
        {'mfcc_mean_1': v1, 'mfcc_mean_2': v2, ..., 'spectral_centroid_mean': v3}
        → {'mfcc_mean': [v1, v2, ...], 'spectral_centroid_mean': [v3]}
    """
    arrays = {}
    for fname, fdim in feature_arrays.items():
        arr = []
        
        if fdim == 1:
            # Scalar: tìm fname (không suffix) hoặc fname_1 (nếu flattened)
            if fname in flat_dict:
                arr = [flat_dict[fname]]
            elif f"{fname}_1" in flat_dict:
                arr = [flat_dict[f"{fname}_1"]]
        else:
            # Array: tìm fname_1, fname_2, ..., fname_fdim (1-indexed)
            for i in range(1, fdim + 1):
                key = f"{fname}_{i}"
                if key in flat_dict:
                    arr.append(flat_dict[key])
        
        if arr:
            arrays[fname] = arr
    
    return arrays


def process_samples_folder(samples_dir: str) -> pd.DataFrame:
    """
    [OFFLINE] Trích xuất feature từ samples folder (WAV files thực).

    Input : Folder với structure: samples/Species_Name/bird_*.wav
    Output: DataFrame feature phẳng (scalar columns) + file_path column

    Ví dụ:
        samples/
        ├── Turdus_merula/
        │   ├── bird_001.wav
        │   ├── bird_002.wav
        ├── Parus_major/
        │   └── bird_001.wav
    """
    feature_list = []
    samples_path = Path(samples_dir)
    file_id_counter = 0
    
    if not samples_path.exists():
        raise FileNotFoundError(f"Samples folder not found: {samples_dir}")
    
    # Scan tất cả species folders
    for species_folder in sorted(samples_path.iterdir()):
        if not species_folder.is_dir():
            continue
        
        species_name = species_folder.name.replace("_", " ")
        wav_files = sorted(species_folder.glob("*.wav"))
        
        if not wav_files:
            continue
        
        print(f"  Processing {species_name}: {len(wav_files)} files")
        
        # Process từng WAV file
        for wav_file in wav_files:
            try:
                # Load audio từ file
                audio_data, sr = librosa.load(str(wav_file), sr=None, mono=True)
                audio_data, sr = preprocess_audio(audio_data, sr)
                raw_features = extract_features(audio_data, sr)
                
                if raw_features:
                    current_features = {
                        'label': species_name,
                        'file_id': file_id_counter,
                        'duration_s': round(len(audio_data) / sr, 4),
                        'sample_rate': sr,
                        'file_path': str(wav_file),  # Real file path
                    }
                    current_features.update(flatten_features(raw_features))
                    feature_list.append(current_features)
                    file_id_counter += 1
                
            except Exception as e:
                print(f"  ⚠️  Error processing {wav_file}: {e}")
                continue
    
    return pd.DataFrame(feature_list)


def insert_records(conn, records: list[dict]):
    """
    Bulk-insert vào 4 bảng theo schema mới.

    records: list of dict với keys:
        file_id    (int)    — index trong dataset
        label      (str)    — tên loài chim (species_name)
        duration_s (float)  — độ dài audio sau preprocess (giây)
        sample_rate(int)    — sample rate sau preprocess
        embedding  (np.ndarray float32) — L2-normalized vector
        features   (dict)   — dict of arrays {fname: [values]}
                             ví dụ: {'mfcc_mean': [v1, v2, ...], 'rms': [v3, v4]}
        file_path  (str, optional) — đường dẫn file thực; nếu None dùng fallback "unknown"
    """
    # ── Step 1: Upsert birds (theo species_name) ─────────────────────────────
    unique_species = list({r["label"] for r in records})
    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO birds (species_name) VALUES %s ON CONFLICT (species_name) DO NOTHING",
            [(s,) for s in unique_species],
        )
        cur.execute(
            "SELECT id, species_name FROM birds WHERE species_name = ANY(%s)",
            (unique_species,),
        )
        species_id_map = {row[1]: row[0] for row in cur.fetchall()}

    # ── Step 2: Insert audio_files, lấy lại id ───────────────────────────────
    audio_rows = [
        (
            species_id_map[r["label"]],
            r.get("file_path") or "unknown",
            r["sample_rate"],
            r["duration_s"],
        )
        for r in records
    ]
    with conn.cursor() as cur:
        audio_id_rows = execute_values(
            cur,
            """
            INSERT INTO audio_files (bird_id, file_path, sample_rate, duration_s)
            VALUES %s
            RETURNING id
            """,
            audio_rows,
            fetch=True,
        )
    audio_ids = [row[0] for row in audio_id_rows]

    # ── Step 3: Insert acoustic_features (dict of arrays) ─────────────────────
    # Build column names from FEATURE_ARRAYS
    col_names = list(FEATURE_ARRAYS.keys())
    col_names_str = ", ".join(f'"{c}"' for c in col_names)
    value_placeholders = ", ".join(["%s"] * len(col_names))
    
    feature_rows = []
    for audio_id, r in zip(audio_ids, records):
        feature_arrays = r["features"]  # dict of arrays
        row = [audio_id]
        for fname in col_names:
            arr = feature_arrays.get(fname, [])
            row.append(arr)  # psycopg2 handles list → FLOAT8[]
        feature_rows.append(row)
    
    with conn.cursor() as cur:
        execute_values(
            cur,
            f'INSERT INTO acoustic_features (audio_id, {col_names_str}) VALUES %s',
            feature_rows,
            template=f"(%s, {value_placeholders})",
        )

    # ── Step 4: Insert embeddings (L2-normalized vector) ─────────────────────
    embedding_rows = [(audio_id, r["embedding"]) for audio_id, r in zip(audio_ids, records)]
    with conn.cursor() as cur:
        execute_values(
            cur,
            "INSERT INTO embeddings (audio_id, embedding) VALUES %s",
            embedding_rows,
            template="(%s, %s::vector)",
        )
        conn.commit()

    print(f"Inserted {len(records)} records into birds / audio_files / acoustic_features (arrays) / embeddings.")

# ---------------------------------------------------------------------------
# End-to-end offline pipeline
# ---------------------------------------------------------------------------

def run_indexing(
    data_path: str,
    mode: str = "ivfflat",
    samples_dir: str = None,
    stats_path: str = "feature_stats.pkl",
    # IVFFlat
    lists: int = 40,
    # HNSW
    m: int = 16,
    ef_construction: int = 64,
):
    """
    Full offline pipeline:
      1. Load data (parquet file OR samples folder)
      2. Extract features
      3. Normalize (StandardScaler) + save stats
      4. Build L2-normalized vectors
      5. Connect DB → create table → drop old index → create new index → insert
    
    Args:
        data_path: Path to parquet file OR samples folder with WAV files
                  - If .parquet: load from parquet bytes (may need --samples for real file_path)
                  - If folder: load from WAV files directly (file_path tự động được set)
        mode: Index mode ('ivfflat' hoặc 'hnsw')
        samples_dir: (Deprecated) Only used if data_path is .parquet
        stats_path: Path to save feature normalization stats
    """
    # ----- 0. Detect input type -----
    # Path là relative to CWD (current working directory)
    data_path_obj = Path(data_path)
    
    is_parquet = str(data_path).endswith('.parquet')
    is_folder = data_path_obj.is_dir()
    is_file = data_path_obj.is_file()
    
    if not (is_parquet or is_folder or is_file):
        raise ValueError(f"data_path must be .parquet file or folder\n"
                        f"  Given: {data_path}\n"
                        f"  CWD: {Path.cwd()}\n"
                        f"  Resolved to: {data_path_obj.resolve()}\n"
                        f"  Exists: {data_path_obj.exists()}")
    
    # Convert to string for later use
    data_path = str(data_path_obj.resolve())
    
    # ----- 1. Load -----
    if is_parquet:
        print(f"\n[1/5] Loading data from parquet '{data_path}' ...")
        df = pd.read_parquet(data_path)
        print(f"      Loaded {len(df)} records from parquet")
    else:  # is_folder
        print(f"\n[1/5] Loading data from samples folder '{data_path}' ...")
        df = process_samples_folder(data_path)
        print(f"      Loaded {len(df)} records from WAV files")

    # ----- 2. Extract features -----
    if is_parquet:
        print("[2/5] Extracting features from parquet bytes ...")
        feature_df = process_dataset(df)
    else:  # is_folder
        print("[2/5] Features already extracted from WAV files ...")
        # feature_df already has flattened features from process_samples_folder
        feature_df = df.copy()
        # Remove file_path from feature columns (metadata)
        if 'file_path' in feature_df.columns:
            feature_df = feature_df  # Keep it, we'll use it later
    
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
        
        # Get raw feature values từ raw_row, flatten to scalar columns,
        # then convert back to arrays format
        raw_flat = {col: float(raw_row[col]) for col in feature_cols}
        feature_arrays = scalars_to_arrays(raw_flat)
        
        records.append({
            "file_id":     int(raw_row["file_id"]),
            "label":       raw_row["label"],
            "duration_s":  float(raw_row.get("duration_s", 0.0)),
            "sample_rate": int(raw_row.get("sample_rate", 22050)),
            "embedding":   vec,
            "features":    feature_arrays,  # dict of arrays
            "file_path":   raw_row.get("file_path"),
        })

    print(f"      Vector dim    : {records[0]['embedding'].shape[0]}")
    print(f"      Feature arrays: {len(FEATURE_ARRAYS)}")
    print(f"      Sample duration_s: {records[0]['duration_s']:.3f}s")

    # ----- 5. Database -----
    print(f"[5/5] Connecting to database and indexing (mode={mode}) ...")
    conn = get_connection()
    try:
        create_tables(conn)  # No feature_cols needed
        drop_index(conn)
        insert_records(conn, records)
        create_index(conn, mode=mode, lists=lists, m=m, ef_construction=ef_construction)
    finally:
        conn.close()

    print("\n✅ Indexing complete.")


if __name__ == "__main__":

    DATA_PATH = "./data/index.parquet"
    STATS_PATH = "./data/feature_stats.pkl"

    parser = argparse.ArgumentParser(
        description="Offline indexing pipeline for bird_sounds.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Indexing từ samples folder (real WAV files)
  python source/indexing.py --data data/samples --mode ivfflat
  
  # Indexing từ parquet (audio bytes)
  python source/indexing.py --data data/index.parquet --mode ivfflat
  
  # Với HNSW index
  python source/indexing.py --data data/samples --mode hnsw
        """
    )
    
    parser.add_argument(
        "--data",
        default=DATA_PATH,
        help="Path to parquet file OR samples folder with WAV files",
    )
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
