"""
database.py — Kết nối DB, tạo bảng, và quản lý vector index.

Schema (4 bảng):
    birds             — thông tin loài chim
    audio_files       — siêu dữ liệu file âm thanh  (FK → birds)
    acoustic_features — feature arrays (mfcc, spectral, etc.)  (FK → audio_files)
    embeddings        — vector embedding L2-normalize (FK → audio_files)
"""

import psycopg2
from pgvector.psycopg2 import register_vector

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "dbname": "mydb",
    "user": "admin",
    "password": "admin123",
}

VECTOR_DIM = 108   # Phải khớp với số chiều vector từ build_vector()
INDEX_NAME = "embeddings_embedding_idx"

# Fixed feature array names (phải khớp với keys từ extract_features output)
FEATURE_ARRAYS = {
    'mfcc_mean': 20,              # MFCC mean
    'mfcc_std': 20,               # MFCC std
    'mfcc_delta_mean': 20,        # MFCC delta mean
    'mfcc_delta2_mean': 20,       # MFCC delta² mean
    'spectral_centroid_mean': 1,  # centroid mean (scalar)
    'spectral_centroid_std': 1,   # centroid std (scalar)
    'spectral_rolloff_mean': 1,   # rolloff mean (scalar)
    'spectral_bandwidth_mean': 1, # bandwidth mean (scalar)
    'spectral_contrast_mean': 7,  # 7 subbands
    'spectral_flatness_mean': 1,  # flatness mean (scalar)
    'zcr_mean': 1,                # ZCR mean (scalar)
    'zcr_std': 1,                 # ZCR std (scalar)
    'chroma_mean': 12,            # 12 chroma bins
    'rms_mean': 1,                # RMS mean (scalar)
    'rms_std': 1,                 # RMS std (scalar)
}


def get_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    register_vector(conn)
    return conn


def create_tables(conn):
    """
    Tạo 4 bảng:

    birds             — thông tin loài chim
        id, species_name (UNIQUE), family, description

    audio_files       — siêu dữ liệu mỗi file âm thanh
        id, bird_id FK→birds, file_path, sample_rate, duration_s,
        record_time, device, created_at

    acoustic_features — feature arrays (thay vì 108 scalar columns)
        id, audio_id FK→audio_files, 
        mfcc_mean FLOAT8[20],
        mfcc_std FLOAT8[20],
        ... (13 FLOAT8[] columns total)

    embeddings        — vector embedding L2-normalized
        id, audio_id FK→audio_files, embedding vector(108)
    """
    # Build FLOAT8[] column definitions
    feature_col_defs = ",\n        ".join(
        f'"{fname}" FLOAT8[{fdim}]'
        for fname, fdim in FEATURE_ARRAYS.items()
    )

    with conn.cursor() as cur:
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # DROP old tables nếu schema thay đổi (backward compatibility)
        # Thứ tự: embeddings, acoustic_features, audio_files, birds (FK order)
        cur.execute("DROP TABLE IF EXISTS embeddings CASCADE;")
        cur.execute("DROP TABLE IF EXISTS acoustic_features CASCADE;")
        cur.execute("DROP TABLE IF EXISTS audio_files CASCADE;")
        cur.execute("DROP TABLE IF EXISTS birds CASCADE;")

        # Bảng 1: thông tin loài chim
        cur.execute("""
            CREATE TABLE IF NOT EXISTS birds (
                id           SERIAL PRIMARY KEY,
                species_name TEXT NOT NULL UNIQUE,
                family       TEXT,
                description  TEXT
            );
        """)

        # Bảng 2: siêu dữ liệu file âm thanh
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audio_files (
                id          SERIAL PRIMARY KEY,
                bird_id     INT NOT NULL REFERENCES birds(id) ON DELETE CASCADE,
                file_path   TEXT,
                sample_rate INT,
                duration_s  FLOAT,
                record_time TIMESTAMP,
                device      TEXT,
                created_at  TIMESTAMP DEFAULT NOW()
            );
        """)

        # Bảng 3: feature arrays (gốc, trước normalize)
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS acoustic_features (
                id       SERIAL PRIMARY KEY,
                audio_id INT NOT NULL REFERENCES audio_files(id) ON DELETE CASCADE,
                {feature_col_defs}
            );
        """)

        # Bảng 4: vector embedding
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS embeddings (
                id       SERIAL PRIMARY KEY,
                audio_id INT NOT NULL REFERENCES audio_files(id) ON DELETE CASCADE,
                embedding vector({VECTOR_DIM}) NOT NULL
            );
        """)

        conn.commit()

    print("✅ Tables recreated (old schema dropped):")
    print("   - birds")
    print("   - audio_files")
    print("   - acoustic_features (12 FLOAT8[] array columns)")
    print("   - embeddings (vector(108))")


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
    Tạo vector index trên bảng embeddings.

    Args:
        mode            : "ivfflat" hoặc "hnsw"
        lists           : (IVFFlat) số cluster, thường ~ sqrt(n_records)
        m               : (HNSW) số liên kết mỗi node
        ef_construction : (HNSW) kích thước beam khi xây đồ thị
    """
    mode = mode.lower()
    if mode not in ("ivfflat", "hnsw"):
        raise ValueError(f"Unsupported index mode: '{mode}'. Choose 'ivfflat' or 'hnsw'.")

    with conn.cursor() as cur:
        if mode == "ivfflat":
            sql = f"""
                CREATE INDEX IF NOT EXISTS {INDEX_NAME}
                ON embeddings
                USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = {lists});
            """
            print(f"Creating IVFFlat index (lists={lists}) ...")
        else:  # hnsw
            sql = f"""
                CREATE INDEX IF NOT EXISTS {INDEX_NAME}
                ON embeddings
                USING hnsw (embedding vector_cosine_ops)
                WITH (m = {m}, ef_construction = {ef_construction});
            """
            print(f"Creating HNSW index (m={m}, ef_construction={ef_construction}) ...")

        cur.execute(sql)
        conn.commit()

    print(f"Index '{INDEX_NAME}' ({mode}) created successfully.")
