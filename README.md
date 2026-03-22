# 🐦 Hệ Thống Tìm Kiếm Tiếng Chim Hót (PTIT-CSDLDPT)

Một hệ thống **lưu trữ và tìm kiếm tiếng chim** sử dụng **trích xuất đặc trưng âm học (MFCC)** và **vector search** với PostgreSQL + pgvector.

---

## 📋 Mô Tả Dự Án

Dự án này xây dựng một hệ thống hoàn chỉnh để:

1. **Thu thập & xử lý dữ liệu**: Sưu tầm bộ dữ liệu gồm 500+ file âm thanh tiếng chim
2. **Trích xuất đặc trưng**: Sử dụng MFCC (Mel-Frequency Cepstral Coefficients) để trích xuất đặc trưng âm học
3. **Lưu trữ**: Quản lý siêu dữ liệu và vector embedding trong PostgreSQL
4. **Tìm kiếm**: Cho phép tìm kiếm 5 file âm thanh tương tự nhất với một file đầu vào bất kỳ
5. **Giao diện**: Cung cấp UI thân thiện cho người dùng qua Streamlit + REST API

---

## 🏗️ Cấu Trúc Dự Án

```
PTIT-CSDLDPT/
├── source/                      # Mã nguồn chính
│   ├── main.py                  # Chương trình chính (xử lý dữ liệu)
│   ├── app.py                   # Giao diện Streamlit frontend
│   ├── api.py                   # REST API backend (FastAPI)
│   ├── database.py              # Kết nối và quản lý DB
│   ├── feature_extraction.py    # Trích xuất MFCC từ âm thanh
│   ├── indexing.py              # Tạo vector index (IVFFlat, HNSW)
│   ├── retriever.py             # Tìm kiếm vector similarity
│   ├── split_data.py            # Chia nhỏ file âm thanh
│   ├── test.py                  # Unit tests
│   ├── utils/                   # Utilities
│   │   ├── config.py
│   │   ├── data.py
│   │   └── utils.py
│   └── notebooks/               # Jupyter notebooks
│       ├── debug.ipynb
│       └── langgraph.ipynb
├── data/                        # Dữ liệu
│   ├── Birds Voice.csv          # Dataset gốc
│   └── samples/                 # File âm thanh mẫu
├── assert/                      # Tài liệu hỗ trợ
│   ├── TOPIC.md                 # Yêu cầu đề bài
│   └── EXPLAINATION_FEATURE.md  # Giải thích chi tiết các feature
├── db/                          # SQL init scripts
│   └── init.sql
├── docker-compose.yml           # Docker Compose config
├── pyproject.toml               # Python project metadata
└── README.md                    # File này
```

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
    embedding vector(108),  -- 108-chiều vector
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index cho tìm kiếm vector nhanh
CREATE INDEX embeddings_embedding_idx ON embeddings USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX embeddings_embedding_hnsw_idx ON embeddings USING hnsw (embedding vector_cosine_ops);
```

---

## 🔊 Các Đặc Trưng Âm Học (Features)

### **MFCC (Mel-Frequency Cepstral Coefficients)**

**MFCC là gì?**
- Bắt chước cách tai người nghe âm thanh (nhạy hơn với tần số thấp)
- Chuyển âm thanh phức tạp (hàng ngàn điểm) thành ~13-20 con số đại diện
- Loại bỏ thông tin không quan trọng, giữ lại đặc trưng cơ bản

**Ví dụ:**
```
Tiếng chim sẻ:     [5.2, -2.1, 0.3, 1.2, -0.8, ...]
Tiếng chim họa mi: [7.8, -0.5, -1.2, 0.6, 1.1, ...]
                   ↑ Khác biệt rõ ràng → Có thể phân biệt!
