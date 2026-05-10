# Chương 4: Chi Tiết Triển Khai Công Nghệ

## 4.1 Triển Khai Agent Logic

### 4.1.1 Kiến Trúc Tác Nhân

Tác nhân LangChain là một vòng lặp (loop) được lặp lại cho đến khi đạt được một trạng thái kết thúc. Vòng lặp này bao gồm các bước:

1. Nhận input từ người dùng và lịch sử trò chuyện
2. Gọi mô hình ngôn ngữ để quyết định hành động tiếp theo
3. Phân tích kết quả từ mô hình để trích xuất hành động
4. Thực thi hành động (gọi công cụ hoặc trả lời)
5. Lặp lại từ bước 2 nếu cần, hoặc dừng lại nếu có đáp án

**Khởi Tạo Tác Nhân**

Để tạo tác nhân, chúng ta cần cấu hình các thành phần sau:

Mô hình ngôn ngữ được sử dụng để suy luận. Trong dự án này, sử dụng OpenAI GPT-4 hoặc GPT-3.5-turbo. Mô hình được cấu hình với nhiệt độ (temperature) thấp (khoảng 0,1-0,3) để đảm bảo tính nhất quán của câu trả lời.

Danh sách công cụ mà tác nhân có quyền truy cập. Mỗi công cụ cần có tên, mô tả, và các tham số đầu vào. Ví dụ, công cụ Cypher Query cần tham số là chuỗi Cypher.

Prompt template giúp hướng dẫn mô hình về cách tư duy. Prompt template này bao gồm ý lệnh (instruction), ví dụ về cách sử dụng công cụ, định dạng của output, v.v.

Memory/Context manager để lưu trữ và quản lý lịch sử trò chuyện. Điều này cho phép tác nhân tham chiếu các câu hỏi/câu trả lời trước đó.

**Vòng Lặp Tác Nhân**

Khi người dùng gửi một câu hỏi, vòng lặp hoạt động như sau:

Bước 1 - Input Processing: Lấy câu hỏi từ người dùng, kèm theo lịch sử trò chuyện từ memory. Tạo prompt bằng cách kết hợp system prompt, ví dụ, lịch sử, và câu hỏi hiện tại.

Bước 2 - Model Invocation: Gửi prompt tới mô hình OpenAI. Mô hình trả về một kết quả có thể là: (a) gọi công cụ với các tham số, hoặc (b) câu trả lời cuối cùng.

Bước 3 - Output Parsing: Phân tích kết quả từ mô hình. Nếu là gọi công cụ, trích xuất tên công cụ và các tham số. Nếu là câu trả lời, trích xuất câu trả lời.

Bước 4 - Tool Execution (nếu cần): Nếu mô hình quyết định gọi công cụ, thực thi công cụ với các tham số được trích xuất. Công cụ trả về một kết quả.

Bước 5 - Loop Decision: Kiểm tra xem có nên tiếp tục vòng lặp hay không. Nếu mô hình trả lời, dừng lại. Nếu mô hình gọi công cụ, thêm kết quả của công cụ vào lịch sử và quay lại bước 2.

### 4.1.2 Cài Đặt Mô Hình

[CODE BLOCK: Agent initialization - Placeholder for Python code showing:
```python
from langchain.agents import Agent, Tool
from langchain.llms import OpenAI

# Initialize LLM
llm = OpenAI(
    model_name="gpt-4",
    temperature=0.1,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Define tools
tools = [
    CypherTool(),
    ElasticsearchTool(),
    DiagnosticTool(),
    HistoryTool()
]

# Create agent
agent = Agent(
    llm=llm,
    tools=tools,
    memory=ConversationBufferMemory(),
    verbose=True
)
```
]

**Lựa Chọn Mô Hình**

Dự án sử dụng OpenAI GPT-4 vì những lý do sau: GPT-4 có khả năng suy luận tốt hơn GPT-3.5, đặc biệt với các câu hỏi phức tạp. Nó cũng có token limit cao hơn (8K hoặc 32K), cho phép xử lý lịch sử trò chuyện dài. Dự án có thể fallback tới GPT-3.5-turbo nếu chi phí là vấn đề hoặc nếu latency là ưu tiên.

**Cấu Hình Temperature**

