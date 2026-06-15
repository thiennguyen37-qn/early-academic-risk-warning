# Worklog — Week 3

## Mục tiêu tuần

Hoàn thiện EDA trên đặc trưng tĩnh và đặc trưng động, tái cấu trúc project, cập nhật `build_features.py` với các hàm fill-in và docstring, đồng thời thử nghiệm một số bước preprocessing và xây dựng baseline.

---

## Công việc đã thực hiện

### 1. Tái cấu trúc Project

- **`src/features/build_features.py`**: chuyển hàm `build_snapshot_dataset()` từ notebook sang module tái sử dụng được, import trong cả EDA lẫn các bước sau
- **`config.py`**: tách `STATIC_FEATURES` thành hai hằng số riêng biệt:
  - `DEMOGRAPHIC_COLS` — 6 cột nhân khẩu học: `gender`, `region`, `age_band`, `imd_band`, `highest_education`, `disability`
  - `BEHAVIORAL_STATIC_COLS` — 2 cột hành vi tĩnh: `num_of_prev_attempts`, `studied_credits`
 
- Dọn dẹp đường dẫn data, sửa lỗi `RAW_DIR` trong `setup_database.py`
- Loại module **GGG** khỏi dataset (`WHERE code_module != 'GGG'` trong query `studentInfo`): toàn bộ điểm của GGG phụ thuộc vào Exam cuối kỳ (ngoài cửa sổ dự đoán) nên không có bài nào có trọng số ý nghĩa trong [0, T]

---

### 2. EDA — Phân tích đặc trưng tĩnh

Tách thông tin tĩnh thành hai DataFrame phục vụ hai hướng phân tích khác nhau:

- **`unique_students`**: dedup theo `id_student`, chứa 6 cột nhân khẩu học — phân tích phân phối cá nhân sinh viên
- **`student_academic_profile`**: theo từng enrollment (`id_student`, `code_module`, `code_presentation`), chứa `num_of_prev_attempts`, `studied_credits`, `final_result` — phân tích tương quan với kết quả học tập

#### 2.1. Phân tích `imd_band`

| Phát hiện | Chi tiết |
|-----------|---------|
| Phân phối | Tập trung cao nhất ở band 30-40% (1,925 SV), giảm dần về hai phía → phần lớn SV thuộc khu vực thiếu thốn trung bình đến cao |
| Missing theo region | North Region: 64.86%; Ireland: 25.42% → cộng lại ~90.3% tổng số `?` |
| Missing theo education | Post Graduate Qualification có tỷ lệ `?` cao nhất (41.85%); No Formal quals: 9.38% |
| Mối quan hệ edu ↔ imd | Band thấp (0-10%, 10-20%) giảm dần từ trình độ thấp lên cao; band cao (80-100%) tăng ngược chiều; điểm giao nhau ở khoảng A Level or Equivalent |

#### 2.2. Phân tích `disability`

- 91.1% sinh viên không khai báo khuyết tật; 8.9% có khuyết tật
- Nghịch biến với `imd_band`: band thấp (0-40%) có tỷ lệ khuyết tật 11-13%; band cao (70-100%) chỉ 5-7% → khu vực thiếu thốn kinh tế hơn đi kèm tỷ lệ khuyết tật khai báo cao hơn

#### 2.3. Phân tích `num_of_prev_attempts` — tạo đặc trưng mới `is_retake_the_course`

- 86.5% học lần đầu; 13.5% đã từng học lại (giảm theo cấp số nhân: retake lần 1 = 10.8%, lần 2 = 2.1%, ≥ 3 < 0.5%)
- Tạo biến nhị phân `is_retake_the_course` (`1` nếu `num_of_prev_attempts > 0`) để đơn giản hoá phân tích
- Nhóm có khuyết tật retake cao hơn rõ rệt: 20.1% vs 12.9% → khuyết tật là yếu tố rủi ro học tập
- Nhóm retake đăng ký nhiều tín chỉ hơn: median 90 vs 60, mean 98.9 vs 77.8

