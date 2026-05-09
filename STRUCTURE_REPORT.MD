Đọc xong cả hai file rồi. Đây là cấu trúc báo cáo đầy đủ:

---

# CẤU TRÚC BÁO CÁO
## HỆ CƠ SỞ DỮ LIỆU LƯU TRỮ VÀ TÌM KIẾM TIẾNG CHIM HÓT

---

## MỤC LỤC

1. Mở đầu
2. Bộ dữ liệu tiếng chim
3. Bộ thuộc tính nhận diện tiếng chim
4. Hệ cơ sở dữ liệu quản trị siêu dữ liệu
5. Hệ thống tìm kiếm tiếng chim
6. Demo và đánh giá kết quả
7. Kết luận
8. Tài liệu tham khảo

---

## CHƯƠNG 1. MỞ ĐẦU

### 1.1. Đặt vấn đề
- Tầm quan trọng của việc nhận diện và phân loại tiếng chim trong nghiên cứu sinh thái, bảo tồn đa dạng sinh học
- Hạn chế của phương pháp nhận diện thủ công truyền thống
- Nhu cầu xây dựng hệ thống tìm kiếm âm thanh tự động dựa trên nội dung (Content-Based Audio Retrieval)

### 1.2. Mục tiêu đề tài
- Thu thập và xây dựng bộ dữ liệu 500+ file âm thanh tiếng chim
- Trích xuất bộ đặc trưng âm học đặc trưng cho từng loài
- Xây dựng hệ CSDL lưu trữ và quản trị siêu dữ liệu
- Xây dựng hệ thống tìm kiếm dựa trên độ tương đồng vector (vector similarity search)

### 1.3. Phạm vi và giới hạn
- Số loài chim, số file âm thanh trong dataset
- Định dạng file âm thanh hỗ trợ (.wav, .mp3, .flac, ...)
- Ngôn ngữ lập trình, framework, hệ quản trị CSDL sử dụng

### 1.4. Cấu trúc báo cáo
- Mô tả ngắn gọn nội dung từng chương

---

## CHƯƠNG 2. BỘ DỮ LIỆU TIẾNG CHIM

### 2.1. Nguồn dữ liệu
- Nguồn thu thập (dataset gốc `Birds Voice.csv`, các nguồn công khai như Xeno-canto, BirdCLEF, ...)
- Tiêu chí lựa chọn dữ liệu (chất lượng âm thanh, độ dài file, đa dạng loài, ...)

### 2.2. Thống kê bộ dữ liệu
- Tổng số file âm thanh (≥ 500 file)
- Số loài chim trong dataset
- Bảng thống kê: tên loài — số file — tổng thời lượng
- Phân bố số file theo loài (biểu đồ cột hoặc tròn)

### 2.3. Tiền xử lý dữ liệu
- **Chia nhỏ file** (module `split_data.py`): lý do và tiêu chí cắt đoạn (ví dụ: đoạn 5 giây)
- **Resample**: chuẩn hóa tần số lấy mẫu về 22,050 Hz
- **Trim silence**: loại bỏ đoạn im lặng đầu/cuối (`top_db=20`)
- **Normalize biên độ**: đưa về khoảng [-1, 1]
- Sơ đồ quy trình tiền xử lý

### 2.4. Định dạng và tổ chức lưu trữ file
- Cấu trúc thư mục `data/samples/`
- Quy tắc đặt tên file

---

## CHƯƠNG 3. BỘ THUỘC TÍNH NHẬN DIỆN TIẾNG CHIM

### 3.1. Tổng quan vector đặc trưng 108 chiều
- Lý do lựa chọn biểu diễn âm thanh dưới dạng vector số học
- Bảng tổng quan 9 loại đặc trưng, số chiều, và vai trò

| STT | Đặc trưng | Số chiều | Vai trò |
|-----|-----------|----------|---------|
| 1 | MFCC Mean | 20 | ... |
| 2 | MFCC Std | 20 | ... |
| ... | ... | ... | ... |
| | **Tổng** | **108** | |

