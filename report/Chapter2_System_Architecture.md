# Chương 2: Tổng Quan Kiến Trúc Hệ Thống

## 2.1 Tổng Quan Kiến Trúc

### 2.1.1 Kiến Trúc Ba Tầng

Hệ thống được thiết kế theo mô hình ba tầng (three-tier architecture), tách rõ ràng giữa giao diện người dùng, logic ứng dụng, và lớp dữ liệu.

**Tầng Giao Diện (Presentation Layer)**

Tầng giao diện được xây dựng bằng Streamlit, một framework Python cho phép tạo giao diện web tương tác mà không cần kiến thức về HTML, CSS, hoặc JavaScript. Streamlit cung cấp các thành phần giao diện như ô nhập văn bản, nút bấm, danh sách thả xuống, và biểu đồ. Người dùng tương tác với hệ thống qua giao diện web này, nhập câu hỏi và nhận kết quả từ backend.

**Tầng Ứng Dụng (Application Layer)**

Tầng ứng dụng được xây dựng bằng FastAPI, một framework web hiện đại cho Python với hiệu suất cao. FastAPI xử lý các yêu cầu từ giao diện người dùng, thực hiện logic ứng dụng, và gọi các dịch vụ khác. Tầng này chứa tác nhân LangChain có khả năng suy luận, quản lý lịch sử trò chuyện, và điều phối các công cụ khác nhau.

**Tầng Dữ Liệu (Data Layer)**

Tầng dữ liệu bao gồm nhiều cơ sở dữ liệu chuyên dụng:
- Neo4j: lưu trữ dữ liệu đồ thị của bệnh viện, bác sĩ, bệnh nhân, và các mối quan hệ giữa chúng
- PostgreSQL: lưu trữ dữ liệu cấu trúc như lịch sử trò chuyện và thông tin người dùng
- Elasticsearch: lưu trữ các tài liệu không có cấu trúc và hỗ trợ tìm kiếm vector cho phân tích ngữ nghĩa
- Redis: dùng làm cache nhanh và quản lý phiên người dùng

### 2.1.2 Kiến Trúc Microservices

Mặc dù hệ thống chính được chứa trong một ứng dụng FastAPI duy nhất, nó được thiết kế theo nguyên tắc microservices với các thành phần có thể chạy độc lập:

**Container hóa với Docker**

Mỗi thành phần chính (FastAPI backend, Streamlit frontend, Neo4j, PostgreSQL, Elasticsearch, Redis) được đóng gói thành một Docker container riêng biệt. Các container này chứa mã ứng dụng, thư viện phụ thuộc, và môi trường chạy, đảm bảo rằng ứng dụng sẽ chạy giống nhau trên máy phát triển, máy kiểm tra, và máy sản xuất.

**Điều Phối bằng Docker Compose**

Docker Compose được sử dụng để định nghĩa và điều phối tất cả các container. Tệp docker-compose.yaml định nghĩa từng dịch vụ, hình ảnh Docker của nó, các biến môi trường, cổng mạng, và các phụ thuộc giữa chúng. Một lệnh duy nhất `docker-compose up` khởi động toàn bộ hệ thống.

**Mạng Nội Bộ**

Các container giao tiếp với nhau qua một mạng Docker nội bộ. Mỗi container có một tên dịch vụ (service name) có thể được sử dụng như tên máy chủ (hostname). Ví dụ, FastAPI backend kết nối tới Neo4j bằng địa chỉ `neo4j:7687` thay vì `localhost:7687`.

## 2.2 Các Thành Phần Chính

### 2.2.1 Frontend - Streamlit

**Chức Năng**

Streamlit được sử dụng để tạo giao diện web tương tác cho người dùng. Giao diện này cho phép người dùng nhập câu hỏi bằng ngôn ngữ tự nhiên và xem kết quả từ backend.

**Cấu Trúc Ứng Dụng**

Ứng dụng Streamlit được tổ chức thành các trang (pages) khác nhau:
- Trang chủ (Home): Giao diện chính nơi người dùng nhập câu hỏi
- Trang Lịch sử (History): Hiển thị các câu hỏi và câu trả lời trước đó
- Trang Cài đặt (Settings): Cho phép người dùng cấu hình các tùy chọn

**Tương Tác với Backend**

Khi người dùng nhập câu hỏi và nhấn nút gửi, Streamlit gửi một yêu cầu HTTP POST tới endpoint `/chat` của FastAPI backend. Khi nhận được phản hồi, Streamlit hiển thị kết quả trên giao diện.