Temperature kiểm soát mức độ ngẫu nhiên của kết quả từ mô hình. Với temperature = 0, mô hình luôn chọn token có xác suất cao nhất, dẫn đến kết quả nhất quán nhưng có thể lặp lại. Với temperature = 1, mô hình có nhiều tự do hơn, dẫn đến kết quả đa dạng hơn nhưng có thể không nhất quán. Dự án sử dụng temperature = 0,1 để cân bằng giữa nhất quán và đa dạng.

### 4.1.3 Prompt Engineering

**System Prompt**

System prompt hướng dẫn mô hình về vai trò và hành vi của nó. Ví dụ:

```
Bạn là một trợ lý thông minh giúp trả lời các câu hỏi về bệnh viện, bác sĩ, bệnh nhân, và thông tin chẩn đoán tâm thần. Bạn có quyền truy cập vào các công cụ sau:

1. Cypher Query Tool: Truy vấn dữ liệu cấu trúc từ Neo4j
2. Elasticsearch Tool: Tìm kiếm các tài liệu không cấu trúc
3. Diagnostic Tool: Tra cứu thông tin tiêu chuẩn chẩn đoán
4. History Tool: Lấy lịch sử trò chuyện

Khi người dùng hỏi, hãy:
1. Phân tích câu hỏi để hiểu ý định
2. Trích xuất các thực thể (tên bệnh viện, loại bảo hiểm, v.v.)
3. Chọn công cụ phù hợp
4. Thực thi công cụ nếu cần
5. Tổng hợp kết quả thành câu trả lời dễ hiểu

Luôn giải thích cách bạn đi đến câu trả lời. Nếu không chắc chắn, hãy nói "Tôi không chắc chắn" thay vì đoán mò.
```

**Few-shot Prompting**

Few-shot prompting cung cấp ví dụ về cách mô hình nên hoạt động. Ví dụ:

```
Ví dụ 1:
User: "Có bao nhiêu bệnh nhân Medicaid tại Texas?"
Assistant: Tôi sẽ truy vấn cơ sở dữ liệu để tìm số lượng bệnh nhân Medicaid tại Texas.
Tool: CypherQuery(query="MATCH (p:Patient)-[:HAS_INSURANCE]->(payer:Payer {type: 'Medicaid'}), (p)-[:LIVES_IN]->(state:State {name: 'TX'}) RETURN COUNT(p)")
Result: 1523
Response: Có 1.523 bệnh nhân bảo hiểm Medicaid tại Texas theo dữ liệu hiện tại.

Ví dụ 2:
User: "Bệnh nhân nói gì về chất lượng nhân viên?"
Assistant: Tôi sẽ tìm kiếm các bình luận của bệnh nhân về nhân viên y tế.
Tool: ElasticsearchSearch(query="patient feedback staff quality")
Result: [bình luận 1, bình luận 2, ...]
Response: Dựa trên các bình luận, bệnh nhân nói rằng nhân viên rất chuyên nghiệp, nhiệt tình, và có kiến thức tốt. Tuy nhiên, một số bệnh nhân lo lắng về thời gian chờ.
```

## 4.2 Triển Khai Các Công Cụ

### 4.2.1 Công Cụ Cypher Query

[CODE BLOCK: CypherTool implementation - Placeholder for Python class showing tool interface, query execution, error handling]

**Chức Năng**

Công cụ Cypher Query cho phép tác nhân thực thi các truy vấn Cypher trên Neo4j để lấy dữ liệu cấu trúc.

**Triển Khai**

Công cụ được triển khai như một class Python kế thừa từ `langchain.tools.BaseTool`. Nó có phương thức `_run()` chứa logic thực thi truy vấn.

Khi tác nhân gọi công cụ, nó cung cấp một chuỗi Cypher. Công cụ kết nối tới Neo4j driver, thực thi truy vấn, và trả về kết quả dưới dạng một danh sách các bản ghi hoặc một số.

**Xác Thực Truy Vấn**

Trước khi thực thi, công cụ kiểm tra xem truy vấn có hợp lệ không. Nó kiểm tra:
- Cú pháp Cypher có đúng không (sử dụng một parser đơn giản hoặc regex)
- Truy vấn có chứa các lệnh nguy hiểm không (ví dụ DELETE, DROP)
- Kết quả có quá lớn không (tối đa 1000 bản ghi)