### 3.2. Phân tích chi tiết từng đặc trưng

#### 3.2.1. MFCC — Mel-Frequency Cepstral Coefficients (60 chiều)
- Định nghĩa và nguyên lý hoạt động (bắt chước thính giác con người, thang Mel)
- Bốn thành phần: Mean, Std, Delta Mean, Delta² Mean — ý nghĩa của từng thành phần
- Giá trị thông tin: đặc trưng "vân tay" cơ bản nhất của giọng chim
- Ví dụ minh họa (hình ảnh MFCC spectrogram nếu có)

#### 3.2.2. Spectral Contrast (7 chiều)
- Định nghĩa: chênh lệch giữa peak và valley trong từng dải tần
- Tại sao hiệu quả với tiếng chim: phân biệt tiếng hót rõ vs. tạp âm nền
- Phân tích 7 dải tần số

#### 3.2.3. Spectral Centroid (2 chiều — Mean + Std)
- Định nghĩa: "trọng tâm" năng lượng phổ tần số
- Phân biệt chim giọng cao vs. giọng trầm

#### 3.2.4. Spectral Rolloff (1 chiều)
- Định nghĩa: tần số ngưỡng chứa 85% năng lượng
- Ý nghĩa: phản ánh độ phong phú harmonics của tiếng chim

#### 3.2.5. Spectral Bandwidth (1 chiều)
- Định nghĩa: độ rộng phân bố năng lượng quanh centroid
- Phân biệt tiếng hót phức tạp vs. đơn giản

#### 3.2.6. Spectral Flatness (1 chiều)
- Định nghĩa: tỉ lệ Geometric Mean / Arithmetic Mean
- Ứng dụng: phát hiện và lọc tạp âm (noise detection)

#### 3.2.7. Zero Crossing Rate — ZCR (2 chiều — Mean + Std)
- Định nghĩa: số lần tín hiệu vượt qua 0 trong 1 giây
- Mối quan hệ với tần số cơ bản; ví dụ so sánh giữa các loài

#### 3.2.8. Chroma Features (12 chiều)
- Định nghĩa: phân bố năng lượng theo 12 nốt nhạc (C đến B)
- Ý nghĩa âm nhạc học; bất biến với octave — ưu điểm khi so sánh giọng chim

#### 3.2.9. RMS Energy (2 chiều — Mean + Std)
- Định nghĩa: Root Mean Square của tín hiệu
- Phản ánh độ to và sự ổn định âm lượng

### 3.3. Quy trình chuẩn hóa vector đặc trưng
- **StandardScaler**: chuẩn hóa về phân phối chuẩn (mean=0, std=1) — tránh đặc trưng lớn lấn át đặc trưng nhỏ
- **L2 Normalization**: đưa về unit vector (‖v‖ = 1) — đảm bảo cosine similarity tính đúng
- Sơ đồ pipeline trích xuất đặc trưng từ raw audio → vector 108 chiều

### 3.4. Lý do lựa chọn tổ hợp đặc trưng này
- So sánh với các phương án khác (chỉ dùng MFCC, chỉ dùng spectrogram thô, ...)
- Tính bổ sung lẫn nhau giữa các nhóm đặc trưng
- Tương quan giữa số chiều và hiệu năng tìm kiếm

---

## CHƯƠNG 4. HỆ CƠ SỞ DỮ LIỆU QUẢN TRỊ SIÊU DỮ LIỆU

### 4.1. Kiến trúc tổng thể hệ CSDL
- Lý do chọn PostgreSQL + pgvector
- Sơ đồ kiến trúc: các thành phần, luồng dữ liệu

### 4.2. Thiết kế Schema

#### 4.2.1. Bảng `birds` — Thông tin loài chim
- Mô tả các trường, ràng buộc, ý nghĩa
- Ví dụ dữ liệu mẫu

#### 4.2.2. Bảng `audio_files` — Thông tin file âm thanh
- Các trường siêu dữ liệu: filename, file_path, duration, sample_rate, created_at, ...
- Quan hệ với bảng `birds`

