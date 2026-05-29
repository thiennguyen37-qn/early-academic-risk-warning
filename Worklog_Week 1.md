# Worklog — Week 1

## Mục tiêu tuần

Xác định bài toán, tìm kiếm dataset, research hướng thiết kế bài toán (problem statement, phục vụ business nào, xây dựng bài toán như thế nào, feature representation, literature review).

---

## Công việc đã thực hiện

### 1. Chọn Dataset

- Chọn **OULAD (Open University Learning Analytics Dataset)** do Open University UK công bố
- Dataset gồm 7 file CSV: `courses`, `assessments`, `vle`, `studentInfo`, `studentRegistration`, `studentAssessment`, `studentVle`
- Quy mô: 32.593 sinh viên, 22 khoá học, 10.6M lượt tương tác VLE

---

### 2. Xác định Bài Toán

**Task:** Multi-class classification — dự đoán `final_result` ∈ {Distinction, Pass, Fail, Withdrawn}

**Các quyết định thiết kế:**

| Quyết định | Lựa chọn | Lý do |
|-----------|---------|-------|
| Số lớp | 4 class (giữ nguyên) | Nuanced hơn binary, phù hợp cho advisor |
| At-risk | Fail + Withdrawn | Cả hai đều là kết quả tiêu cực cần can thiệp |
| Evaluation metric | Recall ưu tiên cho Fail + Withdrawn | Bỏ sót sinh viên có rủi ro tốn kém hơn cảnh báo nhầm |
| Approach | Temporal | Actionable — predict khi sinh viên còn đang học |
| Prediction points | Ngày 60, 120, 180, 240 | Mỗi 2 tháng, đủ thưa để thấy sự thay đổi rõ ràng |
| Output | Explainable (XAI) | Advisor cần hiểu lý do để can thiệp |

**Business context:** Hệ thống hỗ trợ **academic advisor / giáo viên** theo dõi sinh viên có nguy cơ, cập nhật mỗi 2 tháng, kèm giải thích lý do dự đoán.

---

### 3. Literature Review

Để xác định hướng tiếp cận phù hợp và tránh trùng lặp với các nghiên cứu hiện có, tuần này tập trung vào việc tổng quan tài liệu liên quan đến bài toán dự đoán kết quả học tập trên bộ dữ liệu OULAD. Ba nguồn tài liệu được chọn lọc, bao gồm một nghiên cứu thực nghiệm và hai bài tổng quan hệ thống, nhằm cung cấp cái nhìn toàn diện về các phương pháp, kết quả đạt được, cũng như những khoảng trống còn tồn tại trong lĩnh vực này.

| Tên paper (đầy đủ)                                                                                                         | Các tác giả                                                         | Năm xuất bản | Nội dung chính                                                                                                                                                                                                                                                                                                                              | Research Gap (Khoảng trống nghiên cứu)                                                                                                                                                                                                                                                                   |
| -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *OULAD MOOC Dropout and Result Prediction using Ensemble, Deep Learning and Regression Techniques*                         | Nikhil Indrashekhar Jha, Ioana Ghergulescu, Arghir-Nicolae Moldovan | 2019         | Nghiên cứu sử dụng các kỹ thuật Ensemble, Deep Learning và hồi quy để dự đoán tỷ lệ bỏ học và kết quả học tập trên bộ dữ liệu OULAD. Kết quả cho thấy các tương tác với môi trường học tập trực tuyến (VLE interactions) là yếu tố dự báo mạnh nhất đối với hiệu suất học tập và khả năng bỏ học của sinh viên.                             | Các nghiên cứu trước chưa điều tra đầy đủ quy trình tiền xử lý dữ liệu và trích xuất đặc trưng; chưa khai thác chi tiết điểm số bài kiểm tra; và thiếu các đặc trưng dựa trên thời gian nhằm phản ánh tiến trình học tập của sinh viên. |
| *Predictive Modelling with the Open University Learning Analytics Dataset (OULAD): A Systematic Literature Review*         | Lingxi Jin, Yao Wang, Huiying Song, Hyo-Jeong So                    | 2024         | Đây là một nghiên cứu tổng quan hệ thống về 17 bài báo sử dụng bộ dữ liệu OULAD. Nghiên cứu phân loại các mục tiêu dự báo thành ba nhóm chính: dự đoán kết quả học tập, xác định sinh viên có nguy cơ và phân tích mức độ gắn kết học tập (engagement).                                                                                     | Các nghiên cứu hiện tại còn ít tập trung vào khía cạnh “engagement”; nhiều mô hình thiếu khả năng giải thích và tính minh bạch; ngoài ra còn thiếu các thử nghiệm thực nghiệm trong môi trường giảng dạy thực tế để đánh giá hiệu quả triển khai của mô hình.                                            |
| *Predicting student performance: A comprehensive review of machine learning, deep learning, and explainable AI approaches* | Salma Boujmiraz, Hassane Darhmaoui, Ahmed Drissi el maliani         | 2026         | Bài báo thực hiện một Systematic Literature Review về các phương pháp Machine Learning, Deep Learning và Explainable AI (xAI) trong dự đoán kết quả học tập của sinh viên. Nghiên cứu nhấn mạnh vai trò của xAI trong việc nâng cao tính minh bạch và khả năng giải thích của mô hình nhằm hỗ trợ ra quyết định sư phạm hiệu quả hơn. | Chỉ khoảng 14% các nghiên cứu sử dụng mô hình “hộp đen” (blackbox) có áp dụng xAI; phần lớn nghiên cứu chỉ sử dụng các bộ dữ liệu đơn lẻ nên thiếu tính tổng quát; đồng thời còn thiếu sự liên kết giữa các mô hình dự đoán với đổi mới giáo dục và các lý thuyết sư phạm thực tiễn.                                |