### 2.2.2 Backend - FastAPI

**Chức Năng**

FastAPI là server ứng dụng web chịu trách nhiệm xử lý logic ứng dụng chính. Nó tiếp nhận yêu cầu từ Streamlit frontend, xử lý chúng, và trả về kết quả.

**Các Endpoint Chính**

- `POST /chat`: Tiếp nhận câu hỏi của người dùng, gọi tác nhân LangChain, và trả về câu trả lời
- `GET /history`: Lấy lịch sử trò chuyện của người dùng
- `POST /login`: Xác thực người dùng
- `GET /health`: Kiểm tra trạng thái của hệ thống (sử dụng bởi các công cụ giám sát)

**Tác Nhân LangChain**

Tác nhân LangChain là trái tim của backend. Nó nhận một câu hỏi dưới dạng văn bản và quyết định hành động tiếp theo:
1. Phân tích câu hỏi để hiểu ý định (structured query, semantic search, knowledge lookup)
2. Lựa chọn công cụ hoặc công cụ cần gọi
3. Gọi công cụ đó và nhận kết quả
4. Lặp lại cho đến khi có đủ thông tin để trả lời
5. Tạo câu trả lời cuối cùng và giải thích

**Các Công Cụ của Tác Nhân**

Tác nhân có quyền truy cập vào các công cụ sau:
- **Công cụ Cypher**: Tạo và thực thi các truy vấn Cypher trên Neo4j để lấy dữ liệu cấu trúc
- **Công cụ Tìm kiếm**: Tìm kiếm các tài liệu trong Elasticsearch để phân tích ngữ nghĩa
- **Công cụ Cơ sở Dữ liệu Chẩn đoán**: Tra cứu thông tin tiêu chuẩn chẩn đoán tâm thần
- **Công cụ Lịch sử**: Lấy lịch sử trò chuyện trước đó từ PostgreSQL để duy trì ngữ cảnh

### 2.2.3 Cơ Sở Dữ Liệu Neo4j

**Chức Năng**

Neo4j là cơ sở dữ liệu đồ thị lưu trữ dữ liệu hoạt động của bệnh viện dưới dạng nút (nodes) và mối quan hệ (relationships).

**Mô Hình Dữ Liệu**

Dữ liệu được tổ chức thành các nút chính:
- Nút **Bệnh Viện**: Đại diện cho các bệnh viện với các thuộc tính như tên, địa chỉ, thành phố
- Nút **Bác Sĩ**: Đại diện cho các bác sĩ với thông tin như tên, chuyên khoa, năm kinh nghiệm
- Nút **Bệnh Nhân**: Đại diện cho các bệnh nhân với thông tin như tuổi, giới tính, bảo hiểm
- Nút **Công Ty Bảo Hiểm**: Đại diện cho các công ty bảo hiểm với tên và loại kế hoạch
- Nút **Khám Bệnh**: Đại diện cho các cuộc khám bệnh với ngày, thời gian, và chẩn đoán

Các mối quan hệ bao gồm:
- `WORKS_AT`: Liên kết bác sĩ với bệnh viện họ làm việc
- `TREATS`: Liên kết bác sĩ với bệnh nhân họ điều trị
- `HAS_INSURANCE`: Liên kết bệnh nhân với công ty bảo hiểm
- `VISITS`: Liên kết bệnh nhân với các cuộc khám bệnh
- `CONDUCTED_BY`: Liên kết cuộc khám bệnh với bác sĩ

**Truy Vấn Cypher**

Neo4j sử dụng ngôn ngữ truy vấn Cypher, tương tự như SQL nhưng được tối ưu hóa cho đồ thị. Ví dụ, truy vấn để lấy tất cả bác sĩ làm việc tại bệnh viện "Memorial Hospital" sẽ là:

```
MATCH (d:Doctor)-[:WORKS_AT]->(h:Hospital {name: "Memorial Hospital"})
RETURN d.name, d.specialty
```

### 2.2.4 Cơ Sở Dữ Liệu Elasticsearch

**Chức Năng**

Elasticsearch là một search engine dành cho dữ liệu không có cấu trúc. Nó lưu trữ các tài liệu như bình luận bệnh nhân, bài viết tham khảo, và lịch sử trò chuyện, và hỗ trợ tìm kiếm nhanh và phân tích ngữ nghĩa.

**Chỉ Mục (Indices)**

