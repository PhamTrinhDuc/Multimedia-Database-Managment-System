# Chương 3: Phân Tích Yêu Cầu và Thiết Kế

## 3.1 Phân Tích Yêu Cầu Chức Năng

### 3.1.1 Yêu Cầu Xử Lý Truy Vấn

**Yêu cầu 1: Xử lý Truy Vấn Cấu Trúc**

Hệ thống phải có khả năng nhận các câu hỏi bằng ngôn ngữ tự nhiên về dữ liệu cấu trúc và chuyển đổi chúng thành các truy vấn cơ sở dữ liệu. Ví dụ, khi người dùng hỏi "Có bao nhiêu bệnh nhân bảo hiểm Medicaid tại Texas năm 2023?", hệ thống phải:

1. Hiểu rằng đây là câu hỏi về thống kê (COUNT)
2. Xác định các thực thể: payer type = Medicaid, location = Texas, year = 2023
3. Xây dựng một truy vấn Cypher phù hợp: `MATCH (p:Patient)-[:HAS_INSURANCE]->(payer:Payer {type: "Medicaid"}), (p)-[:LIVES_IN]->(loc:Location {state: "TX"}) WHERE p.enrollment_year = 2023 RETURN COUNT(p)`
4. Thực thi truy vấn trên Neo4j
5. Trả về kết quả dưới dạng con số với giải thích

**Yêu cầu 2: Xử lý Truy Vấn Ngữ Nghĩa**

Hệ thống phải có khả năng phân tích dữ liệu không có cấu trúc và trích xuất thông tin ngữ nghĩa. Ví dụ, khi hỏi "Bệnh nhân nói gì về chất lượng nhân viên y tế tại bệnh viện A?", hệ thống phải:

1. Tìm kiếm các tài liệu liên quan trong Elasticsearch sử dụng tìm kiếm vector
2. Phân tích cảm xúc và trích xuất các ý kiến chính
3. Tóm tắt kết quả thành các điểm chính dễ hiểu

**Yêu cầu 3: Xử lý Truy Vấn Kết Hợp**

Hệ thống phải có khả năng xử lý các truy vấn phức tạp kết hợp nhiều loại dữ liệu. Ví dụ, "Bệnh viện nào ở California có thời gian chờ cao nhưng đánh giá bệnh nhân tích cực?" đòi hỏi:

1. Truy vấn Neo4j để lấy thời gian chờ của các bệnh viện ở California
2. Tìm kiếm Elasticsearch để phân tích cảm xúc từ các bình luận bệnh nhân
3. Kết hợp và sắp xếp kết quả để tìm bệnh viện có thời gian chờ cao nhưng cảm xúc tích cực

### 3.1.2 Yêu Cầu Quản Lý Trò Chuyện

**Yêu cầu 1: Lưu Trữ Lịch Sử Trò Chuyện**

Hệ thống phải lưu trữ toàn bộ lịch sử trò chuyện của từng người dùng trong PostgreSQL. Mỗi tin nhắn phải chứa:
- ID của người dùng
- ID của cuộc trò chuyện
- Nội dung tin nhắn
- Vai trò (user hay assistant)
- Timestamp tạo
- Timestamp cập nhật lần cuối

**Yêu cầu 2: Duy Trì Ngữ Cảnh Trò Chuyện**

Khi người dùng đặt một câu hỏi mới, hệ thống phải lấy lịch sử trò chuyện trước đó và cung cấp nó cho tác nhân. Tác nhân sử dụng ngữ cảnh này để hiểu các tham chiếu không rõ ràng. Ví dụ:

Câu hỏi 1: "Bệnh viện nào ở Texas?" → Kết quả: [Bệnh viện A, B, C]
Câu hỏi 2: "Cái nào có thời gian chờ lâu nhất?" → Hệ thống hiểu rằng "cái nào" là tham chiếu tới danh sách từ câu hỏi 1

**Yêu cầu 3: Quản Lý Phiên Người Dùng**

