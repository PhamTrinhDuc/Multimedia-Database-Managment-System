# Chương 1: Bối cảnh và Định vị Dự Án

## 1.1 Bối cảnh Ngành và Nhu cầu Thực tiễn

### 1.1.1 Tình Hình Hiện Tại trong Lĩnh vực Y tế

Các tổ chức y tế và hệ thống bệnh viện lớn trên thế giới hiện đang đối mặt với những thách thức đáng kể:

**Thách thức 1: Sự gia tăng dữ liệu và khó khăn trong quản lý**

Mỗi bệnh viện phải xử lý hàng triệu bản ghi bệnh nhân, nhân viên y tế, điều dưỡng và giao dịch thanh toán hàng năm. Dữ liệu này nằm rải rác ở nhiều hệ thống khác nhau bao gồm hệ thống hồ sơ y tế điện tử, hệ thống thanh toán, và hệ thống quản lý nhân sự. Việc tích hợp và kết hợp dữ liệu từ các nguồn này rất phức tạp.

**Thách thức 2: Thời gian xử lý truy vấn quá dài**

Khi một quản lý bệnh viện cần câu trả lời cho một truy vấn đặc thù, quy trình hiện tại bao gồm: gửi yêu cầu đến phòng công nghệ thông tin, chờ nhân viên phân tích viết truy vấn cơ sở dữ liệu, chờ truy vấn được thực thi, và cuối cùng nhận kết quả (thường không chính xác lần đầu và cần chỉnh sửa). Chu kỳ thời gian điển hình từ 1 đến 3 ngày hoặc thậm chí lâu hơn.

**Thách thức 3: Thiếu khả năng tự phục vụ**

Hầu hết nhân viên không có kiến thức về ngôn ngữ truy vấn cơ sở dữ liệu và do đó không thể đặt câu hỏi một cách độc lập. Họ phải phụ thuộc vào nhân viên phân tích hoặc phòng công nghệ thông tin, tạo thành một nút cổ chai trong tổ chức.

**Thách thức 4: Khó khăn trong phân tích trải nghiệm bệnh nhân**

Phản hồi và nhận xét của bệnh nhân được lưu trữ ở nhiều nơi: khảo sát sự hài lòng, nền tảng đánh giá trực tuyến, biểu mẫu phản hồi nội bộ và ghi chú của bác sĩ. Không có phương pháp toàn diện để tổng hợp ý kiến của bệnh nhân. Một truy vấn như "Bệnh nhân nói gì về chất lượng dịch vụ tại bệnh viện X" không có câu trả lời nhanh chóng.

**Thách thức 5: Hạn chế trong phân tích đa chiều**

Để trả lời các câu hỏi phức tạp như "Bệnh viện nào có thời gian chờ dài nhất, phàn nàn nhiều nhất, và có mối liên quan đến những công ty bảo hiểm nào", cần kết hợp dữ liệu từ 4 đến 5 hệ thống khác nhau, điều này rất khó khăn với cơ sở hạ tầng hiện tại.

### 1.1.2 Nhu cầu từ Các Bên Liên quan

Thông qua các cuộc họp với các quản lý bệnh viện, các yêu cầu chính sau đã được xác định:

**Yêu cầu 1: Trả lời nhanh các truy vấn đặc thù**

Các quản lý cần được cấp câu trả lời nhanh chóng cho những câu hỏi như: "Có bao nhiêu bệnh nhân có bảo hiểm Medicaid tại Texas năm 2023?", "Bệnh viện nào hiện có thời gian chờ dài nhất?", "Bác sĩ John Smith đã điều trị bao nhiêu bệnh nhân?", "Tổng chi phí thanh toán cho công ty bảo hiểm Cigna là bao nhiêu?", "Thời gian nằm viện trung bình cho ca nhập viện cấp cứu bảo hiểm Medicaid?". Yêu cầu là câu trả lời phải có trong vòng dưới 5 giây, trong khi hiện tại phải chờ từ 1 đến 3 ngày.