Dữ liệu được tổ chức thành các chỉ mục:
- Chỉ mục `patient_reviews`: Chứa tất cả bình luận và đánh giá của bệnh nhân
- Chỉ mục `diagnostic_references`: Chứa thông tin tiêu chuẩn chẩn đoán tâm thần
- Chỉ mục `conversation_history`: Chứa lịch sử trò chuyện

**Tìm Kiếm Hybrid**

Elasticsearch hỗ trợ cả tìm kiếm full-text (tìm kiếm từ khóa) và tìm kiếm vector (tìm kiếm ngữ nghĩa). Khi một người dùng hỏi "Bệnh nhân nói gì về chất lượng nhân viên?", hệ thống sẽ:
1. Chuyển đổi câu hỏi thành một vector nhúng (embedding)
2. Tìm kiếm trong Elasticsearch các vector tương tự
3. Lấy kết quả và tóm tắt cho người dùng

### 2.2.5 Cơ Sở Dữ Liệu PostgreSQL

**Chức Năng**

PostgreSQL là cơ sở dữ liệu quan hệ lưu trữ dữ liệu có cấu trúc như thông tin người dùng và lịch sử trò chuyện.

**Các Bảng Chính**

- Bảng `users`: Lưu trữ thông tin người dùng bao gồm username, hashed password, email, và thời gian tạo tài khoản
- Bảng `conversations`: Lưu trữ các cuộc trò chuyện với id, user_id, timestamp tạo, và status
- Bảng `messages`: Lưu trữ từng tin nhắn với content, role (user hay assistant), timestamp, và id của cuộc trò chuyện chứa nó

**Mục Đích**

PostgreSQL được sử dụng cho dữ liệu có cấu trúc, có ACID compliance (Atomicity, Consistency, Isolation, Durability), đảm bảo tính toàn vẹn dữ liệu. Nó phù hợp cho việc lưu trữ lịch sử trò chuyện vì cần đảm bảo rằng không có tin nhắn nào bị mất.

### 2.2.6 Cache - Redis

**Chức Năng**

Redis là một cơ sở dữ liệu key-value trong bộ nhớ được sử dụng cho caching và quản lý phiên. Nó cung cấp hiệu suất rất cao so với các cơ sở dữ liệu truyền thống vì dữ liệu được lưu trữ trong RAM thay vì đĩa cứng.

**Các Trường Hợp Sử Dụng**

- **Caching**: Lưu trữ kết quả truy vấn thường xuyên để tránh phải thực hiện lại cùng một truy vấn
- **Phiên (Sessions)**: Lưu trữ thông tin phiên người dùng như access tokens
- **Queue**: Lưu trữ các yêu cầu chưa xử lý trong hàng đợi để xử lý later
- **Rate Limiting**: Theo dõi số lượng yêu cầu từ mỗi người dùng để ngăn chặn lạm dụng

## 2.3 Luồng Xử Lý Yêu Cầu

### 2.3.1 Từng Bước Xử Lý

**Bước 1: Gửi Yêu Cầu**

Người dùng nhập một câu hỏi vào Streamlit frontend, ví dụ "Bệnh viện nào ở Texas có đánh giá cao nhất?". Streamlit gửi một yêu cầu HTTP POST tới endpoint `/chat` của FastAPI backend với payload chứa câu hỏi và id của người dùng.

**Bước 2: Xác Thực**

FastAPI backend xác thực yêu cầu, kiểm tra xem người dùng có quyền truy cập không, và kiểm tra rate limiting (số lượng yêu cầu được phép trong một khoảng thời gian).

**Bước 3: Gọi Tác Nhân**

FastAPI gọi tác nhân LangChain với câu hỏi. Tác nhân sử dụng mô hình ngôn ngữ OpenAI để:
1. Phân tích câu hỏi: Hiểu rằng đây là truy vấn kết hợp (cần tìm bệnh viện ở Texas + có đánh giá cao)
2. Trích xuất thực thể: State = Texas, target = highest ratings
3. Quyết định công cụ: Cần truy vấn Neo4j cho bệnh viện ở Texas, rồi tìm kiếm Elasticsearch cho đánh giá

**Bước 4: Gọi Công Cụ**

Tác nhân thực hiện các công cụ:
1. Gọi công cụ Cypher: Tạo truy vấn `MATCH (h:Hospital {state: "TX"}) RETURN h.name, h.city`
2. Neo4j trả về danh sách các bệnh viện tại Texas
3. Gọi công cụ Tìm kiếm: Tìm kiếm các bình luận về mỗi bệnh viện trong Elasticsearch
4. Elasticsearch trả về các bình luận kèm scores cảm xúc