#### 4.2.3. Bảng `acoustic_features` — Đặc trưng âm học dạng mảng
- Lưu trữ từng loại đặc trưng dưới dạng `FLOAT8[]`
- Mục đích: tra cứu đặc trưng chi tiết, phân tích

#### 4.2.4. Bảng `embeddings` — Vector embedding 108 chiều
- Kiểu dữ liệu `vector(108)` của pgvector
- Quan hệ với bảng `audio_files`

#### 4.2.5. Sơ đồ ERD (Entity-Relationship Diagram)

### 4.3. Vector Index cho tìm kiếm nhanh

#### 4.3.1. IVFFlat Index
- Nguyên lý: phân cụm không gian vector, tìm kiếm xấp xỉ
- Tham số cấu hình (số danh sách, số danh sách duyệt khi query)
- Câu lệnh SQL tạo index

#### 4.3.2. HNSW Index (Hierarchical Navigable Small World)
- Nguyên lý: đồ thị phân cấp, duyệt theo "láng giềng gần"
- Ưu/nhược điểm so với IVFFlat
- Câu lệnh SQL tạo index

#### 4.3.3. So sánh hai loại index
- Bảng so sánh: tốc độ truy vấn, bộ nhớ, độ chính xác (recall), thời gian build

### 4.4. Cơ chế tìm kiếm dựa trên siêu dữ liệu

#### 4.4.1. Tìm kiếm theo metadata thuần túy
- Lọc theo loài (`species_name`)
- Lọc theo thời lượng, sample rate, ngày tạo

#### 4.4.2. Tìm kiếm vector similarity
- Độ đo Cosine Similarity — công thức và ý nghĩa
- Câu lệnh SQL ví dụ với pgvector (`<=>` operator)

#### 4.4.3. Tìm kiếm kết hợp (Hybrid Search)
- Kết hợp lọc metadata + vector similarity trong một truy vấn
- Ví dụ: tìm trong một loài cụ thể, lấy top-5 tương đồng nhất

---

## CHƯƠNG 5. HỆ THỐNG TÌM KIẾM TIẾNG CHIM

### 5.1. Sơ đồ khối tổng thể hệ thống
- Sơ đồ kiến trúc 3 tầng: Frontend (Streamlit) — Backend API (FastAPI) — Database (PostgreSQL + pgvector)
- Mô tả vai trò từng thành phần

### 5.2. Quy trình xử lý một yêu cầu tìm kiếm

Trình bày theo sơ đồ khối 5 bước:

```
[Upload file âm thanh] → [Tiền xử lý] → [Trích xuất vector 108 chiều]
→ [Chuẩn hóa & L2 Normalize] → [Vector Similarity Search]
→ [Xếp hạng & Trả kết quả Top-5]
```

Mô tả chi tiết từng bước, input/output của mỗi bước.

### 5.3. Các kết quả trung gian của quá trình tìm kiếm

#### 5.3.1. File âm thanh đầu vào — Dạng sóng và spectrogram
- Hình ảnh waveform của file query
- Hình ảnh mel-spectrogram

#### 5.3.2. Vector đặc trưng trước chuẩn hóa
- Bảng giá trị 108 chiều (hoặc từng nhóm đặc trưng)
- Nhận xét về phân phối giá trị, phát hiện bất thường

#### 5.3.3. Vector đặc trưng sau chuẩn hóa
- So sánh phân phối trước và sau StandardScaler
- Kiểm tra ‖v‖ = 1 sau L2 normalize

#### 5.3.4. Kết quả truy vấn vector similarity
- Top-5 kết quả với điểm cosine similarity
- Bảng: Rank — Filename — Loài — Similarity Score
- Trường hợp loài **đã có** trong CSDL
- Trường hợp loài **chưa có** trong CSDL

