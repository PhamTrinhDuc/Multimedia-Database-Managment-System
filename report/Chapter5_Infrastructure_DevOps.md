# Chương 5: Infrastructure và DevOps

## 5.1 CI/CD Pipeline với GitHub Actions

### 5.1.1 Tổng Quan Pipeline

GitHub Actions là nền tảng tự động hóa các quy trình công việc (workflows) được tích hợp trực tiếp vào repository GitHub. Dự án sử dụng GitHub Actions để triển khai một quy trình CI/CD toàn diện từ việc kiểm tra code cho đến triển khai lên môi trường sản xuất.

[IMAGE/DIAGRAM: GitHub Actions Workflow Pipeline - Placeholder showing stages: Push to GitHub → Code Quality Checks → Build Docker Images → Run Tests → Deploy to Staging → Smoke Tests → Deploy to Production]

**Các Giai Đoạn Pipeline**

Quy trình CI/CD được chia thành các giai đoạn sau:

**Giai Đoạn 1 - Code Quality Checks (Kiểm Tra Chất Lượng Mã)**

Khi code được push lên GitHub, GitHub Actions tự động chạy các kiểm tra chất lượng mã:
- Linting: Kiểm tra xem code có tuân theo style guide không (sử dụng pylint hoặc flake8 cho Python)
- Formatting: Kiểm tra xem code có được format đúng không (sử dụng black cho Python)
- Type checking: Kiểm tra xem các type hints có đúng không (sử dụng mypy)
- Security scanning: Kiểm tra xem code có chứa các lỗ hổng bảo mật không (sử dụng Bandit)

Nếu bất kỳ kiểm tra nào fail, workflow dừng lại và developer nhận được thông báo.

**Giai Đoạn 2 - Build Docker Images (Xây Dựng Docker Images)**

Nếu tất cả kiểm tra chất lượng pass, GitHub Actions tiến hành xây dựng Docker images cho các thành phần:
- Backend (FastAPI)
- Frontend (Streamlit)
- Worker (nếu có xử lý async jobs)

Docker images được xây dựng theo multi-stage build pattern để giảm kích thước:
- Stage 1 (Builder): Cài đặt dependencies, build project
- Stage 2 (Runtime): Copy artifacts từ Stage 1, chỉ chứa runtime dependencies

Docker images được tag với:
- Git commit SHA (ví dụ `app-backend:abc1234def5678`)
- Git branch name (ví dụ `app-backend:develop`, `app-backend:main`)
- Semantic version (ví dụ `app-backend:1.2.3`)

**Giai Đoạn 3 - Run Tests (Chạy Tests)**

Các Docker images được sử dụng để chạy unit tests và integration tests:
- Unit tests: Kiểm tra từng function/method riêng lẻ
- Integration tests: Kiểm tra xem các thành phần hoạt động cùng nhau như thế nào
- End-to-end (E2E) tests: Kiểm tra toàn bộ workflow từ user input đến final output

Coverage reports được tạo ra để theo dõi bao nhiêu phần trăm code được test. Target coverage là 70%.

**Giai Đoạn 4 - Deploy to Staging (Triển Khai tới Staging)**

Nếu tất cả tests pass, Docker images được push lên Docker registry (ví dụ Docker Hub hoặc AWS ECR), sau đó được triển khai lên môi trường staging.

Staging là một môi trường có cấu trúc giống với production, cho phép kiểm thử cuối cùng trước khi triển khai lên production.

**Giai Đoạn 5 - Smoke Tests on Staging (Kiểm Tra Smoke Tests)**

Sau khi triển khai lên staging, các smoke tests được chạy để đảm bảo rằng hệ thống hoạt động như mong đợi:
- Health check: Gọi `/health` endpoint
- Basic functionality: Thử một vài câu hỏi cơ bản
- Performance check: Kiểm tra xem response time có chấp nhận được không

**Giai Đoạn 6 - Deploy to Production (Triển Khai tới Production)**

Nếu smoke tests pass, developer có thể bấm nút để triển khai lên production. Hoặc, pipeline có thể được cấu hình để tự động triển khai (auto-deploy) khi pass tất cả checks.

Triển khai sử dụng rolling update strategy để tránh downtime:
- Khởi động các container mới với version mới
- Chờ cho đến khi health checks pass
- Dần dần di chuyển traffic từ container cũ sang container mới
- Sau khi tất cả traffic đã di chuyển, dừng containers cũ

### 5.1.2 GitHub Actions Workflow Definition

