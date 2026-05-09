## 🏗️ Cấu Trúc Dự Án

```
PTIT-CSDLDPT/
│
├── 📂 source/                              # ⭐ MÃ NGUỒN CHÍNH
│   │
│   ├── 🔴 PIPELINE CHÍNH (XỬ LÝ OFFLINE)
│   │   ├── main.py                         # Entry point: Load parquet → Preprocess → Extract features → Normalize → Save embeddings
│   │   ├── split_data.py                   # Chia nhỏ file âm thanh dài thành đoạn 5 giây
│   │   └── feature_extraction.py           # Core: Trích xuất 108-chiều features (offline + online)
│   │
│   ├── 🟢 DATABASE & STORAGE
│   │   ├── database.py                     # PostgreSQL connection, schema, CRUD operations
│   │   └── indexing.py                     # Tạo vector indexes (IVFFlat, HNSW) trên pgvector
│   │
│   ├── 🔵 SEARCH & RETRIEVAL (QUERY TIME)
│   │   └── retriever.py                    # Vector similarity search → Top-K file tương tự
│   │
│   ├── 🟡 API & FRONTEND
│   │   ├── api.py                          # REST API endpoints (FastAPI)
│   │   │                                   # POST /search, GET /birds, GET /audio/{id}, etc.
│   │   └── app.py                          # UI tương tác (Streamlit)
│   │
│   ├── 📊 TESTING & UTILITIES
│   │   ├── test.py                         # Unit tests cho các modules chính
│   │   └── utils/                          # Helper functions
│   │       ├── config.py                   # Configuration constants (paths, hyperparams)
│   │       ├── data.py                     # Data loading, validation utilities
│   │       └── utils.py                    # General utilities
```

---

### 📋 Mô Tả Chi Tiết Từng Phần

#### **1️⃣ source/ — Mã Nguồn Chính**

| File | Mục Đích | Input | Output |
|------|---------|-------|--------|
| `main.py` | **Orchestrator chính**: Load parquet → Preprocess → Feature extraction → Normalize → Save to DB | Parquet file + config | 108-chiều vectors lưu PostgreSQL |
| `feature_extraction.py` | **Core logic**: Trích xuất 9 loại features (MFCC 60d + Spectral 11d + ...) | Audio bytes (22kHz) | Dict features flattened + 108-d vector |
| `split_data.py` | **Chia nhỏ audio**: Cắt file dài thành đoạn 5 giây | Audio file (.wav/.mp3) | Nhiều đoạn ngắn |
| `database.py` | **DB Management**: Connection, schema, CRUD | Queries, data | PostgreSQL responses |
| `indexing.py` | **Vector Index**: Tạo IVFFlat/HNSW indexes | 108-d vectors | Fast search index |
| `retriever.py` | **Search Engine**: Query vector → Top-K similar | Query vector + top_k | Results ranking |
| `api.py` | **REST Endpoints**: `/search`, `/birds`, `/audio/{id}`, etc. | HTTP requests | JSON responses |
| `app.py` | **Streamlit UI**: Upload audio, visualize results | User interactions | Web interface |
| `test.py` | **Unit Tests**: Validate modules | Test cases | Pass/Fail reports |

#### **2️⃣ data/ — Dữ Liệu**

```
data/
├── Birds Voice.csv          # Dataset gốc: filename, species, audio (bytes)
└── samples/
    ├── Bulbul/              # Loài chim 1
    │   ├── bulbul_001.wav
    │   ├── bulbul_002.wav
    │   └── ...
    ├── Sparrow/             # Loài chim 2
    └── ...
```

- **CSV**: Metadata mapping (file → loài)
- **WAV/MP3**: Audio files (chưa được xử lý)

#### **3️⃣ assert/ — Tài Liệu & Giáo Dục**

