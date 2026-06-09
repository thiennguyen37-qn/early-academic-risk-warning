# Worklog — Week 2

## Mục tiêu tuần

Thiết lập project infrastructure, thực hiện EDA trên các bảng dữ liệu (assessment, course, VLE), xử lý missing values, xây dựng temporal dataset và thực hiện train/test split.

---

## Công việc đã thực hiện

### 1. Project Setup

Tạo các file cấu hình và infrastructure ban đầu:

- **`config.py`** — định nghĩa tập trung các hằng số dùng trong toàn project:
  - Đường dẫn đến thư mục data và 7 file CSV gốc
  - Target column: `final_result`; 4 classes: `["Distinction", "Pass", "Fail", "Withdrawn"]`
  - At-risk classes: `["Fail", "Withdrawn"]`
  - Temporal snapshots (prediction points): `[30, 60, 90, 120, 150, 180, 210, 240]` ngày
  - Static features: 8 cột nhân khẩu học từ `studentInfo`

- **`setup_database.py`** — nạp toàn bộ 7 file CSV vào SQLite database (`oulad.db`), phục vụ truy vấn nhanh bằng SQL trong quá trình phân tích

- **`Data Overview.md`** — tài liệu hoá schema chi tiết của 7 bảng OULAD, thống kê quy mô dataset, phân phối nhãn và ghi chú missing values

> **Cập nhật so với Week 1:** Prediction points được mở rộng từ `[60, 120, 180, 240]` lên `[30, 60, 90, 120, 150, 180, 210, 240]` — dày hơn để theo dõi sự thay đổi rủi ro sớm hơn (từ ngày 30).

---

### 2. EDA — Assessment & Course

**Phân tích bảng `assessments` và `courses`:**

| Phát hiện | Chi tiết |
|-----------|---------|
| Tổng số bài kiểm tra | 206 assessments, gồm 3 loại: TMA, CMA, Exam |
| Anomaly trọng số — module GGG | Tất cả TMA/CMA có `weight = 0`; chỉ Exam có `weight = 100` → toàn bộ điểm nằm ở Exam |
| Anomaly trọng số — module CCC | Tổng weight = 300 do có 2 kỳ thi Exam trong một presentation |
| Missing deadline của Exam | 11 bản ghi Exam thiếu `date` (45.8% số Exam); tuy nhiên Exam nằm ngoài cửa sổ dự đoán (T ≤ 240) nên ảnh hưởng tối thiểu |

**Hướng xử lý:**
- Với module GGG: loại bỏ hoặc không dùng `weight` như feature vì không phản ánh contribution thực của từng bài
- Missing `date` của Exam: chấp nhận được vì các mốc dự đoán đều trước kỳ thi cuối kỳ

---

### 3. EDA — VLE (Virtual Learning Environment)

**Phân tích bảng `studentVle` (10.6M bản ghi):**

Sau khi aggregate theo tuần (`week = date // 7`) và `activity_type`:

| Thống kê | Giá trị |
|----------|---------|
| Số record sau aggregate | 627.031 |
| Trung bình click/tuần | 63.16 |
| Trung vị click/tuần | 30 |
| Độ lệch chuẩn | 96.59 |
| Max | 6.999 |
| Phân vị 90 (P90) | 159 |
| Phân vị 95 (P95) | 232 |
| Khoảng tuần | −4 đến 38 (âm = trước khi khoá bắt đầu) |

**Nhận xét:**
- Phân phối **lệch phải mạnh** (right-skewed): trung vị = 30 nhưng trung bình = 63, xuất hiện outliers đến 6.999
- Top 10% sinh viên tích cực hơn ~2.5× so với mức trung bình
- VLE interaction có từ tuần −4 (sinh viên truy cập tài nguyên trước khi khoá học chính thức bắt đầu)
- Cần cân nhắc log-transform hoặc capping khi engineering features

---

### 4. Xử lý Missing Values — `imd_band`

**Phát hiện:** `imd_band` trong `studentInfo` có giá trị `'?'` thay vì `NaN` — cần xử lý riêng.