### 5.4. REST API — Các endpoint chính

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/search` | Tìm kiếm Top-K file tương tự |
| GET | `/birds` | Danh sách các loài chim |
| GET | `/audio/{id}` | Chi tiết một file âm thanh |
| GET | `/audio/{id}/features` | Đặc trưng của một file |
| GET | `/health` | Kiểm tra trạng thái hệ thống |

### 5.5. Giao diện người dùng (Streamlit)
- Mô tả luồng sử dụng: upload → cấu hình → search → xem kết quả
- Ảnh chụp màn hình giao diện (screenshot)
- Tùy chọn: Top-K, loại index (IVFFlat/HNSW), lọc theo loài, hiển thị kết quả trung gian

### 5.6. Triển khai hệ thống với Docker
- Mô tả `docker-compose.yml`: các service (PostgreSQL, API, Streamlit), cổng, volume
- Hướng dẫn khởi chạy nhanh

---

## CHƯƠNG 6. DEMO VÀ ĐÁNH GIÁ KẾT QUẢ

### 6.1. Môi trường thực nghiệm
- Cấu hình phần cứng (CPU, RAM, ổ cứng)
- Phiên bản phần mềm (Python, PostgreSQL, pgvector, Librosa, ...)

### 6.2. Demo hệ thống

#### 6.2.1. Kịch bản 1 — File truy vấn thuộc loài đã có trong CSDL
- File đầu vào, loài tương ứng
- Top-5 kết quả, similarity score
- Nhận xét: kết quả Top-1/5 có đúng loài không?

#### 6.2.2. Kịch bản 2 — File truy vấn thuộc loài chưa có trong CSDL
- File đầu vào, loài thực tế
- Top-5 kết quả, similarity score
- Nhận xét: hệ thống trả về loài nào gần nhất? Có hợp lý không?

#### 6.2.3. So sánh IVFFlat vs HNSW
- Thời gian truy vấn trung bình
- Recall@5 (tỉ lệ kết quả đúng trong Top-5)

### 6.3. Đánh giá chất lượng tìm kiếm

#### 6.3.1. Độ chính xác (Precision@5)
- Tỉ lệ file trong Top-5 đúng loài với file truy vấn

#### 6.3.2. Recall@5
- Tỉ lệ tìm được file đúng trong tổng số file cùng loài

#### 6.3.3. Thời gian phản hồi
- Thời gian trích xuất đặc trưng
- Thời gian truy vấn CSDL
- Tổng thời gian end-to-end

### 6.4. Phân tích kết quả và thảo luận
- Trường hợp hệ thống hoạt động tốt
- Trường hợp hệ thống gặp khó khăn (tiếng ồn nền cao, loài có tiếng hót tương tự nhau, ...)
- Nguyên nhân và hướng khắc phục

---

## CHƯƠNG 7. KẾT LUẬN

### 7.1. Kết quả đạt được
- Tóm tắt những gì đã xây dựng được so với yêu cầu đề bài (đối chiếu từng mục 1–5 của TOPIC)

### 7.2. Hạn chế
- Hạn chế về dữ liệu, về đặc trưng, về hệ thống

### 7.3. Hướng phát triển
- Tăng kích thước dataset
- Thử nghiệm đặc trưng học sâu (CNN embedding, BirdNET, ...)
- Xây dựng module nhận diện loài tự động (classification)
- Tối ưu hiệu năng cho dataset lớn hơn

---

## TÀI LIỆU THAM KHẢO

- Davis, S., & Mermelstein, P. (1980). Comparison of parametric representations for monosyllabic word recognition in continuously spoken sentences. *IEEE Transactions on Acoustics, Speech, and Signal Processing*
- McFee, B., et al. Librosa: Audio and Music Signal Analysis in Python
- Pgvector documentation
- BirdCLEF / Xeno-canto dataset papers
- Các tài liệu khác sử dụng trong quá trình thực hiện

---

> **Ghi chú:** Bạn điền ảnh screenshot, bảng số liệu thực tế, và sơ đồ vào các chỗ được chú thích trong từng mục. Nếu cần mình viết chi tiết nội dung cho bất kỳ chương nào, cứ hỏi thêm nhé!