| File | Nội Dung |
|------|----------|
| `TOPIC.md` | Yêu cầu đề tài, mục tiêu, phạm vi, timeline |
| `EXPLAINATION_FEATURE.md` | **📖 Giải thích chi tiết** từng feature (9 loại), công thức, ý nghĩa |
| `STRUCTURE_REPORT.MD` | Báo cáo cấu trúc project, phân tích dữ liệu, kết quả |

#### **4️⃣ db/ — Database Initialization**

```sql
-- init.sql
CREATE TABLE birds (...)              -- Danh sách loài
CREATE TABLE audio_files (...)        -- Metadata file
CREATE TABLE acoustic_features (...)  -- Raw features
CREATE TABLE embeddings (...)         -- 108-chiều vectors
CREATE INDEX ... USING ivfflat ...    -- Vector search index
```

#### **5️⃣ Docker & Deployment**

```yaml
# docker-compose.yml
services:
  postgres:
    image: pgvector/pgvector
    ports: 5433:5432
  
  api:
    build: .
    ports: 8000:8000
    command: uvicorn api:app --host 0.0.0.0 --port 8000
  
  streamlit:
    build: .
    ports: 8501:8501
    command: streamlit run app.py
```

Chạy toàn bộ hệ thống: `docker-compose up -d`

---

## 🛠️ Công Nghệ Sử Dụng

| Thành Phần | Công Nghệ | Phiên Bản |
|-----------|-----------|----------|
| **Audio Processing** | Librosa | >=0.11.0 |
| **Data Processing** | Pandas | >=2.3.3 |
| **Vector Database** | PostgreSQL + pgvector | >=0.3 |
| **Backend API** | FastAPI | >=0.135.1 |
| **Web Server** | Uvicorn | >=0.41.0 |
| **Frontend UI** | Streamlit | >=1.55.0 |
| **Containerization** | Docker & Docker Compose | Latest |
| **Python** | Python | >=3.10 |

---

## ⚙️ Cài Đặt & Khởi Chạy

### 1. **Clone và vào thư mục dự án**

```bash
cd /home/ducpham/workspace/PTIT-CSDLDPT
```

### 2. **Chuẩn bị môi trường**

#### Tùy chọn A: Sử dụng Docker (Khuyến nghị)

```bash
# Khởi động các service (PostgreSQL, API, Streamlit)
docker-compose up -d

# Kiểm tra trạng thái
docker-compose ps
```

#### Tùy chọn B: Cài đặt cục bộ

```bash
# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -e .

# Khởi động PostgreSQL (nếu chưa có)
# - Đảm bảo PostgreSQL chạy trên port 5433
# - Tạo database: createdb -p 5433 mydb
# - Chạy init script: psql -p 5433 -d mydb -f db/init.sql
```

### 3. **Khởi chạy các thành phần**

#### Backend API (FastAPI)

```bash
cd source
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

API sẽ chạy tại: `http://localhost:8000`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

#### Frontend UI (Streamlit)

```bash
cd source
streamlit run app.py
```

Mở trình duyệt tại: `http://localhost:8501`

### 4. **Xử lý dữ liệu (Tùy chọn)**

Nếu cần xử lý lại file âm thanh và trích xuất feature:

```bash
cd source
python main.py  # Trích xuất MFCC từ tất cả file âm thanh
```

---

## 🚀 Cách Sử Dụng

### **Via Streamlit UI**

1. Mở `http://localhost:8501`
2. Upload một file âm thanh (`.wav`, `.mp3`, `.flac`, etc.)
3. Điều chỉnh các tùy chọn:
   - **Top-K**: Số kết quả trả về (1-20)
   - **Index Type**: Chọn `ivfflat` hoặc `hnsw`
   - **Hiển thị kết quả trung gian**: Xem chi tiết quá trình tìm kiếm
   - **Lọc theo loài**: Giới hạn tìm kiếm trong một loài (optional)
4. Nhấn **Search**
5. Xem kết quả: 5 file tương tự nhất với điểm similarity

### **Via REST API**