Từ quá trình tổng quan trên, có thể thấy rằng khoảng trống rõ nhất nằm ở việc kết hợp giữa **độ chính xác kỹ thuật** và **tính giải thích sư phạm** — cụ thể là ứng dụng XAI kết hợp với các đặc trưng theo thời gian (temporal features). Đây cũng là định hướng chính cho thiết kế feature và mô hình trong các bước tiếp theo.

---

### 4. Feature Representation

Thiết kế 2 nhóm feature dựa trên các cột thực có trong dữ liệu gốc:

**Static** — lấy trực tiếp từ `studentInfo`, không thay đổi theo mốc thời gian T:

| Cột | Mô tả |
|-----|-------|
| `gender` | Giới tính |
| `region` | Khu vực địa lý |
| `highest_education` | Trình độ học vấn cao nhất khi vào học |
| `imd_band` | Chỉ số đa chiều về thiếu thốn (socioeconomic) |
| `age_band` | Nhóm tuổi |
| `num_of_prev_attempts` | Số lần học lại module này trước đây |
| `studied_credits` | Tổng tín chỉ đang theo học |
| `disability` | Có khai báo khuyết tật hay không |

**Dynamic** — trích xuất từ dữ liệu trong cửa sổ `[0, T]`, cần engineer từ raw data:

*VLE* (từ `studentVle` join `vle`):

| Cột gốc | Mô tả |
|---------|-------|
| `sum_click` | Số lần click vào từng `id_site` trong ngày `date` |
| `date` | Ngày tương tác (relative to presentation start) |
| `activity_type` | Loại tài nguyên (từ join với `vle`) |

*Assessment* (từ `studentAssessment` join `assessments`):

| Cột gốc | Mô tả |
|---------|-------|
| `score` | Điểm bài nộp (0–100; dưới 40 là Fail) |
| `date_submitted` | Ngày nộp bài (relative to presentation start) |
| `is_banked` | Kết quả được chuyển từ kỳ học trước |
| `date` | Deadline của bài (từ `assessments`) |
| `assessment_type` | Loại bài kiểm tra (từ `assessments`) |
| `weight` | Trọng số của bài trong tổng điểm (từ `assessments`) |

*Registration* (từ `studentRegistration`):

| Cột gốc | Mô tả |
|---------|-------|
| `date_registration` | Ngày đăng ký (âm = trước khi khoá học bắt đầu) |
| `date_unregistration` | Ngày rút khỏi khoá học (null nếu hoàn thành) |

---

### 5. Thiết kế End-to-End Workflow

```
Raw Data → EDA → Preprocessing → Temporal Dataset Construction
→ Class Imbalance Handling → Model Training → Evaluation → XAI
```