**Yêu cầu 2: Tìm hiểu trải nghiệm bệnh nhân từ phản hồi**

Một nhu cầu khác là có thể tìm hiểu những gì bệnh nhân nói về chất lượng dịch vụ, phàn nàn về nhân viên tại bệnh viện cụ thể, đánh giá về trang thiết bị, hoặc lý do bệnh nhân không quay lại. Yêu cầu là khả năng tổng hợp ý kiến từ hàng trăm bình luận và đánh giá, trong khi hiện tại phải đọc thủ công hoặc không thể xử lý.

**Yêu cầu 3: Khả năng tự phục vụ**

Nhân viên không chuyên về công nghệ thông tin cần có khả năng đặt câu hỏi bằng ngôn ngữ tự nhiên và nhận được câu trả lời tức thì mà không cần hiểu biết về các ngôn ngữ truy vấn cơ sở dữ liệu. Hiện tại họ phải liên hệ với nhân viên phân tích.

**Yêu cầu 4: Giải thích và độ tin cậy**

Cần biết rõ dữ liệu xuất phát từ đâu, cách tính toán như thế nào, có thể kiểm chứng lại, và tạo vết kiểm toán cho mục đích tuân thủ quy định y tế. Hiện tại đôi khi không rõ nguồn gốc dữ liệu.

**Yêu cầu 5: Hỗ trợ chẩn đoán tâm lý**

Là yêu cầu mở rộng thêm, bao gồm khả năng cung cấp thông tin về tiêu chuẩn chẩn đoán tâm thần, triệu chứng trầm cảm, sự khác biệt giữa các rối loạn lo âu, v.v. Yêu cầu là cung cấp thông tin chuẩn hóa với độ tin cậy cao.

### 1.1.3 Các Mô hình Ngôn ngữ Lớn và Khả năng của Chúng

Những năm gần đây, các mô hình ngôn ngữ lớn đã chứng minh được những khả năng đáng chú ý:

**Khả năng 1: Hiểu biết ngôn ngữ tự nhiên**

Các mô hình có thể xử lý câu hỏi bằng ngôn ngữ tự nhiên, nhận diện ý định của người dùng (truy vấn cấu trúc so với tìm kiếm ngữ nghĩa so với tra cứu tham khảo), và trích xuất các thực thể quan trọng như tên bệnh viện, thời gian, hoặc tên công ty bảo hiểm. Ví dụ, với đầu vào "Tổng cộng bao nhiêu bệnh nhân từ Cigna tại Texas từ 2022 đến 2024?", mô hình có thể hiểu rằng ý định là lấy thống kê tổng hợp với các thực thể là công ty bảo hiểm Cigna, tiểu bang Texas, và khoảng thời gian từ 2022 đến 2024.

**Khả năng 2: Suy luận đa bước**

Các mô hình có thể phân tích các câu hỏi phức tạp, chia nhỏ chúng thành các tác vụ con, và kết hợp kết quả từ nhiều nguồn dữ liệu. Ví dụ, để trả lời câu hỏi "Bệnh viện nào có thời gian chờ dài nhất nhưng lại có đánh giá tích cực nhất?", mô hình có thể: bước 1 lấy dữ liệu thời gian chờ từ các nguồn hoạt động, bước 2 tìm kiếm và phân tích đánh giá để tính toán cảm xúc của bệnh nhân, bước 3 kết hợp và sắp xếp kết quả.

**Khả năng 3: Tạo mã truy vấn tự động**

Các mô hình có thể tạo ra các truy vấn cơ sở dữ liệu từ ngôn ngữ tự nhiên, xác thực cú pháp và logic của chúng. Với đầu vào "Bác sĩ nào điều trị nhiều bệnh nhân bảo hiểm Medicaid nhất?", mô hình có thể tự động tạo ra truy vấn phù hợp để thực thi trên cơ sở dữ liệu.

**Khả năng 4: Tổng hợp và giải thích**