```bash
# 1. Tìm kiếm bằng file âm thanh
curl -X POST http://localhost:8000/search \
  -F "audio_file=@path/to/bird_sound.wav" \
  -F "top_k=5" \
  -F "index_type=ivfflat"

# 2. Lấy danh sách các loài chim
curl http://localhost:8000/birds

# 3. Lấy chi tiết một file âm thanh
curl http://localhost:8000/audio/{file_id}

# 4. Lấy các feature của một file âm thanh
curl http://localhost:8000/audio/{file_id}/features

# 5. Health check
curl http://localhost:8000/health
```

---

## 📊 Cấu Trúc Cơ Sở Dữ Liệu

### **Schema PostgreSQL**

```sql
-- 1. Bảng loài chim
CREATE TABLE birds (
    id SERIAL PRIMARY KEY,
    species_name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT
);

-- 2. Bảng file âm thanh
CREATE TABLE audio_files (
    id SERIAL PRIMARY KEY,
    bird_id INT REFERENCES birds(id),
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    duration FLOAT,
    sample_rate INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng đặc trưng âm học
CREATE TABLE acoustic_features (
    id SERIAL PRIMARY KEY,
    audio_file_id INT REFERENCES audio_files(id),
    feature_name VARCHAR(100),
    feature_values FLOAT8[],  -- Mảng giá trị MFCC
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Bảng vector embedding (hỗ trợ pgvector)
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    audio_file_id INT REFERENCES audio_files(id),
    embedding vector(108),  -- 108-chiều vector (MFCC 60d + Spectral 11d + ZCR 2d + Chroma 12d + RMS 2d)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index cho tìm kiếm vector nhanh
CREATE INDEX embeddings_embedding_idx ON embeddings USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX embeddings_embedding_hnsw_idx ON embeddings USING hnsw (embedding vector_cosine_ops);
```

---

## 🔊 Các Đặc Trưng Âm Học (Features) — 108 Chiều

### **Tổng Quan Vector 108-Chiều**

Hệ thống sử dụng **9 loại đặc trưng** để tạo ra vector embedding 108-chiều:

| STT | Đặc trưng | Số chiều | Ý nghĩa |
|-----|-----------|---------|--------|
| 1 | **MFCC Mean** | 20 | Đặc trưng tổng thể của tiếng chim |
| 2 | **MFCC Std** | 20 | Độ biến thiên của MFCC |
| 3 | **MFCC Delta Mean** | 20 | Sự thay đổi theo thời gian (tần số bộ xử lý) |
| 4 | **MFCC Delta² Mean** | 20 | Gia tốc/thay đổi nhanh chóng |
| 5 | **Spectral Contrast Mean** | 7 | Phân biệt dải tần cao/thấp (rất hiệu quả với tiếng chim) |
| 6 | **Spectral Centroid** | 2 | Mean + Std (giọng cao/thấp) |
| 7 | **Spectral Rolloff** | 1 | Tần số ngưỡng 85% năng lượng |
| 8 | **Spectral Bandwidth** | 1 | Độ rộng phổ |
| 9 | **Spectral Flatness** | 1 | Phân biệt âm nhạc vs noise |
| 10 | **Zero Crossing Rate** | 2 | Mean + Std (phân biệt tần số thô) |
| 11 | **Chroma Features** | 12 | Giai điệu (12 nốt nhạc) |
| 12 | **RMS Energy** | 2 | Mean + Std (độ to) |
| | **TỔNG CỘNG** | **108** | |

---

### **Chi Tiết Từng Đặc Trưng**

#### **1. MFCC (Mel-Frequency Cepstral Coefficients) — 60 chiều**

**MFCC là gì?**
- Bắt chước cách tai người nghe âm thanh (nhạy hơn với tần số thấp)
- Chuyển âm thanh phức tạp (hàng ngàn điểm) thành 60 con số đại diện (20 mean + 20 std + 20 delta mean + 20 delta² mean)
- Loại bỏ thông tin không quan trọng, giữ lại đặc trưng cơ bản