Hệ thống phải quản lý các phiên người dùng, theo dõi ai đang đăng nhập, và đảm bảo mỗi người chỉ xem lịch sử trò chuyện của chính họ.

### 3.1.3 Yêu Cầu Trích Xuất Thông Tin

**Yêu cầu 1: Trích Xuất Thực Thể**

Hệ thống phải có khả năng trích xuất các thực thể quan trọng từ câu hỏi của người dùng, bao gồm:
- Tên bệnh viện, bác sĩ, bệnh nhân (nếu có tên cụ thể)
- Loại bảo hiểm (Medicaid, Medicare, Cigna, Aetna, v.v.)
- Địa điểm (tiểu bang, thành phố, quận)
- Khoảng thời gian (năm, tháng, ngày)
- Các chỉ số sức khỏe (diagnostic codes, symptoms, v.v.)

**Yêu cầu 2: Xác Định Loại Truy Vấn**

Hệ thống phải xác định loại của câu hỏi:
- Truy vấn cấu trúc (structured): Dùng Cypher trên Neo4j
- Truy vấn ngữ nghĩa (semantic): Dùng Elasticsearch
- Tra cứu tham khảo (lookup): Dùng cơ sở dữ liệu chẩn đoán
- Truy vấn kết hợp (hybrid): Kết hợp nhiều loại

### 3.1.4 Yêu Cầu Tạo Phản Hồi

**Yêu cầu 1: Tạo Câu Trả Lời Dễ Hiểu**

Hệ thống phải tạo ra các câu trả lời dễ hiểu bằng ngôn ngữ tự nhiên, không phải các kết quả thô từ cơ sở dữ liệu. Ví dụ, thay vì trả về kết quả thô `{"count": 1523, "payer": "Medicaid", "state": "TX", "year": 2023}`, hệ thống phải tạo câu trả lời như "Có 1.523 bệnh nhân bảo hiểm Medicaid ở Texas năm 2023, tăng 12% so với năm 2022."

**Yêu cầu 2: Giải Thích Cách Tính Toán**

Hệ thống phải cung cấp giải thích về cách nó đã đạt được câu trả lời, chẳng hạn:
- Công cụ nào đã được sử dụng (Cypher, Elasticsearch, v.v.)
- Truy vấn cụ thể nào đã được thực thi
- Bao lâu để có kết quả
- Mức độ tin cậy của kết quả (nếu áp dụng)

**Yêu cầu 3: Hỗ Trợ Định Dạng Đa Dạng**

Hệ thống phải có thể trả lời ở nhiều định dạng:
- Văn bản thô
- Bảng dữ liệu (nếu kết quả là danh sách)
- Biểu đồ (nếu kết quả là xu hướng theo thời gian)

### 3.1.5 Yêu Cầu Xác Thực Người Dùng

**Yêu cầu 1: Đăng Ký Người Dùng**

Người dùng mới phải có thể đăng ký bằng email và mật khẩu. Hệ thống phải:
- Kiểm tra xem email đã tồn tại chưa
- Xác thực định dạng email
- Mã hóa mật khẩu trước khi lưu trữ
- Gửi email xác nhận (tùy chọn)

**Yêu cầu 2: Đăng Nhập Người Dùng**

Người dùng phải có thể đăng nhập bằng email và mật khẩu. Hệ thống phải:
- Xác thực thông tin đăng nhập
- Tạo phiên người dùng
- Tạo và trả về access token
- Đảm bảo token hết hạn sau một khoảng thời gian (ví dụ 24 giờ)

**Yêu cầu 3: Quản Lý Phiên**

Hệ thống phải:
- Lưu trữ thông tin phiên trong Redis
- Kiểm tra token của người dùng ở mỗi yêu cầu
- Từ chối yêu cầu nếu token không hợp lệ hoặc hết hạn

## 3.2 Phân Tích Yêu Cầu Phi Chức Năng