Các mô hình có thể đọc và tóm tắt hàng trăm tài liệu, trích xuất thông tin chính, và giải thích bằng ngôn ngữ dễ hiểu. Để trả lời "Bệnh nhân nói gì về nhân viên tại Bệnh viện A?", mô hình có thể tìm kiếm các bình luận liên quan, trích xuất các ý kiến về nhân viên, và tổng hợp thành một câu trả lời toàn diện.

### 1.1.4 Tại sao Phương pháp Tạo sinh Tăng cường Truy vấn là Giải pháp

Phương pháp tạo sinh tăng cường truy vấn kết hợp ba thành phần chính: truy vấn dữ liệu từ các cơ sở dữ liệu, cung cấp dữ liệu đó làm ngữ cảnh cho mô hình ngôn ngữ, và mô hình tạo ra câu trả lời dựa trên dữ liệu được cung cấp. So với sử dụng mô hình ngôn ngữ một mình, phương pháp này mang lại lợi ích: dữ liệu được kiểm chứng thay vì bịa đặt, thông tin luôn cập nhật, kiến thức miền được tích hợp, và người dùng có thể hiểu được nguồn gốc của thông tin.

## 1.2 Mục Tiêu và Phạm Vi Dự Án

### 1.2.1 Mục Tiêu Chính

Dự án này được xây dựng với bốn mục tiêu chính:

**Mục tiêu 1: Xây dựng hệ thống trò chuyện thông minh**

Phát triển một ứng dụng trò chuyện có khả năng trả lời các câu hỏi từ nhiều nguồn dữ liệu khác nhau, tự động lựa chọn công cụ và chiến lược phù hợp, giải thích được cách thức tính toán, và xử lý lỗi một cách tự nhiên.

**Mục tiêu 2: Xử lý các câu hỏi kết hợp dữ liệu cấu trúc và không cấu trúc**

Hệ thống phải có khả năng trả lời hai loại câu hỏi khác biệt: truy vấn định lượng như "Tổng chi phí thanh toán cho công ty bảo hiểm Aetna tại California?" yêu cầu dữ liệu chính xác từ cơ sở dữ liệu, cũng như truy vấn định tính như "Bệnh nhân nói gì về chất lượng dịch vụ?" yêu cầu phân tích ngữ nghĩa của các đánh giá và bình luận. Ngoài ra, hệ thống cần hỗ trợ các truy vấn kết hợp như "Bệnh viện nào có thời gian chờ cao nhưng đánh giá tốt?" đòi hỏi kết hợp thông tin từ nhiều nguồn và loại dữ liệu.

**Mục tiêu 3: Triển khai hệ thống sẵn sàng cho môi trường sản xuất**

Hệ thống cần thiết phải có giám sát toàn diện, ghi nhật ký chi tiết, khả năng sẵn sàng cao với xử lý lỗi tự động, thời gian phản hồi được tối ưu hóa, bảo mật và tuân thủ quy định, tự động hóa triển khai thông qua GitHub Actions, cũng như kiến trúc có khả năng mở rộng để hỗ trợ nhu cầu tăng.

**Mục tiêu 4: Cung cấp các tính năng mở rộng**

Hệ thống bao gồm các tính năng vượt quá những hệ thống cơ bản: hỗ trợ cơ sở dữ liệu tham khảo tiêu chuẩn chẩn đoán tâm thần, quản lý lịch sử trò chuyện nhiều vòng, xác thực và quản lý người dùng, cũng như ngăn xếp giám sát toàn diện bao gồm tracing, metrics, và logging tập trung.

### 1.2.2 Phạm Vi Dự Án

**Những thành phần được bao gồm**

Dự án bao gồm: dữ liệu hoạt động của bệnh viện như thông tin bệnh nhân, bác sĩ, bệnh viện, cuộc khám bệnh và công ty bảo hiểm; các bình luận và đánh giá của bệnh nhân cùng với phân tích cảm xúc; thông tin thời gian chờ cho các hoạt động; cơ sở dữ liệu tham khảo tiêu chuẩn chẩn đoán tâm thần; quản lý lịch sử trò chuyện và phiên làm việc người dùng; công nghệ bao gồm tác nhân LangChain, Neo4j, Elasticsearch, PostgreSQL, FastAPI, Streamlit, GitHub Actions, cũng như ngăn xếp giám sát hoàn chỉnh với Phoenix, Prometheus, Grafana, và ELK.