**Thành phần MFCC:**
- **MFCC Mean** (20): Đặc trưng tổng thể trung bình
- **MFCC Std** (20): Độ biến thiên → bắt được tính không đều của tiếng chim
- **MFCC Delta** (20): Tốc độ thay đổi MFCC → bắt được âm điệu (nhanh hay chậm)
- **MFCC Delta²** (20): Gia tốc của thay đổi → bắt được pattern phức tạp hơn

**Tại sao cần cả mean, std, delta, delta²?**
- MFCC Mean: "Cái gì là cái gì" (whatness)
- MFCC Std: "Có ổn định không" (stability)
- MFCC Delta: "Thay đổi nhanh hay chậm" (speed of change)
- MFCC Delta²: "Thay đổi có mịn không" (smoothness)

#### **2. Spectral Contrast (7 chiều) — Phân biệt dải tần cao/thấp**

**Ý nghĩa:**
- Chia phổ thành 7 dải tần số khác nhau
- Mỗi dải tính: Peak - Valley = Độ tương phản
- Tiếng chim rõ → Contrast cao, Background noise → Contrast thấp

**Ứng dụng:** Rất hiệu quả phân biệt tiếng chim vs background noise

#### **3. Spectral Flatness (1 chiều) — Phân biệt âm nhạc vs noise**

**Công thức:** Geometric Mean / Arithmetic Mean
- Flatness **thấp** (≈ 0.2-0.3): Tiếng chim → có peak rõ ràng
- Flatness **cao** (≈ 0.7-0.9): Background noise → phẳng, đều đặn

**Ứng dụng:** Detect và lọc background noise trước khi tính features khác

#### **4. Spectral Centroid (2 chiều) — Giọng cao/thấp**

**Ý nghĩa:** "Trọng tâm" của phổ tần số
- Centroid **cao** → Giọng sáng/sắc (chim cao)
- Centroid **thấp** → Giọng trầm (chim thấp)

#### **5. Spectral Rolloff (1 chiều) — Độ phong phú**

**Ý nghĩa:** Tần số mà tại đó 85% năng lượng nằm bên trái
- Rolloff **cao** → Âm thanh có nhiều harmonics (phong phú)
- Rolloff **thấp** → Âm thanh đơn giản (như còi xe)

#### **6. Spectral Bandwidth (1 chiều) — Độ rộng phổ**

**Ý nghĩa:** Độ rộng của phân bố năng lượng
- Bandwidth **cao** → Âm thanh rộng, phức tạp
- Bandwidth **thấp** → Âm thanh hẹp, thuần khiết

#### **7. Zero Crossing Rate (2 chiều) — Tần số thô**

**Ý nghĩa:** Số lần tín hiệu đi qua 0 trong 1 giây
- ZCR ≈ 2 × Frequency (gần đúng)
- Tần số cao → ZCR cao, Tần số thấp → ZCR thấp

**Ví dụ:**
- Chim trầm (cú): ZCR ≈ 300
- Chim cao (sẻ): ZCR ≈ 2000

#### **8. Chroma Features (12 chiều) — Giai điệu**