#### 2.4. Phân tích theo nhãn mục tiêu (static features)

Tạo `analysis_df` = `student_academic_profile` merge với `unique_students` (đã encode `disability` → 0/1, tạo `is_U35`).

**Radar chart — profile theo nhóm kết quả:**

| Nhóm | Profile đặc trưng |
|------|-----------------|
| Pass | Thấp nhất ở mọi chỉ số: 9.7% retake, 78.2 tín chỉ, 7.4% khuyết tật |
| Fail | Cao nhất ở lịch sử học tập: 20.5% retake, `num_of_prev_attempts` = 0.27 — vòng lặp thất bại kéo dài |
| Withdrawn | Cao nhất ở `studied_credits` (87.0) và `disability` (13.6%) — bỏ học do quá tải và rào cản sức khoẻ |

→ Fail và Withdrawn có cơ chế rủi ro khác nhau: Fail liên quan đến khó khăn học thuật tích luỹ, Withdrawn liên quan đến quá tải khối lượng và yếu tố cá nhân.

---

### 3. EDA — Phân tích đặc trưng động

#### 3.1. Số sinh viên còn active theo mốc thời gian

- Số sinh viên giảm dần từ Day 30 đến Day 240; mức giảm lớn nhất xảy ra trong giai đoạn đầu khoá học
- Đây là hành vi Withdrawn — có thể capture được qua các đặc trưng tương tác sớm

#### 3.2. Ma trận tương quan (dynamic features)

- `total_clicks` ↔ `active_weeks` và `avg_weekly_clicks` có tương quan cao → giữ lại `active_weeks` và `avg_weekly_clicks` 
- `avg_score` ↔ `num_failed` tương quan âm mạnh, nhưng cả hai vẫn giữ lại vì `num_failed` capture tần suất thất bại, `avg_score` capture mức điểm trung bình
- Bubble chart `avg_score` vs `num_failed`: phần lớn sinh viên tập trung ở góc điểm cao / num_failed = 0, outliers rải rác

#### 3.3. Phân tích `avg_days_early` theo nhãn

- Boxplot theo `final_result`: nhóm Pass có `avg_days_early` dương (nộp trước hạn); Fail và Withdrawn có median âm hoặc gần 0, đồng thời phân tán rộng hơn → nộp trễ là tín hiệu rủi ro
- Nhóm Withdrawn thiếu nhiều giá trị nhất do không nộp bài

#### 3.4. Radar chart — dynamic features theo nhóm kết quả

- Pass dẫn đầu mọi chỉ số tương tác và assessment
- Withdrawn thấp nhất ở tất cả, đặc biệt `avg_score`, `num_submitted`, `active_weeks` — phù hợp với hành vi giảm tương tác trước khi bỏ học
- Fail ở giữa: tương tác VLE vừa phải nhưng điểm assessment thấp

---

### 4. Cập nhật `build_features.py`

Thêm hai hàm fill-in xử lý missing values cho đặc trưng động, tách khỏi notebook để tái sử dụng:

**`fill_in_weekly_clicks(df)`**
- Fill 0 cho `total_clicks`, `active_weeks`, `avg_weekly_clicks`
- Lý do: NaN nghĩa là sinh viên chưa tương tác VLE → số click thực sự là 0

**`fill_in_assessment(df, assessment)`**
- Tính `num_due` (số bài đến hạn tại mỗi mốc T) theo `(code_module, code_presentation, prediction_point)` — cần bảng `assessment` làm tham chiếu
- Fill 0 cho `num_submitted`, `num_failed`
- Tính `submission_rate = num_submitted / num_due` (NaN nếu `num_due = 0`)
- Tạo đặc trưng mới `no_submission_despite_due`: `1` nếu có bài đến hạn nhưng không nộp bài nào — capture trường hợp sinh viên đang bỏ bê hẳn
- Thêm docstring đầy đủ cho `build_snapshot_dataset()` mô tả logic từng bước

---

### 5. Hoàn thiện EDA notebook