Nếu truy vấn không hợp lệ, công cụ trả về một lỗi rõ ràng thay vì thực thi truy vấn sai.

**Caching**

Để tối ưu hóa hiệu suất, công cụ lưu trữ kết quả trong Redis với key là hash của truy vấn. Nếu cùng một truy vấn được thực thi lại trong vòng 1 giờ, kết quả cached được trả lại thay vì thực thi lại truy vấn.

### 4.2.2 Công Cụ Elasticsearch Search

**Chức Năng**

Công cụ Elasticsearch cho phép tác nhân tìm kiếm các tài liệu không cấu trúc bằng tìm kiếm ngữ nghĩa.

**Triển Khai**

Khi tác nhân gọi công cụ, nó cung cấp một chuỗi truy vấn tự nhiên. Công cụ:

1. Chuyển đổi chuỗi truy vấn thành một embedding sử dụng mô hình embedding (ví dụ OpenAI Embedding Model hoặc sentence-transformers)
2. Gửi embedding tới Elasticsearch để tìm kiếm vector tương tự
3. Trả về top-k tài liệu phù hợp nhất (mặc định k=5)

**Phân Tích Cảm Xúc**

Đối với các truy vấn liên quan đến feedback bệnh nhân, công cụ cũng thực hiện phân tích cảm xúc. Nó sử dụng một mô hình cảm xúc để tính toán điểm cảm xúc (-1 đến 1) cho mỗi bình luận, sau đó tóm tắt tổng thể cảm xúc.

### 4.2.3 Công Cụ Cơ Sở Dữ Liệu Chẩn Đoán

**Chức Năng**

Công cụ này cho phép tác nhân tra cứu thông tin tiêu chuẩn chẩn đoán tâm thần.

**Triển Khai**

Công cụ nhận một mô tả triệu chứng hoặc mã chẩn đoán, tìm kiếm trong Elasticsearch index `diagnostic_references`, và trả về thông tin tiêu chuẩn về chẩn đoán.

Ví dụ, nếu tác nhân hỏi "Tiêu chuẩn chẩn đoán cho trầm cảm?", công cụ sẽ:
1. Tìm kiếm trong Elasticsearch cho "depression" hoặc mã ICD-10 F32/F33
2. Trả về tiêu chuẩn DSM-5 cho chẩn đoán trầm cảm
3. Bao gồm thông tin về triệu chứng, độ tuổi khởi phát, tỷ lệ phổ biến, v.v.

### 4.2.4 Công Cụ Lịch Sử Trò Chuyện

**Chức Năng**

Công cụ này cho phép tác nhân truy cập lịch sử trò chuyện của người dùng.

**Triển Khai**

Khi tác nhân cần ngữ cảnh từ các câu hỏi trước đó, nó gọi công cụ này. Công cụ:

1. Lấy ID người dùng từ ngữ cảnh hiện tại
2. Truy vấn PostgreSQL để lấy tin nhắn 10-20 gần nhất của cuộc trò chuyện này
3. Định dạng chúng thành một chuỗi có thể đọc được
4. Trả lại cho tác nhân

Công cụ cũng có thể lọc lịch sử để chỉ bao gồm tin nhắn từ người dùng và câu trả lời của trợ lý, bỏ qua các tin nhắn hệ thống.

## 4.3 Triển Khai Quản Lý Trò Chuyện

### 4.3.1 Lưu Trữ Tin Nhắn

**Cấu Trúc Dữ Liệu**

Mỗi tin nhắn được lưu trữ trong PostgreSQL với cấu trúc sau:

```python
class Message(Base):
    __tablename__ = "messages"
    
    id: UUID = Column(UUID, primary_key=True, default=uuid4)
    conversation_id: UUID = Column(UUID, ForeignKey("conversations.id"))
    role: str = Column(String(50))  # "user", "assistant", "system"
    content: str = Column(Text)
    metadata: dict = Column(JSON)  # Store execution details
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow)
    
    # Indexes for fast retrieval
    __table_args__ = (
        Index('ix_conversation_id', 'conversation_id'),
        Index('ix_created_at', 'created_at'),
    )
```

**Metadata**

Trường metadata chứa thông tin bổ sung về tin nhắn, bao gồm:
- Các công cụ được sử dụng (ví dụ `["CypherQuery", "ElasticsearchSearch"]`)
- Thời gian xử lý
- Trace ID cho distributed tracing
- Các lỗi nếu có