**Những thành phần không được bao gồm**

Không bao gồm tuân thủ quy định HIPAA thực tế do sử dụng dữ liệu tổng hợp; tích hợp với các hệ thống hồ sơ y tế điện tử hiện có của bệnh viện; xử lý thanh toán thực tế; hoặc tinh chỉnh mô hình ngôn ngữ tự nhiên chuyên sâu trên dữ liệu miền, vì dự án sử dụng các mô hình được đào tạo trước từ OpenAI.

### 1.2.3 Chỉ Số Đánh Giá Thành Công

Các chỉ số định lượng bao gồm: thời gian phản hồi ở phân vị 95 phải dưới 3 giây, tính khả dụng không dưới 99%, tỷ lệ thành công truy vấn ít nhất 95%, và độ chính xác kết quả ít nhất 90%. Về việc sử dụng, hệ thống phải phục vụ ít nhất 50 người dùng hoạt động hàng ngày, xử lý 200 truy vấn trở lên mỗi ngày, duy trì tỷ lệ người dùng quay lại ít nhất 60%, và mỗi cuộc trò chuyện có ít nhất 3 vòng tương tác. Từ góc độ chi phí, chi phí cơ sở hạ tầng mỗi tháng dưới 500 đô la, chi phí API mô hình ngôn ngữ dưới 1000 đô la mỗi tháng, và chi phí mỗi truy vấn dưới 0,10 đô la.

Các chỉ số định tính bao gồm độ chính xác lựa chọn công cụ, rõ ràng giải thích, xử lý lỗi tự nhiên, cũng như tính khả quan sát cao. Chất lượng hệ thống bao gồm khả năng bảo trì mã, độ hoàn chỉnh tài liệu, độ bao phủ kiểm tra trên 70%, và hiệu quả giám sát.

## 1.3 Kiến Trúc và Phương Pháp Tiếp Cận

### 1.3.1 Kiến Trúc Tổng Thể

Hệ thống được xây dựng trên kiến trúc microservices với ba tầng chính: tầng giao diện người dùng sử dụng Streamlit để cung cấp trải nghiệm web tương tác, tầng ứng dụng sử dụng FastAPI để xử lý logic ứng dụng và API, và tầng dữ liệu sử dụng Neo4j cho dữ liệu đồ thị, Elasticsearch cho tìm kiếm vector, PostgreSQL cho dữ liệu có cấu trúc, và Redis cho cache và phiên. Tất cả các thành phần được container hóa bằng Docker và điều phối bằng Docker Compose.

**Tầng Ứng Dụng Chi Tiết**

Tầng ứng dụng sử dụng LangChain để xây dựng một tác nhân có khả năng suy luận. Tác nhân này có quyền truy cập vào các công cụ bao gồm: công cụ truy vấn Cypher cho Neo4j để truy vấn dữ liệu cấu trúc, công cụ tìm kiếm Elasticsearch cho phân tích ngữ nghĩa, công cụ tham khảo cơ sở dữ liệu chẩn đoán tâm thần, và công cụ lấy lịch sử trò chuyện từ PostgreSQL. Khi một người dùng đặt câu hỏi, tác nhân này tự động quyết định công cụ nào cần gọi, theo thứ tự nào, và cách kết hợp kết quả.

**Phương Pháp Tạo sinh Tăng cường Truy vấn**