### 3.2.1 Yêu Cầu Hiệu Suất

**Thời Gian Phản Hồi**

Hệ thống phải có thời gian phản hồi thấp:
- Phân vị 50 (median): dưới 1 giây
- Phân vị 95 (P95): dưới 3 giây
- Phân vị 99 (P99): dưới 5 giây

Điều này có nghĩa là trong 95% trường hợp, người dùng nhận được câu trả lời trong vòng 3 giây.

**Throughput**

Hệ thống phải có thể xử lý ít nhất 200 truy vấn mỗi ngày, tương đương khoảng 0,15 truy vấn mỗi phút. Nếu có đột biến (spike), hệ thống phải có thể xử lý 10 lần throughput bình thường trong vòng 1-2 phút.

**Khả Dụng Tài Nguyên**

Hệ thống phải tối ưu hóa sử dụng tài nguyên:
- CPU: Không vượt quá 80% sử dụng bình thường
- Bộ nhớ: Không vượt quá 75% sử dụng bình thường
- Dung lượng lưu trữ: Có đủ dung lượng cho dữ liệu tăng 3 năm

### 3.2.2 Yêu Cầu Khả Dụng và Độ Tin Cậy

**Khả Dụng**

Hệ thống phải có tính khả dụng ≥ 99%, có nghĩa là:
- Tối đa 7.2 giờ downtime mỗi tháng (744 giờ)
- Tối đa 43.8 giờ downtime mỗi năm (8760 giờ)

Để đạt được mục tiêu này, hệ thống phải:
- Có khả năng xử lý lỗi gracefully
- Có cơ chế recovery tự động
- Có backup dữ liệu định kỳ

**Độ Tin Cậy**

Hệ thống phải cung cấp các kết quả tin cậy:
- Độ chính xác của câu trả lời ≥ 90%: Trong 90% trường hợp, câu trả lời phải chính xác
- Tỷ lệ thành công truy vấn ≥ 95%: Trong 95% trường hợp, hệ thống phải có thể trả lời câu hỏi mà không gặp lỗi

**Khôi Phục Sau Lỗi**

Khi xảy ra lỗi (ví dụ Neo4j bị down), hệ thống phải:
- Phát hiện lỗi trong vòng 5 giây
- Chuyển sang chế độ degraded (cung cấp dữ liệu cached nếu có thể)
- Thông báo cho người dùng rằng một số tính năng tạm thời không khả dụng
- Tự động khôi phục khi dịch vụ trở lại hoạt động

### 3.2.3 Yêu Cầu Bảo Mật

**Mã Hóa**

- Mật khẩu phải được mã hóa bằng bcrypt hoặc Argon2 trước khi lưu trữ
- Dữ liệu truyền tải phải được mã hóa bằng TLS/HTTPS
- Thông tin nhạy cảm phải được mã hóa tại chỗ nếu cần lưu trữ dài hạn

**Kiểm Soát Truy Cập**

- Mỗi người dùng chỉ có quyền truy cập dữ liệu của chính họ
- Không được lộ lịch sử trò chuyện của người dùng khác
- Admin phải có quyền cao hơn để xem logs hệ thống

**Kiểm Toán**

- Tất cả các hoạt động đăng nhập phải được ghi lại
- Tất cả các thay đổi dữ liệu phải có timestamp và user ID
- Tất cả các lỗi phải được ghi lại cho mục đích gỡ lỗi

### 3.2.4 Yêu Cầu Khả Năng Mở Rộng

**Khả Năng Mở Rộng Ngang (Horizontal Scalability)**

Hệ thống phải có thể mở rộng bằng cách thêm các máy chủ mới:
- FastAPI backend có thể chạy trên nhiều instance với load balancer
- Neo4j, Elasticsearch, PostgreSQL có thể chạy trên multiple nodes
- Redis có thể sử dụng cluster mode

**Khả Năng Mở Rộng Dọc (Vertical Scalability)**