**Ý nghĩa:** Nhóm 88 phím piano thành 12 nốt nhạc (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
- Bắt được "giai điệu" của tiếng chim
- Bất biến với octave (cao hay thấp, chỉ quan tâm "nốt nào")

#### **9. RMS Energy (2 chiều) — Độ to**

**Ý nghĩa:** "Độ to" của âm thanh (Root Mean Square)
- RMS **cao** → Chim hót to, RMS **thấp** → Chim hót nhỏ
- Mean + Std: Bắt được cả mức năng lượng lẫn độ biến đổi

---

### **Quy Trình Tạo Vector 108-Chiều**

```
1. Audio raw (22,050 Hz) → 5 giây = 110,250 samples
                     ↓
2. Preprocess:
   - Resample về 22,050 Hz
   - Trim silence (top_db=20)
   - Normalize amplitude [-1, 1]
                     ↓
3. Extract 9 loại features → ~110 giá trị (một số là array)
   - MFCC (60d) + Spectral Contrast (7d) + Spectral Features (5d)
   - ZCR (2d) + Chroma (12d) + RMS (2d) = 88 values
                     ↓
4. Flatten thành scalar columns → 108 chiều
                     ↓
5. StandardScaler (mean=0, std=1) → normalize scales
                     ↓
6. L2 normalization (||vec|| = 1) → unit vector
                     ↓
7. Vector 108-chiều sẵn sàng để lưu vào pgvector + search
```

---

### **Chi Tiết Đầy Đủ**

Xem phần giải thích chi tiết cho mỗi feature: [EXPLAINATION_FEATURE.md](assert/EXPLAINATION_FEATURE.md)

---

## 📈 Quy Trình Tìm Kiếm

```
┌──────────────────────────────────────────────────────────────┐
│ 1. UPLOAD FILE ÂM THANH TỪ USER                             │
│    └─> File mới (.wav, .mp3, .flac, etc.)                   │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. TRÍCH XUẤT 9 LOẠI FEATURES                               │
│    └─> MFCC (60d) + Spectral Contrast/Flatness (8d)        │
│        Spectral Centroid/Rolloff/Bandwidth (4d)             │
│        ZCR (2d) + Chroma (12d) + RMS (2d)                  │
│    └─> Total: 108-dimensional vector                        │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. NORMALIZE & L2 NORMALIZE                                 │
│    └─> StandardScaler (dùng stats từ offline training)     │
│    └─> L2 normalize (||vec|| = 1) → unit vector            │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. VECTOR SIMILARITY SEARCH                                 │
│    └─> So sánh query vector với 500+ vectors trong DB      │
│    └─> Thuật toán: IVFFlat hoặc HNSW (pgvector indexes)   │
│    └─> Metric: Cosine similarity (L2 distance)             │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│ 5. XẾPTHỨ TỰ & TRẢ VỀ KẾT QUẢ                              │
│    └─> Top-5 file tương tự nhất (similarity từ cao→thấp)    │
│    └─> Kèm theo: Filename, Species, Similarity Score        │
└──────────────────────────────────────────────────────────────┘
```
---

## 📝 File Quan Trọng

| File | Mục Đích |
|------|---------|
| [source/main.py](source/main.py) | Chương trình chính: Xử lý dataset, trích xuất 9 loại features, chuẩn hóa, tạo embeddings 108-chiều |
| [source/app.py](source/app.py) | Giao diện Streamlit (frontend) - Upload audio, tìm kiếm, hiển thị kết quả |
| [source/api.py](source/api.py) | REST API backend (FastAPI) - Endpoints cho search, bird list, features |
| [source/database.py](source/database.py) | Quản lý kết nối PostgreSQL và schema DB (birds, audio_files, acoustic_features, embeddings) |
| [source/feature_extraction.py](source/feature_extraction.py) | Trích xuất 9 loại features (MFCC 60d + Spectral 11d + ZCR 2d + Chroma 12d + RMS 2d) → 108-chiều embedding |
| [source/indexing.py](source/indexing.py) | Tạo vector indexes (IVFFlat, HNSW) trên PostgreSQL + pgvector |
| [source/retriever.py](source/retriever.py) | Vector similarity search (cosine/L2 distance) để tìm Top-K file tương tự |
| [assert/TOPIC.md](assert/TOPIC.md) | Yêu cầu đề bài chi tiết |
| [assert/EXPLAINATION_FEATURE.md](assert/EXPLAINATION_FEATURE.md) | Giải thích chi tiết 9 loại features (MFCC, Spectral Contrast/Flatness, ZCR, Chroma, RMS) |