Hệ thống sử dụng phương pháp tạo sinh tăng cường truy vấn làm nền tảng. Khi người dùng đặt câu hỏi, hệ thống: (1) sử dụng mô hình ngôn ngữ để hiểu ý định và trích xuất các thực thể, (2) truy vấn các cơ sở dữ liệu thích hợp để lấy dữ liệu liên quan, (3) cung cấp dữ liệu đó làm ngữ cảnh cho mô hình ngôn ngữ, và (4) mô hình tạo ra câu trả lời dựa trên dữ liệu được cung cấp. Phương pháp này đảm bảo rằng câu trả lời được đặt trên cơ sở của dữ liệu thực tế thay vì được bịa đặt.

### 1.3.2 Tính Năng Chính

**Xử lý Truy vấn Cấu trúc**

Hệ thống có thể xử lý các câu hỏi về dữ liệu cấu trúc như "Có bao nhiêu bệnh nhân Medicaid tại Texas?" bằng cách: tác nhân hiểu ý định là truy vấn thống kê, xác định các thực thể là bảo hiểm Medicaid, tiểu bang Texas, tạo truy vấn Cypher phù hợp, thực thi trên Neo4j, và trả về kết quả.

**Xử lý Truy vấn Ngữ nghĩa**

Hệ thống có thể xử lý các câu hỏi về dữ liệu không có cấu trúc như "Bệnh nhân nói gì về nhân viên y tế?" bằng cách: tác nhân hiểu ý định là tìm kiếm ngữ nghĩa, tìm kiếm trong Elasticsearch các tài liệu liên quan đến nhân viên y tế, trích xuất các ý kiến chính, và tổng hợp thành câu trả lời.

**Xử lý Truy vấn Kết hợp**

Hệ thống có thể xử lý các câu hỏi phức tạp như "Bệnh viện nào có thời gian chờ dài nhưng đánh giá tốt?" bằng cách: tác nhân chia nhỏ thành các tác vụ con, truy vấn Neo4j để lấy thời gian chờ, tìm kiếm Elasticsearch để phân tích cảm xúc, kết hợp và sắp xếp kết quả.

**Lịch sử Trò chuyện Liên tục**

Hệ thống duy trì lịch sử trò chuyện, cho phép người dùng tham khảo các câu hỏi trước đó. Khi người dùng hỏi "Cái nào có wait time lâu nhất?", hệ thống hiểu ngữ cảnh từ câu hỏi trước "Bệnh viện nào ở Texas?" và chỉ tập trung vào những bệnh viện ở Texas.

**Hỗ Trợ Chẩn Đoán Tâm Thần**

Hệ thống tích hợp cơ sở dữ liệu tiêu chuẩn chẩn đoán tâm thần, cho phép các truy vấn như "Tiêu chuẩn chẩn đoán tâm thần cho trầm cảm là gì?" hoặc "Sự khác biệt giữa rối loạn lo âu và rối loạn hoảng sợ?"

### 1.3.3 Ngăn Xếp Giám Sát

Hệ thống bao gồm một ngăn xếp giám sát toàn diện: Phoenix Tracing theo dõi chi tiết mỗi yêu cầu từ khi vào cho đến khi ra, Prometheus thu thập các số liệu hệ thống như thời gian phản hồi và tỷ lệ lỗi, Grafana trực quan hóa các số liệu này trên các bảng điều khiển, và ELK Stack (Elasticsearch, Logstash, Kibana) ghi nhật ký tập trung tất cả các thông báo từ tất cả các thành phần.

## 1.4 Giá Trị Thực Tiễn

### 1.4.1 Tối Ưu Hóa Quy Trình

**Cải Thiện Tốc Độ Xử Lý**

Trước khi triển khai hệ thống, khi một quản lý bệnh viện cần câu trả lời cho một câu hỏi, quy trình có thể mất 3 đến 4 ngày: ngày thứ nhất gửi yêu cầu, ngày thứ hai đến thứ ba nhân viên phân tích viết và xem xét truy vấn, ngày thứ tư kết quả được trả về. Sau khi triển khai hệ thống, quá trình tương tự chỉ mất dưới 5 giây. Mức độ cải thiện này là khoảng 50.000 lần nhanh hơn.

**Khả Năng Tự Phục Vụ Tăng Lên**