| Thống kê | Giá trị |
|----------|---------|
| Tỷ lệ `'?'` trong train set | 3.78% |
| Tập trung theo khu vực | North Region: 64.75%; Ireland: 25.78% |

**Kết luận:** Missing có tính **hệ thống theo địa lý** (không phải ngẫu nhiên — MNAR), cần lưu ý khi impute để không tạo bias.

---

### 5. Xây dựng Temporal Dataset

**Hàm `build_snapshot_dataset()`** tạo dataset theo từng mốc thời gian T:

**Logic hoạt động:**
1. Với mỗi prediction point T ∈ [30, 60, 90, 120, 150, 180, 210, 240]:
   - Chỉ giữ sinh viên **còn đang học** tại T (chưa rút hoặc rút sau T)
   - Lọc dữ liệu VLE và Assessment trong cửa sổ `[0, T]`
2. Engineer dynamic features:

| Feature | Nguồn | Mô tả |
|---------|-------|-------|
| `total_clicks` | studentVle | Tổng click trong [0, T] |
| `active_weeks` | studentVle | Số tuần có ít nhất 1 click |
| `avg_weekly_clicks` | studentVle | Trung bình click/tuần |
| `num_submitted` | studentAssessment | Số bài đã nộp đến T |
| `avg_score` | studentAssessment | Điểm trung bình các bài đã nộp |
| `submission_rate` | studentAssessment | Tỷ lệ bài nộp đúng hạn / tổng bài đến hạn |
| `num_failed` | studentAssessment | Số bài có điểm < 40 |
| `avg_days_early` | studentAssessment | Trung bình số ngày nộp trước deadline |

3. Ghép với static features từ `studentInfo`
4. Gán nhãn `final_result` từ bảng gốc

**Kết quả:** Dataset gồm **196.932 dòng** (student–timepoint pairs)

---

### 6. Train/Test Split

**Chiến lược:** Split theo `id_student` (không phải theo dòng) để tránh data leakage giữa các mốc thời gian của cùng một sinh viên.

| Tập | Số sinh viên | Số dòng (snapshot) | Tỷ lệ |
|-----|-------------|-------------------|-------|
| Train | 19.829 | 157.348 | 80% |
| Test | 4.958 | 39.584 | 20% |

**Quyết định giảm nhãn: 4 → 3 classes**

Phân phối nhãn gốc trên toàn `final_df` (196.932 dòng):

| Nhãn | Số dòng | Tỷ lệ |
|------|---------|-------|
| Pass | 98.888 | 50.2% |
| Fail | 56.349 | 28.6% |
| Distinction | 24.192 | 12.3% |
| Withdrawn | 17.503 | 8.9% |

Quyết định: gộp `Distinction` vào `Pass` bằng `.replace("Distinction", "Pass")` — lý do: phân biệt "đạt yêu cầu" và "xuất sắc" không có giá trị thực tiễn trong bài toán early risk warning; việc can thiệp chỉ cần thiết cho nhóm at-risk (Fail, Withdrawn).

**Phân phối nhãn sau khi gộp:**

| Nhãn | Tỷ lệ |
|------|-------|
| Pass (incl. Distinction) | 62.5% |
| Fail | 28.6% |
| Withdrawn | 8.9% |

**Lưu ý:** Task chính thức là **3-class classification**. Class imbalance rõ ràng — cần xử lý ở bước tiếp theo (SMOTE, class weighting, v.v.)

---

## Tổng hợp Missing Values

| Feature | % Missing | Nguyên nhân |
|---------|-----------|-------------|
| `date_unregistration` | 91.49% | Hầu hết sinh viên hoàn thành khoá, không rút |
| `avg_score` | 17.64% | Sinh viên chưa nộp bài nào đến mốc T |
| `num_submitted`, `num_failed`, `submission_rate`, `avg_days_early` | ~10.29% | Chưa có assessment nào đến hạn tại T |
| VLE features (`total_clicks`, `active_weeks`, `avg_weekly_clicks`) | ~2% | Sinh viên chưa tương tác VLE |
| `imd_band` (train) | 3.78% | Hệ thống theo địa lý (MNAR) |

---