Hệ thống phải có thể tận dụng tài nguyên tăng:
- Sử dụng async/await để xử lý nhiều yêu cầu đồng thời
- Tối ưu hóa truy vấn cơ sở dữ liệu
- Sử dụng caching để giảm số lượng truy vấn cơ sở dữ liệu

### 3.2.5 Yêu Cầu Bảo Trì

**Khả Năng Bảo Trì**

- Mã phải tuân theo các chuẩn code style
- Phải có tài liệu chi tiết cho mỗi function/module
- Phải có unit tests cho các logic phức tạp

**Khả Năng Gỡ Lỗi**

- Tất cả các logs phải được ghi trong định dạng cấu trúc (structured logging)
- Phải có distributed tracing để theo dõi yêu cầu qua các thành phần khác nhau
- Phải có các bảng điều khiển giám sát hiển thị các số liệu chính

## 3.3 Design Patterns

### 3.3.1 Agent Pattern

[IMAGE/DIAGRAM: Agent Pattern Architecture - Placeholder for agent loop diagram showing: User Input → Agent → Tool Selection → Tool Execution → Result Processing → Agent Decision Loop]

**Mô Tả**

Agent pattern là một mô hình lập trình trong đó một tác nhân có thể tự động chọn các hành động tiếp theo dựa trên trạng thái hiện tại. Trong dự án này, tác nhân LangChain hoạt động như sau:

1. Nhận câu hỏi từ người dùng
2. Sử dụng mô hình ngôn ngữ để hiểu ý định và lựa chọn công cụ
3. Gọi công cụ được lựa chọn
4. Nhận kết quả từ công cụ
5. Quyết định xem có đủ thông tin để trả lời hay cần gọi công cụ khác
6. Lặp lại từ bước 2 nếu cần, hoặc tạo câu trả lời nếu có đủ thông tin

**Lợi Ích**

- Tính linh hoạt: Tác nhân có thể xử lý các loại câu hỏi khác nhau mà không cần hardcode logic cho mỗi loại
- Tính mở rộng: Dễ dàng thêm công cụ mới mà không cần thay đổi tác nhân
- Tính trí tuệ: Tác nhân có thể suy luận qua nhiều bước và kết hợp kết quả từ nhiều công cụ

### 3.3.2 RAG (Retrieval-Augmented Generation) Pattern

[IMAGE/DIAGRAM: RAG Pattern - Placeholder for diagram showing: User Query → Retrieval → Retrieved Documents → LLM with Context → Generated Response]

**Mô Tả**

RAG pattern kết hợp việc truy xuất tài liệu liên quan từ cơ sở dữ liệu với việc tạo phản hồi bằng mô hình ngôn ngữ. Quá trình gồm ba bước:

1. **Truy xuất**: Tìm kiếm các tài liệu liên quan từ Elasticsearch dựa trên câu hỏi của người dùng
2. **Tăng cường**: Cung cấp các tài liệu truy xuất được làm ngữ cảnh cho mô hình ngôn ngữ
3. **Tạo phản hồi**: Mô hình tạo ra phản hồi dựa trên tài liệu và câu hỏi

**Lợi Ích**

- Độ chính xác: Câu trả lời được dựa trên dữ liệu thực tế thay vì kiến thức được đào tạo trước
- Cập nhật: Khi dữ liệu cơ sở dữ liệu thay đổi, câu trả lời cũng thay đổi tự động
- Traceability: Có thể biết chính xác tài liệu nào đã được sử dụng để tạo câu trả lời

### 3.3.3 Layered Architecture Pattern

**Mô Tả**

Layered architecture tách biệt hệ thống thành các tầng, mỗi tầng có trách nhiệm riêng. Dự án sử dụng ba tầng:

1. **Tầng Giao Diện** (Presentation Layer): Streamlit - chịu trách nhiệm tương tác với người dùng
2. **Tầng Ứng Dụng** (Application Layer): FastAPI + LangChain - xử lý logic ứng dụng
3. **Tầng Dữ Liệu** (Data Layer): Neo4j, Elasticsearch, PostgreSQL, Redis - lưu trữ và truy xuất dữ liệu