- Lưu `train.parquet` và `test.parquet` vào `data/processed/` ở cuối notebook EDA để làm đầu vào cho bước tiếp theo
- Thêm mô tả văn bản cho từng biểu đồ (nhận xét bên dưới mỗi cell)
- Cập nhật README: phản ánh bài toán 3-class (Distinction được gộp vào Pass)

---

### 6. Cập nhật số liệu so với Week 2

Nguyên nhân thay đổi: loại module **GGG** khỏi dataset.

**Dataset & Train/Test Split:**

| Chỉ số | Week 2 | Week 3 |
|--------|--------|--------|
| Tổng số dòng (`final_df`) | 196.932 | 178.294 |
| Train — số sinh viên | 19.829 | 17.921 |
| Train — số dòng (snapshot) | 157.348 | 142.384 |
| Test — số sinh viên | 4.958 | 4.481 |
| Test — số dòng (snapshot) | 39.584 | 35.910 |

**Phân phối nhãn (trên toàn `final_df`):**

| Nhãn | Week 2 | Week 3 |
|------|--------|--------|
| Pass | 98.888 (50.2%) | 89.944 (50.4%) |
| Fail | 56.349 (28.6%) | 50.525 (28.3%) |
| Distinction | 24.192 (12.3%) | 21.024 (11.8%) |
| Withdrawn | 17.503 (8.9%) | 16.801 (9.4%) |

**Phân phối nhãn sau khi gộp Distinction → Pass:**

| Nhãn | Week 2 | Week 3 |
|------|--------|--------|
| Pass (bao gồm cả Distinction đã gộp) | 62.5% | 62.2% |
| Fail | 28.6% | 28.3% |
| Withdrawn | 8.9% | 9.4% |

**Missing values:**

| Feature | Week 2 | Week 3 |
|---------|--------|--------|
| `date_unregistration` | 91.49% | 90.98% |
| `avg_score` | 17.64% | 10.39% |
| `num_submitted`, `num_failed`, `avg_days_early` | ~10.29% | ~9.08% |
| VLE features | ~2% | ~1.70% |
| `imd_band` (train, row-level) | 3.78% | 4.20% |
| `imd_band` (train, theo khu vực — North Region) | 64.75% | 64.86% |
| `imd_band` (train, theo khu vực — Ireland) | 25.78% | 25.42% |

---

### 7. Thay đổi Feature Matrix so với Week 2

Feature matrix dùng để huấn luyện model (`X_train.parquet`) — **14 features**, so sánh với thiết kế ban đầu ở Week 2:

| Feature | Nhóm | Thay đổi |
|---------|------|----------|
| `imd_band` | Static — Demographic | Giữ |
| `highest_education` | Static — Demographic | Giữ |
| `disability` | Static — Demographic | Giữ |
| `num_of_prev_attempts` | Static — Behavioral | Giữ |
| `studied_credits` | Static — Behavioral | Giữ |
| `active_weeks` | Dynamic — VLE | Giữ |
| `avg_weekly_clicks` | Dynamic — VLE | Giữ |
| `num_submitted` | Dynamic — Assessment | Giữ |
| `avg_score` | Dynamic — Assessment | Giữ |
| `submission_rate` | Dynamic — Assessment | Giữ |
| `num_failed` | Dynamic — Assessment | Giữ |
| `avg_days_early` | Dynamic — Assessment | Giữ |
| `num_due` | Dynamic — Assessment | **Thêm mới** — số bài đến hạn tại T, cần thiết để tính `submission_rate` đúng |
| `no_submission_despite_due` | Dynamic — Assessment | **Thêm mới** — flag nhị phân: có bài đến hạn nhưng không nộp bài nào |
| ~~`gender`~~ | Static — Demographic | **Loại** — không đưa vào X (giữ trong parquet thô) |
| ~~`region`~~ | Static — Demographic | **Loại** — không đưa vào X |
| ~~`age_band`~~ | Static — Demographic | **Loại** — không đưa vào X |
| ~~`total_clicks`~~ | Dynamic — VLE | **Loại** — tương quan cao với `active_weeks` và `avg_weekly_clicks` |

---