Trước đây, nhân viên không chuyên về công nghệ thông tin phải phụ thuộc vào nhân viên phân tích, những người chỉ khả dụng trong giờ làm việc từ 8 đến 17. Bây giờ, hệ thống có sẵn 24/7, nhân viên có thể đặt câu hỏi bằng ngôn ngữ tự nhiên mà không cần kiến thức kỹ thuật.

**Độ Chính Xác Kết Quả Tăng Lên**

Trước đây, viết truy vấn thủ công có thể dẫn đến các lỗi như lỗi gõ, hiểu lầm yêu cầu, hoặc sao chép sai. Bây giờ, hệ thống sử dụng các mô hình ngôn ngữ để hiểu ý định một cách chính xác, tạo ra các truy vấn được xác thực, và kết quả được kiểm tra với dữ liệu thực tế.

### 1.4.2 Khám Phá Thông Tin Kinh Doanh Mới

**Phát Hiện Mẫu từ Đánh Giá Bệnh Nhân**

Trong quá khứ, các bình luận và đánh giá của bệnh nhân nằm rải rác ở nhiều nơi và không thể tổng hợp. Phân tích thủ công hàng trăm bình luận rất tốn thời gian. Bây giờ, hệ thống có thể trả lời "Bệnh nhân nói gì về nhân viên?" bằng cách tự động tóm tắt hơn 500 bình luận, xác định các mẫu tích cực và tiêu cực, và theo dõi xu hướng theo thời gian. Ví dụ, hệ thống có thể phát hiện "65% bệnh nhân phàn nàn về thời gian chờ tại bệnh viện A" hoặc "Bác sĩ mới John Smith nhận được các bình luận xuất sắc" hoặc "Các phàn nàn về quy trình hành chính tăng 30% tháng này".

**Phân Tích Xu Hướng**

Hệ thống có thể trả lời các câu hỏi như "Số lượng khám bệnh bảo hiểm Medicaid tại California tăng hay giảm bao nhiêu từ 2022 đến 2024?" bằng cách truy vấn tự động vào cơ sở dữ liệu đồ thị, nhận kết quả như tăng 15%, và cung cấp thông tin chi tiết về nguyên nhân có thể như kế hoạch bảo hiểm mới hoặc cơ sở mới.

**Mối Liên Hệ Giữa Các Miền Khác Nhau**

Hệ thống có thể trả lời các câu hỏi phức tạp như "Bệnh viện nào có mối tương quan giữa thời gian chờ cao nhưng đánh giá tốt?" bằng cách kết hợp dữ liệu hoạt động, cảm xúc bệnh nhân từ đánh giá, và chỉ số chất lượng nhân viên, cung cấp kết quả có thể hành động như "Bệnh viện X: thời gian chờ dài nhưng chăm sóc xuất sắc", cho phép tăng cường nhân sự để giảm thời gian chờ.

### 1.4.3 Mở Rộng Khả Năng

**Hỗ Trợ Chẩn Đoán Tâm Thần**

Hiện tại, các nguồn lực chẩn đoán tâm thần hạn chế và thông tin có thể không được chuẩn hóa. Hệ thống bổ sung cơ sở dữ liệu tiêu chuẩn chẩn đoán tâm thần, cho phép các truy vấn như "Tiêu chuẩn chẩn đoán tâm thần cho trầm cảm?" nhận được câu trả lời tức thì và chính xác. Hệ thống cũng có thể giải thích sự khác biệt giữa rối loạn lo âu và rối loạn hoảng sợ, hoặc đề xuất liệu pháp cho rối loạn căng thẳng sau chấn thương.

**Tích Hợp Đa Nguồn**

Cách tiếp cận truyền thống yêu cầu nhân viên tra cứu từng hệ thống riêng biệt: kiểm tra hệ thống hồ sơ y tế điện tử để truy vấn 1, kiểm tra hệ thống thanh toán cho truy vấn 2, tìm kiếm đánh giá cho truy vấn 3, sau đó kết hợp thủ công. Một truy vấn duy nhất như "Hiển thị những bệnh viện có chi phí thanh toán Medicaid cao nhưng đánh giá tiêu cực" có thể được trả lời tức thì bằng cách kết hợp tất cả các nguồn trong một truy vấn duy nhất.