[CODE BLOCK: GitHub Actions Workflow YAML - Placeholder for .github/workflows/ci-cd.yml showing:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install pylint flake8 black mypy bandit
      
      - name: Run linting
        run: pylint src/
      
      - name: Run formatting check
        run: black --check src/
      
      - name: Run type checking
        run: mypy src/
      
      - name: Run security scan
        run: bandit -r src/
  
  build-images:
    needs: code-quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Build backend image
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: false
          tags: app-backend:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha
  
  test:
    needs: build-images
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run unit tests
        run: docker-compose -f docker-compose.test.yml up --abort-on-container-exit
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  deploy-staging:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to staging
        run: |
          # Deploy scripts here
          ./scripts/deploy-staging.sh
  
  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        run: |
          ./scripts/deploy-production.sh
```
]

### 5.1.3 Triggers và Conditions

**Push Trigger**

Pipeline được kích hoạt khi code được push lên các nhánh chính:
- `main`: Production branch, mọi commit đều được triển khai lên production
- `develop`: Development branch, các commits được triển khai lên staging

**Pull Request Trigger**

Pipeline cũng được chạy khi có pull request. Trong trường hợp này, pipeline chỉ chạy các kiểm tra chất lượng, build, và tests, nhưng không triển khai tới staging hoặc production. Merge request chỉ được cho phép nếu tất cả checks pass.

**Manual Trigger (Workflow Dispatch)**

Developer có thể bấm nút để chạy pipeline thủ công, ngay cả khi không có code changes. Điều này hữu ích trong trường hợp cần redeploy hay re-run tests.

**Scheduled Trigger (Cron)**

Pipeline cũng có thể được chạy theo lịch định kỳ (ví dụ mỗi ngày lúc 2 AM) để chạy các performance tests hoặc security audits.

### 5.1.4 Artifacts and Caching

**Docker Layer Caching**

Để tăng tốc độ build, GitHub Actions sử dụng layer caching. Mỗi layer của Dockerfile được cache, nên nếu chỉ có changes ở layer cuối cùng, các layer trước không cần rebuild.

**Dependency Caching**

Python dependencies được cache để tránh download lại mỗi lần. Cache key được tính dựa trên hash của requirements.txt, nên nếu không có changes, dependencies cũ được sử dụng.

**Artifact Storage**

Các artifacts như coverage reports, build logs, v.v. được lưu trữ trong GitHub Actions artifact storage để review sau.

### 5.1.5 Notifications

**Slack Notifications**

Khi pipeline fail, một notification được gửi tới Slack channel:

```
🚨 CI/CD Pipeline Failed
Repository: LLM-Chatbot-with-LangChain-and-Neo4j
Branch: develop
Commit: abc1234def5678
Message: Code quality checks failed
Failed stage: pylint
Error: Module X has issues
Author: @john.doe
Action: https://github.com/org/repo/actions/runs/12345
```

**Email Notifications**

Ngoài Slack, email notifications cũng được gửi cho developers.

**GitHub Status Checks**

GitHub tự động hiển thị status của pipeline trên pull request page, cho phép developers dễ dàng thấy xem pipeline pass hay fail.

## 5.2 Containerization với Docker

### 5.2.1 Multi-Container Architecture

[IMAGE/DIAGRAM: Docker Compose Architecture - Placeholder showing all containers and their relationships: frontend, backend, neo4j, postgres, elasticsearch, redis, prometheus, grafana]

**Frontend Container (Streamlit)**

```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src/ .

EXPOSE 8501

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501')"

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Backend Container (FastAPI)**

Dockerfile cho backend tương tự, sử dụng multi-stage build. Đặc biệt:
- Expose port 8000 (hoặc port khác tùy cấu hình)
- Health check gọi `/health` endpoint
- Sử dụng Uvicorn ASGI server với gunicorn wrapper để handle multiple workers

**Database Containers**

Cho Neo4j, PostgreSQL, Elasticsearch, Redis, các container được sử dụng từ official images từ Docker Hub, với cấu hình tùy chỉnh thông qua environment variables.

### 5.2.2 Docker Compose Configuration

[CODE BLOCK: docker-compose.yml - Placeholder for full docker-compose configuration showing all services, volumes, networks, environment variables]

**Version và Services**

```yaml
version: '3.9'

services:
  frontend:
    build: ./frontend
    ports:
      - "8501:8501"
    environment:
      BACKEND_URL: http://backend:8000
    depends_on:
      - backend
    networks:
      - app-network
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      NEO4J_URL: bolt://neo4j:7687
      POSTGRES_URL: postgresql://user:pass@postgres:5432/appdb
      ELASTICSEARCH_URL: http://elasticsearch:9200
      REDIS_URL: redis://redis:6379
    depends_on:
      - neo4j
      - postgres
      - elasticsearch
      - redis
    networks:
      - app-network
  
  neo4j:
    image: neo4j:5.0
    ports:
      - "7687:7687"
      - "7474:7474"
    environment:
      NEO4J_AUTH: neo4j/password
    volumes:
      - neo4j-data:/var/lib/neo4j/data
    networks:
      - app-network
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: appdb
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - app-network
  
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
    environment:
      discovery.type: single-node
      xpack.security.enabled: false
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    networks:
      - app-network
  
  redis:
    image: redis:7-alpine
    networks:
      - app-network

volumes:
  neo4j-data:
  postgres-data:
  elasticsearch-data:

networks:
  app-network:
    driver: bridge
```

### 5.2.3 Build Optimization

**Multi-Stage Builds**

Sử dụng multi-stage builds để giảm kích thước final image:
- Builder stage: Cài đặt tất cả dependencies (bao gồm cả dev dependencies)
- Runtime stage: Copy chỉ những gì cần thiết (không copy dev dependencies)

Điều này giảm kích thước image từ ~500MB xuống ~200MB.

**Layer Caching**

Sắp xếp Dockerfile sao cho các layers thay đổi ít nhất ở cuối:
1. FROM (không thay đổi)
2. System packages (ít thay đổi)
3. Python dependencies (thay đổi thỉnh thoảng)
4. Application code (thay đổi thường xuyên)

Nếu chỉ application code thay đổi, Docker có thể reuse các layers trước đó.

**Minimal Base Images**

Sử dụng minimal base images như `python:3.11-slim` hoặc `python:3.11-alpine` thay vì `python:3.11` (full version).

### 5.2.4 Volume Management

**Named Volumes**

Các databases sử dụng named volumes để persist dữ liệu:

```yaml
volumes:
  neo4j-data:
    driver: local
  postgres-data:
    driver: local
  elasticsearch-data:
    driver: local
```

Volumes này có thể được backup bằng lệnh:

```bash
docker run --rm -v neo4j-data:/data -v $(pwd):/backup \
  busybox tar czf /backup/neo4j-backup.tar.gz -C /data .
```

**Bind Mounts**

Trong development, code có thể được mounted vào container sử dụng bind mount:

```yaml
backend:
  volumes:
    - ./backend/src:/app/src
```

Điều này cho phép developer chỉnh sửa code và thấy changes ngay lập tức (nếu app hỗ trợ hot reload).

## 5.3 Deployment Strategy

### 5.3.1 Rolling Update

Rolling update là chiến lược triển khai mặc định, giúp tránh downtime:

[IMAGE/DIAGRAM: Rolling Update Process - Placeholder showing 4-step process: All serving V1 → 75% V1 + 25% V2 → 50% V1 + 50% V2 → All serving V2]

**Quá Trình**

1. **Chuẩn Bị**: Tạo containers mới với version mới, nhưng chưa gửi traffic tới
2. **Health Check**: Chạy health checks trên containers mới để đảm bảo khởi động thành công
3. **Gradual Traffic Shift**: Dần dần chuyển traffic từ containers cũ sang containers mới
4. **Cleanup**: Sau khi tất cả traffic đã chuyển, dừng containers cũ

**Lợi Ích**

- Không có downtime
- Dễ dàng rollback nếu có issues (vì containers cũ vẫn chạy)
- Cho phép A/B testing

**Nhược Điểm**

- Phức tạp hơn so với other strategies
- Database migrations phải backward compatible

### 5.3.2 Blue-Green Deployment

[IMAGE/DIAGRAM: Blue-Green Deployment - Placeholder showing two identical production environments, switch from Blue to Green]

Ngoài rolling update, dự án cũng có thể sử dụng blue-green deployment khi cần:

**Quá Trình**

1. **Blue Environment**: Version hiện tại đang serving traffic
2. **Green Environment**: Version mới được deployed và tested
3. **Switch**: Khi ready, switch traffic từ Blue sang Green
4. **Rollback**: Nếu có issues, switch lại tới Blue

**Lợi Ích**

- Rất dễ rollback (chỉ cần switch traffic)
- Zero downtime
- Cho phép testing trên version mới trước khi publish

**Nhược Điểm**

- Cần gấp đôi resources
- Tất cả data phải sync giữa Blue và Green

### 5.3.3 Canary Deployment

Canary deployment là một chiến lược khác, trong đó version mới được triển khai cho một tập con nhỏ người dùng trước:

**Quá Trình**

1. Triển khai version mới cho 5% người dùng
2. Monitor metrics (error rate, latency, v.v.)
3. Nếu metrics bình thường, tăng lên 25%
4. Tiếp tục tăng dần cho đến khi 100%
5. Nếu bất kỳ lúc nào metrics xấu, rollback

**Lợi Ích**

- Giảm thiểu risk khi triển khai version mới
- Cho phép phát hiện issues trước khi affect tất cả users

## 5.4 Monitoring và Alerting

### 5.4.1 Metrics Collection

**Prometheus Configuration**

Prometheus được cấu hình để scrape metrics từ các endpoints:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
  
  - job_name: 'neo4j'
    static_configs:
      - targets: ['localhost:7687']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:5432']
  
  - job_name: 'elasticsearch'
    static_configs:
      - targets: ['localhost:9200']
```

**Recording Rules**

Recording rules được sử dụng để tính toán các metrics phức tạp một lần mỗi 15 giây, thay vì tính toán mỗi lần query:

```yaml
groups:
  - name: application
    interval: 15s
    rules:
      - record: rate:http_requests:5m
        expr: rate(http_requests_total[5m])
      
      - record: rate:http_errors:5m
        expr: rate(http_requests_total{status=~"5.."}[5m])
```

### 5.4.2 Alerting Rules

[CODE BLOCK: Prometheus Alerting Rules - Placeholder for alert rules YAML]

**Alert Definition**

```yaml
groups:
  - name: application_alerts
    rules:
      - alert: HighErrorRate
        expr: rate:http_errors:5m > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s"
      
      - alert: DatabaseDown
        expr: up{job="neo4j"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Neo4j database is down"
          description: "Neo4j has been down for more than 1 minute"
```

**Alerting Channels**

Alerts được gửi tới nhiều channels:

- **Slack**: Immediate notification với details
- **Email**: Backup notification
- **PagerDuty**: Để oncall engineers nhận notification trên điện thoại

### 5.4.3 Dashboards

**System Health Dashboard**

Hiển thị tổng thể sức khỏe hệ thống:
- CPU, Memory, Disk usage
- Network bandwidth
- Container status
- Service status

**Application Performance Dashboard**

Hiển thị hiệu suất ứng dụng:
- Request count (total, per endpoint, per method)
- Response time (P50, P95, P99)
- Error rate
- LLM API latency

**Business Metrics Dashboard**

Hiển thị metrics kinh doanh:
- Active users
- Questions answered per day
- User satisfaction score
- Cost per query

### 5.4.4 Distributed Tracing

**Phoenix Tracing Setup**

Phoenix được deployed như một backend service, và tất cả các components được instrumented để gửi traces tới Phoenix:

```python
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger",
    agent_port=6831,
)

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)
```

**Trace Analysis**

Traces được phân tích để:
- Identify bottlenecks
- Debug performance issues
- Track request flow qua các components

### 5.4.5 Log Aggregation

**ELK Stack Deployment**

```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    discovery.type: single-node
    xpack.security.enabled: false