```

**Tại sao chọn MFCC?**
- ✅ Giảm kích thước dữ liệu (tiết kiệm storage & tối ưu tốc độ)
- ✅ Bất biến với âm lượng (nói to/nhỏ kết quả giống nhau)
- ✅ Bắt chước cách nghe của con người
- ✅ Được chứng minh hiệu quả trong speech/music recognition

Chi tiết đầy đủ xem: [EXPLAINATION_FEATURE.md](assert/EXPLAINATION_FEATURE.md)

---

## 📈 Quy Trình Tìm Kiếm

```
┌─────────────────────────────────────────────────────────────┐
│ 1. UPLOAD FILE ÂM THANH                                     │
│    └─> File mới từ người dùng                               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. TRÍCH XUẤT FEATURES (MFCC)                               │
│    └─> Chuyển audio thành vector đặc trưng                  │
│        5 giây audio → 13-20 con số + embeddings (108-d)    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. TÌM KIẾM VECTOR SIMILARITY                               │
│    └─> So sánh với tất cả vector trong DB                   │
│        Thuật toán: IVFFlat hoặc HNSW                        │
│        Metric: Cosine similarity                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. XẾPTHỨ TỰ & TRẢ VỀ KẾT QUẢ                              │
│    └─> Top-5 file tương tự nhất (sắp xếp theo similarity)   │
│        Kèm theo: Tên file, loài chim, điểm similarity       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧪 Chạy Tests

```bash
cd source
python -m pytest test.py -v

# Hoặc chạy file test trực tiếp
python test.py
```

---

## 📝 File Quan Trọng

| File | Mục Đích |
|------|---------|
| [source/main.py](source/main.py) | Chương trình chính: Xử lý dataset, trích feature, tạo embeddings |
| [source/app.py](source/app.py) | Giao diện Streamlit (frontend) |
| [source/api.py](source/api.py) | REST API backend (FastAPI) |
| [source/database.py](source/database.py) | Quản lý kết nối và schema DB |
| [source/feature_extraction.py](source/feature_extraction.py) | Trích xuất MFCC, embeddings |
| [source/retriever.py](source/retriever.py) | Vector search similarity |
| [assert/TOPIC.md](assert/TOPIC.md) | Yêu cầu đề bài chi tiết |
| [assert/EXPLAINATION_FEATURE.md](assert/EXPLAINATION_FEATURE.md) | Giải thích 20+ feature đầy đủ |

---

## 🐛 Troubleshooting

### **"Không kết nối được tới PostgreSQL"**
```bash
# Kiểm tra PostgreSQL đang chạy
psql -U admin -d mydb -p 5433 -c "SELECT 1"

# Nếu chưa tạo DB:
createdb -p 5433 -U admin mydb
psql -p 5433 -U admin -d mydb -f db/init.sql
```

### **"Module 'librosa' not found"**
```bash
pip install librosa>=0.11.0
```

### **"pgvector extension not installed"**
```bash
# Kết nối vào PostgreSQL
psql -p 5433 -U admin -d mydb

# Chạy SQL
CREATE EXTENSION IF NOT EXISTS vector;
```

### **"Port 8000 đã được sử dụng"**
```bash
# Tìm process sử dụng port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Hoặc sử dụng port khác
python -m uvicorn api:app --port 8001
```

---

## 📚 Tài Liệu Tham Khảo

- **PostgreSQL + pgvector**: https://github.com/pgvector/pgvector
- **Librosa (Audio Processing)**: https://librosa.org/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://docs.streamlit.io/
- **MFCC Chi tiết**: Xem [assert/EXPLAINATION_FEATURE.md](assert/EXPLAINATION_FEATURE.md)

---

## 👥 Tác Giả

**Dự án PTIT (Học Viện Công Nghệ Bưu Chính Viễn Thông)**
- Hệ thống Lưu Trữ và Tìm Kiếm Tiếng Chim Hót
- CSDL và Data Processing

---

## 📄 License

MIT License - Tự do sử dụng và sửa đổi

---

## 🎯 Các Bước Tiếp Theo

- [ ] Mở rộng dataset (>1000 file âm thanh)
- [ ] Tối ưu hóa vector index performance
- [ ] Thêm feature: Phân loại tự động loài chim
- [ ] Deploy lên production (AWS, GCP, etc.)
- [ ] Cải thiện giao diện UI/UX
- [ ] Thêm authentication & access control