### 4.3.2 Quản Lý Ngữ Cảnh

**Buffer Memory**

Tác nhân sử dụng `ConversationBufferMemory` từ LangChain để lưu trữ lịch sử trò chuyện trong bộ nhớ. Memory này chứa tất cả các tin nhắn từ cuộc trò chuyện hiện tại, được định dạng thành một chuỗi có thể đọc được.

**Cửa Sổ Trượt (Sliding Window)**

Để tránh context quá dài (vì mô hình OpenAI có giới hạn token), hệ thống sử dụng một cửa sổ trượt. Nó chỉ giữ các tin nhắn 10-20 gần nhất, sau đó loại bỏ các tin nhắn cũ hơn.

**Tóm Tắt Tự Động**

Để giảm thiểu mất mát thông tin khi loại bỏ tin nhắn cũ, hệ thống có thể tạo một tóm tắt của các tin nhắn bị loại bỏ và bao gồm tóm tắt này trong ngữ cảnh. Ví dụ, thay vì giữ tất cả 20 tin nhắn cuối cùng, hệ thống có thể giữ 10 tin nhắn cuối cùng + 1 tóm tắt của 10 tin nhắn trước đó.

### 4.3.3 Tạo Cuộc Trò Chuyện Mới

Khi người dùng bắt đầu cuộc trò chuyện mới, hệ thống:

1. Tạo một record mới trong bảng `conversations` với user_id và status = "active"
2. Tạo một memory buffer mới (trống) cho cuộc trò chuyện này
3. Trả về conversation_id cho giao diện để sử dụng trong các yêu cầu tiếp theo

### 4.3.4 Tiếp Tục Cuộc Trò Chuyện

Khi người dùng tiếp tục một cuộc trò chuyện hiện có:

1. Trích xuất conversation_id từ yêu cầu
2. Lấy tất cả các tin nhắn của cuộc trò chuyện này từ PostgreSQL
3. Tái tạo memory buffer bằng cách thêm từng tin nhắn một
4. Sử dụng memory này làm ngữ cảnh cho tác nhân

## 4.4 Triển Khai Xử Lý Lỗi

### 4.4.1 Các Loại Lỗi

**Lỗi Mô Hình (Model Errors)**

Khi gọi API OpenAI, các lỗi có thể xảy ra:
- Rate limit: OpenAI giới hạn số lượng yêu cầu mỗi phút
- Token limit: Tổng số token (input + output) vượt quá giới hạn của mô hình
- API error: OpenAI server gặp sự cố

Xử lý: Retry với exponential backoff, fallback tới mô hình thay thế (ví dụ GPT-3.5 nếu GPT-4 fail), hoặc trả về lỗi cho người dùng.

**Lỗi Công Cụ (Tool Errors)**

Khi gọi các công cụ, các lỗi có thể xảy ra:
- Neo4j connection error: Không thể kết nối tới Neo4j
- Cypher syntax error: Truy vấn Cypher không hợp lệ
- Elasticsearch timeout: Tìm kiếm mất quá lâu

Xử lý: Log lỗi, trả về thông báo lỗi rõ ràng cho tác nhân, tác nhân có thể thử công cụ khác hoặc hỏi người dùng làm rõ.

**Lỗi Validation (Validation Errors)**

Khi xác thực input từ người dùng:
- Email không hợp lệ
- Mật khẩu quá yếu
- Token hết hạn

Xử lý: Trả về lỗi chi tiết cho người dùng.

### 4.4.2 Cơ Chế Retry

**Exponential Backoff**

Khi xảy ra lỗi transient (có thể tự phục hồi), hệ thống retry với exponential backoff:

```
Attempt 1: Immediate
Attempt 2: Wait 1 second, then retry
Attempt 3: Wait 2 seconds, then retry
Attempt 4: Wait 4 seconds, then retry
Attempt 5: Wait 8 seconds, then retry
Max attempts: 5
Max wait time: 8 seconds
```

Nếu sau 5 lần retry vẫn fail, trả về lỗi cho người dùng.

**Circuit Breaker**