**Bước 5: Tổng Hợp Kết Quả**

Tác nhân tổng hợp kết quả: nhận danh sách bệnh viện từ Neo4j, phân tích cảm xúc từ Elasticsearch, sắp xếp theo rating, và tạo một câu trả lời dễ hiểu cho người dùng.

**Bước 6: Trả Về Kết Quả**

FastAPI trả về câu trả lời cho Streamlit, đồng thời lưu trữ câu hỏi và câu trả lời trong PostgreSQL. Streamlit hiển thị kết quả trên giao diện người dùng.

### 2.3.2 Lịch Sử Trò Chuyện

Khi một người dùng đặt câu hỏi tiếp theo, tác nhân có quyền truy cập vào lịch sử trò chuyện trước đó. Ví dụ, nếu người dùng trước đó hỏi "Bệnh viện nào ở Texas?" và hiện tại hỏi "Cái nào có thời gian chờ lâu nhất?", tác nhân sẽ hiểu rằng câu hỏi thứ hai được tham chiếu tới kết quả của câu hỏi trước.

Quá trình này được thực hiện bằng cách:
1. FastAPI lấy lịch sử trò chuyện từ PostgreSQL
2. Cung cấp lịch sử cho tác nhân LangChain làm ngữ cảnh
3. Tác nhân sử dụng ngữ cảnh để hiểu câu hỏi hiện tại

## 2.4 Ngăn Xếp Giám Sát và Quan Sát

### 2.4.1 Phoenix Tracing

**Chức Năng**

Phoenix Tracing là một hệ thống theo dõi phân tán (distributed tracing system) cho phép theo dõi một yêu cầu từ khi vào hệ thống cho đến khi ra.

**Cách Hoạt Động**

Mỗi yêu cầu được gán một trace ID duy nhất. Khi yêu cầu đi qua các thành phần khác nhau của hệ thống (FastAPI, LangChain, Neo4j, Elasticsearch), mỗi thành phần thêm thông tin về những gì nó đã làm vào trace này. Ví dụ:
- FastAPI ghi lại rằng nó nhận được yêu cầu tại thời điểm T1
- LangChain ghi lại rằng nó gọi mô hình OpenAI từ T2 đến T3
- Công cụ Cypher ghi lại rằng nó thực thi truy vấn từ T4 đến T5
- FastAPI ghi lại rằng nó gửi phản hồi tại thời điểm T6

Thông tin này được lưu trữ và có thể được xem trong giao diện Phoenix để theo dõi hiệu suất và gỡ lỗi vấn đề.

### 2.4.2 Prometheus Metrics

**Chức Năng**

Prometheus là một hệ thống thu thập số liệu (metrics collection system) tập trung vào giám sát các dịch vụ.

**Các Số Liệu Được Thu Thập**

- `http_requests_total`: Tổng số yêu cầu HTTP nhận được
- `http_request_duration_seconds`: Thời gian xử lý các yêu cầu HTTP
- `database_query_duration_seconds`: Thời gian thực thi truy vấn cơ sở dữ liệu
- `llm_api_calls_total`: Tổng số lần gọi API mô hình ngôn ngữ
- `cache_hits_total` và `cache_misses_total`: Số lần cache hit/miss

**Cách Lưu Trữ**

Prometheus lưu trữ các số liệu này theo chuỗi thời gian (time series), cho phép phân tích xu hướng và lịch sử.

### 2.4.3 Grafana Dashboards

**Chức Năng**

Grafana là một công cụ trực quan hóa số liệu. Nó lấy dữ liệu từ Prometheus và hiển thị trên các bảng điều khiển (dashboards) với biểu đồ, đồ thị, và chỉ báo.

**Các Bảng Điều Khiển**

- Bảng điều khiển **Hiệu Suất**: Hiển thị thời gian phản hồi, throughput, và tỷ lệ lỗi
- Bảng điều khiển **Cơ Sở Dữ Liệu**: Hiển thị số lượng kết nối, thời gian truy vấn, và kích thước dữ liệu
- Bảng điều khiển **LLM API**: Hiển thị chi phí, latency, và số lần gọi

### 2.4.4 ELK Stack (Elasticsearch, Logstash, Kibana)

**Chức Năng**

