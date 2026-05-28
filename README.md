# Cảnh Báo Rủi Ro Học Thuật Sớm

## Bối Cảnh

Sự phát triển của học trực tuyến và học kết hợp (blended learning) đã tạo ra khối lượng lớn dữ liệu hành vi học tập, mở ra cơ hội ứng dụng các phương pháp học máy để hỗ trợ ra quyết định trong giáo dục. Việc phát hiện sớm sinh viên có nguy cơ trượt môn hoặc bỏ học giúp giáo viên và cố vấn học thuật can thiệp kịp thời, trước khi kết quả trở nên không thể cứu vãn.

Dự án sử dụng bộ dữ liệu **OULAD (Open University Learning Analytics Dataset)** — một bộ dữ liệu công khai phong phú gồm thông tin nhân khẩu học, nhật ký tương tác với môi trường học tập ảo (VLE), và kết quả bài kiểm tra của **32.593 sinh viên** trên **22 khoá học**.

---

## Định Nghĩa Bài Toán

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

Các nghiên cứu hiện có trên OULAD chủ yếu giải quyết bài toán **phân loại nhị phân** (bỏ học / không bỏ học, đậu / trượt), ít nghiên cứu giữ nguyên cấu trúc 4 nhãn đầy đủ. Dự đoán theo thời gian tại nhiều mốc kiểm tra vẫn chưa được khai thác triệt để. Ngoài ra, việc áp dụng **XAI (Explainable AI)** để làm cho kết quả dự đoán có thể giải thích được cho các bên liên quan phi kỹ thuật như cố vấn học thuật vẫn còn rất hạn chế. Nhiều nghiên cứu cũng chỉ sử dụng một hoặc hai trong ba nhóm feature (nhân khẩu học, tương tác VLE, kết quả kiểm tra), chưa khai thác giá trị kết hợp của cả ba.

---

## Hướng Tiếp Cận

Dự án xây dựng một pipeline dự đoán theo thời gian, có khả năng giải thích, bao gồm:

1. **Feature Engineering theo thời gian**: xây dựng feature tại mỗi mốc từ cả ba nhóm — nhân khẩu học (tĩnh), hành vi tương tác VLE tích luỹ, và hành vi nộp bài kiểm tra
2. **Mô hình phân loại 4 nhãn**: tối ưu hoá recall cho nhãn Fail và Withdrawn, kết hợp xử lý mất cân bằng nhãn (class imbalance)
3. **Giải thích kết quả (XAI)**: cung cấp lý do dự đoán theo từng sinh viên, phù hợp để cố vấn học thuật hành động

---

## Mục Tiêu

- Dự đoán kết quả học tập theo 4 nhãn tại các mốc ngày 60, 120, 180, 240
- Đạt recall cao cho nhãn Fail và Withdrawn tại mỗi mốc thời gian
- Cung cấp kết quả dự đoán có thể giải thích được, phù hợp với nhu cầu của cố vấn học thuật

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