Để tránh gây thêm tải khi một dịch vụ bị sập, hệ thống sử dụng circuit breaker pattern. Nếu một dịch vụ fail liên tục (ví dụ 5 lần liên tiếp), circuit breaker sẽ "mở" và ngừng gửi yêu cầu tới dịch vụ đó trong một khoảng thời gian (ví dụ 30 giây). Sau đó, nó sẽ "nửa mở" và thử lại.

### 4.4.3 Ghi Nhật Ký Lỗi

Tất cả các lỗi được ghi nhật ký với:
- Timestamp
- Loại lỗi
- Thông báo lỗi
- Stack trace (nếu có)
- Trace ID (để theo dõi yêu cầu qua các thành phần)
- Severity level (ERROR, WARNING, INFO)

Logs được gửi tới ELK Stack để lưu trữ tập trung và phân tích.

### 4.4.4 Thông Báo Lỗi cho Người Dùng

Khi xảy ra lỗi, người dùng được thông báo với một tin nhắn rõ ràng và có thể hành động:

- **Lỗi Transient**: "Tôi đang gặp một lỗi tạm thời. Vui lòng thử lại sau vài giây."
- **Lỗi Permanent**: "Xin lỗi, tôi không thể trả lời câu hỏi này lúc này. Vui lòng thử câu hỏi khác."
- **Lỗi Validation**: "Email bạn không hợp lệ. Vui lòng nhập lại."

Người dùng cũng nhận được một error ID mà họ có thể cung cấp cho support nếu cần.

## 4.5 Triển Khai Monitoring

### 4.5.1 Instrumentation

**Thêm Tracing vào Code**

Sử dụng thư viện OpenTelemetry, hệ thống thêm tracing tới các phần quan trọng:

- FastAPI endpoints: Tự động traced bằng middleware
- Database queries: Traced bằng custom wrapper
- LLM calls: Traced bằng callback function
- Tool execution: Traced bằng decorator

[CODE BLOCK: Instrumentation example - Placeholder for Python code showing OpenTelemetry instrumentation]

**Thu Thập Metrics**

Sử dụng Prometheus client library, hệ thống thu thập các metrics:

```python
# Request metrics
request_count = Counter('http_requests_total', 'Total HTTP requests')
request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')

# Database metrics
db_query_duration = Histogram('db_query_duration_seconds', 'Database query duration')
db_connection_pool_size = Gauge('db_connection_pool_size', 'Database connection pool size')

# LLM metrics
llm_api_calls = Counter('llm_api_calls_total', 'Total LLM API calls')
llm_api_cost = Counter('llm_api_cost_total', 'Total LLM API cost')

# Tool metrics
tool_execution_duration = Histogram('tool_execution_duration_seconds', 'Tool execution duration')
tool_errors = Counter('tool_errors_total', 'Total tool errors')
```

### 4.5.2 Dashboards

Grafana dashboards được tạo để trực quan hóa các metrics:

- **Dashboard Hiệu Suất**: Thời gian phản hồi P50/P95/P99, throughput, tỷ lệ lỗi
- **Dashboard Cơ Sở Dữ Liệu**: Số lượng kết nối, thời gian truy vấn, kích thước dữ liệu
- **Dashboard LLM**: Số lần gọi, chi phí, latency, error rate
- **Dashboard Hệ Thống**: CPU, bộ nhớ, disk usage, network bandwidth

[IMAGE/DIAGRAM: Grafana Dashboard Mockup - Placeholder for screenshot of monitoring dashboard]

## 4.6 Kết Luận Chương 4

Chương này đã chi tiết hóa cách triển khai các thành phần chính của hệ thống. Triển khai agent logic tuân theo mô hình vòng lặp của LangChain, với hỗ trợ cho prompt engineering, model configuration, và memory management. Các công cụ được triển khai theo một interface chung, cho phép tác nhân dễ dàng gọi chúng.

Quản lý trò chuyện sử dụng PostgreSQL cho lưu trữ bền vững và bộ nhớ buffer cho ngữ cảnh hiện tại. Xử lý lỗi bao gồm các cơ chế retry, circuit breaker, và logging chi tiết. Cuối cùng, monitoring được triển khai bằng cách sử dụng OpenTelemetry cho tracing và Prometheus cho metrics collection.

Chương tiếp theo sẽ tập trung vào infrastructure và DevOps, đặc biệt là CI/CD pipeline với GitHub Actions.