ELK Stack là một giải pháp ghi nhật ký tập trung (centralized logging solution). Các thành phần ghi lại các sự kiện (logs) ở các mức khác nhau (DEBUG, INFO, WARNING, ERROR), và những logs này được gửi tới ELK.

**Cách Hoạt Động**

- **Elasticsearch**: Lưu trữ các logs
- **Logstash**: Xử lý và chuyển đổi các logs từ các nguồn khác nhau
- **Kibana**: Giao diện để xem, tìm kiếm, và phân tích logs

**Ví Dụ**

Khi FastAPI xử lý yêu cầu, nó ghi lại các logs như:
```
[2024-05-10 10:23:45.123] INFO FastAPI Received request /chat from user 123
[2024-05-10 10:23:45.456] DEBUG LangChain Calling OpenAI API
[2024-05-10 10:23:46.789] INFO Neo4j Executed query successfully
[2024-05-10 10:23:47.000] INFO FastAPI Sent response to user 123
```

Các logs này được lưu trữ trong Elasticsearch và có thể được tìm kiếm trong Kibana.

## 2.5 Công Nghệ và Lựa Chọn

### 2.5.1 Tại Sao LangChain?

LangChain là một framework cho phép xây dựng các ứng dụng được điều khiển bởi mô hình ngôn ngữ lớn. Nó cung cấp các tiện ích cho việc:
- Quản lý các gợi ý (prompts) tới mô hình
- Gọi các mô hình khác nhau (OpenAI, Anthropic, Local models)
- Xây dựng các tác nhân (agents) có thể suy luận
- Tích hợp các cơ sở dữ liệu khác nhau

### 2.5.2 Tại Sao Neo4j?

Neo4j là cơ sở dữ liệu đồ thị tốt nhất cho dữ liệu có cấu trúc và các mối quan hệ phức tạp. Nó vượt trội hơn SQL trong trường hợp này vì:
- Dữ liệu bệnh viện có nhiều mối quan hệ (bác sĩ làm việc tại bệnh viện, bác sĩ điều trị bệnh nhân, bệnh nhân có bảo hiểm, v.v.)
- Truy vấn trên đồ thị nhanh hơn JOIN trong SQL
- Cypher dễ đọc và dễ tạo động từ ngôn ngữ tự nhiên

### 2.5.3 Tại Sao Elasticsearch?

Elasticsearch được chọn cho tìm kiếm ngữ nghĩa vì:
- Hỗ trợ cả tìm kiếm full-text và vector search
- Hiệu suất cao thậm chí với dữ liệu lớn
- Hỗ trợ các bộ lọc (filters) và tập hợp (aggregations) nâng cao

### 2.5.4 Tại Sao PostgreSQL?

PostgreSQL được sử dụng cho dữ liệu cấu trúc vì:
- ACID compliance đảm bảo tính toàn vẹn dữ liệu
- Hỗ trợ các constraint và trigger phức tạp
- Có thể xử lý các truy vấn lớn với hiệu suất tốt

### 2.5.5 Tại Sao FastAPI?

FastAPI được lựa chọn cho backend vì:
- Hiệu suất cao (async/await support)
- Tự động sinh các tài liệu API (Swagger UI)
- Type hints giúp phát hiện lỗi sớm
- Dễ dàng tích hợp các thư viện Python khác

### 2.5.6 Tại Sao Streamlit?

Streamlit được sử dụng cho frontend vì:
- Không cần HTML/CSS/JavaScript
- Phát triển nhanh
- Tích hợp tốt với Python
- Thích hợp cho các ứng dụng data/AI

## 2.6 Kết Luận Chương 2

Kiến trúc hệ thống được thiết kế để cân bằng giữa sự đơn giản, hiệu suất, và khả năng mở rộng. Sử dụng ba tầng rõ ràng cho phép phát triển và thay đổi độc lập từng phần. Việc sử dụng các công cụ chuyên dụng (Neo4j cho đồ thị, Elasticsearch cho tìm kiếm, PostgreSQL cho dữ liệu cấu trúc) đảm bảo mỗi thành phần làm tốt nhất những gì nó được thiết kế cho. Ngăn xếp giám sát toàn diện cho phép nhận diện vấn đề nhanh chóng và gỡ lỗi hiệu quả.

Chương tiếp theo sẽ chi tiết hóa các yêu cầu cụ thể và cách hệ thống được thiết kế để đáp ứng những yêu cầu đó.