**Giao Diện Ngôn Ngữ Tự Nhiên**

Trước khi công nghệ hiện đại phát triển, chỉ những người biết ngôn ngữ bảng tính có thể phân tích dữ liệu. Trước khi hệ thống trò chuyện ra đời, chỉ những người biết SQL mới có thể truy vấn cơ sở dữ liệu. Bây giờ, bất kỳ ai cũng có thể đặt câu hỏi: bác sĩ hỏi "Có bao nhiêu ca viêm phổi tháng vừa rồi?", quản lý hỏi "Đơn vị nào có lợi nhuận cao nhất?", nhân viên tài chính hỏi "Xu hướng thanh toán của chúng tôi như thế nào?", bệnh nhân hỏi "Bệnh viện nào có đánh giá tốt nhất?". Mọi người đều trở thành nhà phân tích dữ liệu.

### 1.4.4 Lợi Ích Kinh Tế

**Tác Động Tài Chính**

Các khoản tiết kiệm chi phí bao gồm: giảm thời gian nhân viên phân tích bằng cách giải phóng 2 nhân viên từ tổng số 10, mỗi nhân viên tiết kiệm 20% thời gian, tương đương tiết kiệm 200.000 đô la mỗi năm, sau khi trừ chi phí vận hành là 100.000 đô la. Quyết định được cải thiện nhanh hơn nhờ dữ liệu dẫn đến tránh được các quyết định sai lầm, ước tính cải thiện 5% quyết định nhân lên là 500.000 đến 1.000.000 đô la mỗi năm cải thiện. Cải thiện hoạt động bệnh viện thông qua tối ưu hóa thời gian chờ và nhân sự dẫn đến cải thiện hiệu quả 10 đến 15%, tương đương 1 triệu đô la trở lên mỗi năm.

Chi phí phát triển ban đầu từ 100.000 đến 200.000 đô la, chi phí cơ sở hạ tầng mỗi năm 50.000 đô la, chi phí bảo trì mỗi năm 30.000 đô la. Tổng lợi ích hàng năm là 600.000 đến 1,5 triệu đô la, dẫn đến suất lợi nhuận đầu tư 6 đến 15 lần trong năm đầu tiên, 3 đến 5 lần cho các năm tiếp theo.

**Lợi Ích Phi Tài Chính**

Ngoài lợi ích tài chính, hệ thống cải thiện sự hài lòng của nhân viên bằng cách giảm công việc thủ công, cho phép đưa ra quyết định dựa trên dữ liệu thay vì trực giác, tăng tốc độ xác định vấn đề, hỗ trợ chăm sóc bệnh nhân dựa trên bằng chứng, cung cấp lợi thế cạnh tranh, và tạo nền tảng cho các sáng kiến trí tuệ nhân tạo và học máy trong tương lai.

## 1.5 Kết Luận Chương 1

Dự án này được hình thành từ những nhu cầu thực tiễn của ngành y tế: dữ liệu tăng đáng kể, quy trình xử lý chậm chạp, và thiếu khả năng tự phục vụ. Công nghệ mô hình ngôn ngữ lớn kết hợp với phương pháp tạo sinh tăng cường truy vấn cung cấp một giải pháp lý tưởng. Mục tiêu là phát triển một hệ thống trò chuyện sẵn sàng cho sản xuất hỗ trợ các truy vấn từ nhiều nguồn dữ liệu, với lợi ích được dự kiến là suất lợi nhuận đầu tư 6 đến 15 lần trong năm đầu tiên.

Chương tiếp theo sẽ trình bày chi tiết kiến trúc hệ thống, giải thích cách các thành phần tương tác với nhau để đạt được các mục tiêu đã đề ra.