**Lợi Ích**

- Tính độc lập: Mỗi tầng có thể phát triển độc lập
- Tính bảo trì: Dễ dàng tìm và sửa lỗi trong một tầng
- Tính kiểm thử: Có thể kiểm thử từng tầng riêng biệt

### 3.3.4 Command Pattern (Tool Abstraction)

**Mô Tả**

Command pattern được sử dụng để trừu tượng hóa các công cụ. Mỗi công cụ được triển khai như một command object có thể được gọi bởi tác nhân:

```python
class CypherQueryTool(Tool):
    def execute(self, query: str) -> str:
        # Execute Cypher query on Neo4j
        pass

class ElasticsearchTool(Tool):
    def execute(self, query: str) -> str:
        # Execute semantic search on Elasticsearch
        pass
```

**Lợi Ích**

- Tính nhất quán: Tất cả công cụ có cùng interface
- Tính mở rộng: Dễ dàng thêm công cụ mới
- Tính kiểm thử: Có thể mock các công cụ cho mục đích kiểm thử

### 3.3.5 Observer Pattern (Event Logging)

**Mô Tả**

Observer pattern được sử dụng cho logging và monitoring. Mỗi khi một sự kiện xảy ra (ví dụ, một yêu cầu hoàn thành), tất cả các observer được thông báo. Trong dự án, observer bao gồm:

- Logger: Ghi sự kiện vào file log
- Metrics Collector: Cập nhật các số liệu
- Tracer: Ghi lại thông tin tracing

**Lợi Ích**

- Tính độc lập: Các observer hoạt động độc lập với nhau
- Tính mở rộng: Dễ dàng thêm observer mới (ví dụ, gửi alert email)
- Tính dynamic: Observer có thể được thêm/loại bỏ lúc runtime

## 3.4 Thiết Kế Cơ Sở Dữ Liệu

### 3.4.1 Neo4j Schema

[IMAGE/DIAGRAM: Neo4j Data Model - Placeholder for diagram showing nodes (Hospital, Doctor, Patient, Insurance, Visit) and their relationships]

**Các Nút (Nodes)**

```
Hospital:
  - id: UUID
  - name: String
  - city: String
  - state: String
  - country: String
  - beds: Integer
  - avg_wait_time: Float (minutes)
  - created_at: DateTime
  - updated_at: DateTime

Doctor:
  - id: UUID
  - name: String
  - specialty: String (Cardiology, Neurology, etc.)
  - years_experience: Integer
  - license_number: String
  - hospital_id: UUID (denormalized for convenience)
  - created_at: DateTime

Patient:
  - id: UUID
  - age: Integer
  - gender: String (M/F)
  - diagnosis: String (ICD-10 code)
  - insurance_type: String (Medicaid, Medicare, etc.)
  - state: String
  - created_at: DateTime

Payer:
  - id: UUID
  - name: String (Medicaid, Medicare, Cigna, etc.)
  - plan_type: String (HMO, PPO, etc.)

Visit:
  - id: UUID
  - visit_date: Date
  - visit_type: String (In-person, Telehealth, etc.)
  - duration_minutes: Integer
  - diagnosis: String
  - created_at: DateTime
```

**Các Mối Quan Hệ (Relationships)**

```
(Doctor)-[:WORKS_AT]->(Hospital)
(Doctor)-[:TREATS]->(Patient)
(Patient)-[:HAS_INSURANCE]->(Payer)
(Patient)-[:LIVES_IN]->(State)
(Patient)-[:HAS_VISIT]->(Visit)
(Visit)-[:CONDUCTED_BY]->(Doctor)
(Visit)-[:AT_HOSPITAL]->(Hospital)
```

**Các Chỉ Mục (Indexes)**

