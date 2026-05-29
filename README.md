# Early Academic Risk Warning

## Background

Sự phát triển mạnh mẽ của hình thức học trực tuyến và học kết hợp (blended learning) đã tạo ra lượng lớn dữ liệu về hành vi học tập của sinh viên. Điều này mở ra cơ hội ứng dụng các phương pháp học máy và phân tích dữ liệu nhằm hỗ trợ quá trình ra quyết định trong giáo dục. Trong đó, việc phát hiện sớm sinh viên có nguy cơ trượt môn hoặc bỏ học là một bài toán quan trọng, giúp giảng viên và cố vấn học tập có thể đưa ra các biện pháp can thiệp kịp thời trước khi kết quả học tập trở nên khó cải thiện.

Project này sử dụng bộ dữ liệu **OULAD (Open University Learning Analytics Dataset)** — một bộ dữ liệu công khai nổi tiếng trong lĩnh vực learning analytics. Bộ dữ liệu bao gồm thông tin nhân khẩu học, lịch sử tương tác của sinh viên với môi trường học tập ảo (Virtual Learning Environment - VLE), cùng kết quả đánh giá học tập của 32.593 sinh viên thuộc 22 khóa học khác nhau. OULAD là nền tảng phù hợp để xây dựng các mô hình cảnh báo sớm rủi ro học tập và phân tích các yếu tố ảnh hưởng đến kết quả học tập của sinh viên.


---

## Problem Definition

Bài toán được xây dựng dưới dạng **phân loại 4 nhãn**, trong đó biến mục tiêu là `final_result` ∈ {Distinction, Pass, Fail, Withdrawn}.

| Nhãn | Ý nghĩa |
|------|---------|
| Distinction | Hoàn thành khoá học với kết quả xuất sắc |
| Pass | Hoàn thành khoá học với kết quả đạt yêu cầu |
| Fail | Hoàn thành khoá học nhưng không đạt |
| Withdrawn | Bỏ học giữa chừng |

Sinh viên thuộc nhóm **Fail** hoặc **Withdrawn** được xem là *có rủi ro*, do đó **Recall** cho hai nhãn này là tiêu chí đánh giá ưu tiên — bỏ sót một sinh viên có rủi ro tốn kém hơn nhiều so với cảnh báo nhầm.

Dự đoán được thực hiện tại **4 mốc thời gian**: ngày **60, 120, 180, 240** của khoá học, chỉ sử dụng dữ liệu có sẵn đến thời điểm đó. Sinh viên đã bỏ học trước mỗi mốc dự đoán sẽ bị loại khỏi tập dữ liệu tại mốc đó, đảm bảo model chỉ hoạt động trên những sinh viên đang còn học.

---

## Research Gap

Các nghiên cứu hiện có trên OULAD chủ yếu giải quyết bài toán **phân loại nhị phân** (bỏ học / không bỏ học, đậu / trượt), ít nghiên cứu giữ nguyên cấu trúc 4 nhãn đầy đủ. Dự đoán theo thời gian tại nhiều mốc kiểm tra vẫn chưa được khai thác triệt để. Ngoài ra, việc áp dụng **XAI (Explainable AI)** để làm cho kết quả dự đoán có thể giải thích được vẫn còn rất hạn chế. Nhiều nghiên cứu cũng chỉ sử dụng một hoặc hai trong ba nhóm feature (nhân khẩu học, tương tác VLE, kết quả kiểm tra), chưa khai thác giá trị kết hợp của cả ba.

---

## Proposed Approach

Dự án xây dựng một pipeline dự đoán theo thời gian, có khả năng giải thích, bao gồm:

1. **Feature Engineering theo thời gian**: xây dựng feature tại mỗi mốc từ cả ba nhóm — nhân khẩu học, hành vi tương tác VLE tích luỹ, và hành vi nộp bài kiểm tra
2. **Mô hình phân loại 4 nhãn**: tối ưu hoá recall cho nhãn Fail và Withdrawn, kết hợp xử lý mất cân bằng nhãn (class imbalance)
3. **Giải thích kết quả (XAI)**: cung cấp lý do dự đoán theo từng sinh viên, phù hợp để cố vấn học tập hành động

---

## Objectives

- Dự đoán kết quả học tập theo 4 nhãn tại các mốc ngày 60, 120, 180, 240
- Đạt recall cao cho nhãn Fail và Withdrawn tại mỗi mốc thời gian
- Cung cấp kết quả dự đoán có thể giải thích được, phù hợp với nhu cầu của cố vấn học tập

---

## Dataset

| Bảng | Mô tả | Kích thước |
|------|-------|-----------|
| `studentInfo.csv` | Thông tin nhân khẩu học và kết quả cuối khoá | ~3.3 MB |
| `studentVle.csv` | Nhật ký tương tác VLE (10.6M lượt) | ~433 MB |
| `studentAssessment.csv` | Kết quả và thời gian nộp bài kiểm tra | ~5.4 MB |
| `studentRegistration.csv` | Ngày đăng ký và bỏ học | ~1.1 MB |
| `assessments.csv` | Thông tin các bài kiểm tra | ~8 KB |
| `vle.csv` | Danh sách tài nguyên học tập VLE | ~264 KB |
| `courses.csv` | Thông tin các khoá học | ~526 B |