logstash:
  image: docker.elastic.co/logstash/logstash:8.0.0
  volumes:
    - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
  depends_on:
    - elasticsearch

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
  environment:
    ELASTICSEARCH_HOSTS: http://elasticsearch:9200
  depends_on:
    - elasticsearch
```

**Logstash Filters**

Logstash được cấu hình để parse và enrich logs:

```
input {
  tcp {
    port => 5000
  }
}

filter {
  mutate {
    add_field => { "received_at" => "%{@timestamp}" }
  }
  
  if [message] =~ /ERROR/ {
    mutate { add_tag => [ "error" ] }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
}
```

**Kibana Dashboards**

Kibana dashboards được tạo để visualize logs:
- Real-time log tail
- Error log alerts
- Log search and filtering

## 5.5 Infrastructure as Code (IaC)

Dự án sử dụng Docker Compose cho development. Cho production, có thể sử dụng Kubernetes với Helm charts, hoặc Terraform để manage AWS resources.

### 5.5.1 Environment Configuration

Các environment khác nhau (development, staging, production) được managed thông qua:

- `docker-compose.yml`: Development
- `docker-compose.staging.yml`: Staging
- `docker-compose.prod.yml`: Production (simplified, actual prod dùng Kubernetes)

Mỗi file có các values khác nhau cho:
- Replicas (development: 1, staging: 2, production: 3+)
- Resource limits (development: low, staging: medium, production: high)
- Environment variables (API keys, database URLs, v.v.)

### 5.5.2 Database Migrations

Database migrations được managed bằng Alembic (cho PostgreSQL) hoặc Liquibase (multi-database):

```bash
# Create migration
alembic revision --autogenerate -m "Add user table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

Migrations được chạy tự động khi deploying version mới, và được versioned cùng với code.

## 5.6 Kết Luận Chương 5

Chương này đã chi tiết hóa infrastructure và DevOps practices của dự án. GitHub Actions được sử dụng để triển khai một quy trình CI/CD toàn diện, tự động kiểm tra chất lượng, build, test, và triển khai. Docker được sử dụng cho containerization, với docker-compose để manage multiple containers.

Deployment strategy sử dụng rolling update mặc định để tránh downtime, với tùy chọn sử dụng blue-green hoặc canary deployment cho các tình huống cụ thể. Monitoring được thực hiện thông qua Prometheus, Grafana, ELK Stack, và Phoenix Tracing, cho phép theo dõi toàn diện hiệu suất hệ thống.

Chương tiếp theo sẽ tập trung vào kết quả và đánh giá dự án.