- `CREATE INDEX ON :Hospital(name)`
- `CREATE INDEX ON :Hospital(state)`
- `CREATE INDEX ON :Doctor(specialty)`
- `CREATE INDEX ON :Patient(age)`
- `CREATE INDEX ON :Patient(insurance_type)`

### 3.4.2 PostgreSQL Schema

[IMAGE/DIAGRAM: PostgreSQL Database Schema - Placeholder for ER diagram showing users, conversations, messages tables and relationships]

**Bảng Users**

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  role VARCHAR(50) DEFAULT 'user', -- user, admin, analyst
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP
);
```

**Bảng Conversations**

```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  title VARCHAR(255),
  status VARCHAR(50) DEFAULT 'active', -- active, archived, deleted
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user_id (user_id),
  INDEX idx_created_at (created_at)
);
```

**Bảng Messages**

```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY,
  conversation_id UUID NOT NULL REFERENCES conversations(id),
  role VARCHAR(50) NOT NULL, -- user, assistant, system
  content TEXT NOT NULL,
  metadata JSON, -- Store execution details, tool calls, etc.
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_conversation_id (conversation_id),
  INDEX idx_created_at (created_at)
);
```

**Bảng Sessions**

```sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  access_token VARCHAR(500) NOT NULL UNIQUE,
  refresh_token VARCHAR(500),
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  is_valid BOOLEAN DEFAULT TRUE,
  INDEX idx_user_id (user_id),
  INDEX idx_access_token (access_token)
);
```

### 3.4.3 Elasticsearch Indices

**Index: patient_reviews**

```json
{
  "mappings": {
    "properties": {
      "hospital_id": { "type": "keyword" },
      "patient_id": { "type": "keyword" },
      "rating": { "type": "integer" },
      "text": { "type": "text", "analyzer": "standard" },
      "embedding": { "type": "dense_vector", "dims": 1536 },
      "sentiment_score": { "type": "float" },
      "created_at": { "type": "date" }
    }
  }
}
```

**Index: diagnostic_references**

```json
{
  "mappings": {
    "properties": {
      "code": { "type": "keyword" },
      "name": { "type": "text" },
      "description": { "type": "text" },
      "criteria": { "type": "text" },
      "embedding": { "type": "dense_vector", "dims": 1536 },
      "category": { "type": "keyword" }
    }
  }
}
```

### 3.4.4 Redis Keys Structure

```
# User sessions
session:{user_id}:{session_id} → JSON with token, expiry, etc.

# Conversation state (cache)
conversation:{conversation_id}:context → Last 10 messages for context

# Rate limiting
rate_limit:{user_id}:{hour} → Counter of requests in this hour

# Query cache
query_cache:{query_hash} → Cached result (expires in 1 hour)

# Online users
online_users:{timestamp} → Set of currently active user IDs
```

## 3.5 Kết Luận Chương 3

Chương này đã chi tiết hóa các yêu cầu chức năng và phi chức năng, cũng như các design patterns được sử dụng. Các yêu cầu chức năng tập trung vào khả năng xử lý các loại truy vấn khác nhau, quản lý trò chuyện, và tạo phản hồi dễ hiểu. Các yêu cầu phi chức năng tập trung vào hiệu suất, khả dụng, bảo mật, và khả năng mở rộng.

Các design patterns được lựa chọn để đạt được các yêu cầu này: Agent pattern cho tính linh hoạt, RAG pattern cho độ chính xác, Layered architecture cho tính bảo trì, Command pattern cho tính mở rộng, và Observer pattern cho tính độc lập. Thiết kế cơ sở dữ liệu sử dụng các công cụ phù hợp cho mỗi loại dữ liệu: Neo4j cho dữ liệu đồ thị, PostgreSQL cho dữ liệu cấu trúc, Elasticsearch cho dữ liệu không cấu trúc, và Redis cho caching.

Chương tiếp theo sẽ chi tiết hóa cách các design này được triển khai trong mã nguồn.
