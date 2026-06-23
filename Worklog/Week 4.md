# Worklog — Week 4

## Mục tiêu tuần

Hoàn thiện bước preprocessing (kiểm định cơ chế missing của `imd_band` và imputation theo phân phối), chốt feature matrix cuối cùng, và bước vào giai đoạn modeling: xây dựng baseline, train model 3-class và binary với SMOTE + Bayesian Optimization, phân tích feature importance, so sánh nhiều thuật toán và giải thích model bằng SHAP.

---

## Công việc đã thực hiện

### 1. Preprocessing — Kiểm định cơ chế missing của `imd_band`

Trước khi impute `imd_band = '?'`, thực hiện kiểm định thống kê để xác định cơ chế missing (MCAR / MAR / MNAR), tránh impute sai gây bias.

**Thiết kế test:** dùng snapshot tĩnh (dedup theo `id_student, code_module, code_presentation` vì `imd_band` không đổi theo thời gian) — 817 / 19.988 sinh viên thiếu (4.09%).

**[MCAR proxy] Mann-Whitney U trên biến số:**

| Biến | p-value | Kết luận |
|------|---------|----------|
| `num_of_prev_attempts` | 0.0003 | ❌ Không MCAR |
| `studied_credits` | 0.0031 | ❌ Không MCAR |

**[MAR] Chi-square + Cramér's V trên biến categorical:**

| Biến | p-value | Cramér's V | Kết luận |
|------|---------|------------|----------|
| `region` | 0.0 | 0.5768 | ❌ MAR (mạnh nhất) |
| `highest_education` | 0.0 | 0.2143 | ❌ MAR |
| `code_module` | 0.0 | 0.1011 | ❌ MAR |
| `final_result` | 0.0 | 0.0690 | ❌ MAR |
| `gender` | 0.0 | 0.0652 | ❌ MAR |
| `disability` | 0.0 | 0.0439 | ❌ MAR |

**Kết luận:** Cả 2 biến số bác bỏ MCAR; cả 6 biến categorical đều liên quan tới missingness (mạnh nhất là `region`, V = 0.5768) → cơ chế là **MAR**. Quyết định: **impute theo phân phối `imd_band` của từng region** (fit trên train) + thêm indicator `imd_missing`.

---

### 2. Refactor imputation — output cột `_filled` thay vì mutate gốc

Tái cấu trúc các hàm fill-in trong `build_features.py` để **không ghi đè cột gốc**, giúp giữ được giá trị thô để đối chiếu và tránh tác dụng phụ:

- **`fill_in_weekly_clicks(df)`** → tạo `total_clicks_filled`, `active_weeks_filled`, `avg_weekly_clicks_filled` (fill 0)
- **`fill_in_assessment(df, assessment)`** → tạo `num_due`, `num_submitted_filled`, `num_failed_filled`, `no_submission_despite_due` (tính lại `num_due` theo `assessment` ở mỗi mốc T)
- **`fit_imd_distributions(train_df)`** → học phân phối `imd_band` theo từng region từ train (kèm phân phối `__overall__` để fallback)
- **`transform_imd_imputation(df, distributions, rng)`** → impute `imd_band_filled` bằng cách **bốc ngẫu nhiên theo phân phối region** (dùng `RANDOM_SEED` để reproducible); impute **1 lần per student** rồi broadcast về mọi snapshot để tránh cùng sinh viên nhận giá trị khác nhau ở các mốc khác nhau

Hai cột xử lý riêng trong notebook:
- `avg_score_filled` = `avg_score.fillna(-1)` — dùng **sentinel -1** (ngoài range [0,100]) để phân biệt với điểm 0 thực
- `avg_days_early_filled` = `avg_days_early.fillna(0)` — trường hợp không nộp đã được `no_submission_despite_due` capture

Sau impute: `imd_band_filled` không còn giá trị `'?'` ở cả train lẫn test (0 còn lại).

---

### 3. Encode & chốt Feature Matrix cuối cùng

**Encoding:**

| Feature | Kiểu | Mapping |
|---|---|---|
| `disability` | Binary | `Y→1, N→0` (`DISAB_MAP`) |
| `highest_education` | Ordinal | theo bậc học (`EDU_ORDER`) |
| `imd_band_filled` | Ordinal | theo mức độ nghèo (`IMD_ORDER`) |
| `final_result` (target) | Label | `{Fail: 0, Pass: 1, Withdrawn: 2}` |

`gender`, `region`, `age_band`, `imd_band` (gốc) bị loại khỏi X (`DROP_COLS`); `prediction_point` lưu riêng vào `train_meta.parquet` / `test_meta.parquet` để modeling tách dữ liệu theo từng mốc.

**Feature matrix: 15 features** (`X_train`: 142.384 × 15, `X_test`: 35.910 × 15, **0 NaN**):

```
highest_education, disability, num_of_prev_attempts, studied_credits,
total_clicks_filled, active_weeks_filled, avg_weekly_clicks_filled,
num_due, num_submitted_filled, avg_score_filled, num_failed_filled,
avg_days_early_filled, no_submission_despite_due, imd_band_filled, imd_missing
```

**Thay đổi so với feature matrix Week 3 (14 features):**

| Thay đổi | Chi tiết |
|---|---|
| **Thêm `imd_missing`** | Indicator nhị phân từ phân tích MAR — giữ lại tín hiệu missingness sau khi impute |
| **Thêm `total_clicks_filled`** | Đưa trở lại tổng click (Week 3 đã loại `total_clicks`) dưới dạng cột `_filled` |
| **Refactor `_filled`** | Toàn bộ dynamic features chuyển sang hậu tố `_filled`; `imd_band → imd_band_filled` |
| **Loại `submission_rate`** | Bỏ khỏi X (giữ `num_due` để diễn giải khối lượng bài đến hạn) |

**Phân phối nhãn (snapshot-level):**

| Nhãn | Train | Test |
|------|-------|------|
| Fail (0) | 40.333 | 10.192 |
| Pass (1) | 88.536 | 22.432 |
| Withdrawn (2) | 13.515 | 3.286 |

---

### 4. Baseline — HistGradientBoosting (3-class)

Xây dựng baseline tối giản làm mốc so sánh (`baseline.ipynb`):

- Giữ nguyên 3 lớp **Fail / Pass / Withdrawn**
- **Không** SMOTE, class weight, hyperparameter tuning hay scaling — chỉ `HistGradientBoostingClassifier` mặc định
- Train **1 model riêng cho mỗi mốc** trong 8 prediction points (30 → 240 ngày)
- Đánh giá: classification report, confusion matrix, ROC-AUC macro (one-vs-rest) theo từng mốc

---

### 5. Modeling — 3-class (SMOTE + Bayesian Optimization)

`modeling.ipynb` — train HistGradientBoosting có xử lý mất cân bằng, cho cả 8 mốc thời gian:

- **SMOTE** oversample Fail và Withdrawn với tỷ lệ `(1 + x)·N`, `x ∈ [0.1, 0.9]`
- **Optuna (30 trials)** tune đồng thời: hyperparameter model + SMOTE ratio (Fail/Withdrawn riêng) + class weight (`w_fail ∈ [1,5]`, `w_withdrawn ∈ [1,8]`)
- **Metric tối ưu:** F2-macro trên 2 lớp at-risk (β=2, ưu tiên recall) qua StratifiedKFold 3-fold
- Lưu metrics theo mốc (recall/precision/F2 từng lớp) và **permutation importance**

### 6. Modeling — Binary At-risk (SMOTE + Bayesian Optimization)

`modeling_2label.ipynb` — gộp **Fail + Withdrawn → At-risk (1)**, Pass → 0:

- Cùng pipeline SMOTE + Optuna, nhưng **tối ưu F1 At-risk** thay vì F2
- Lý do đổi metric: tối ưu thuần recall khiến model dự đoán toàn bộ về At-risk (recall=1, precision rất thấp); F1 cân bằng precision/recall

### 7. Feature Importance — Permutation Importance

- Tính permutation importance trên test set cho từng mốc, dùng chính F2/F1 At-risk làm scoring (đo đúng ảnh hưởng tới mục tiêu)
- Trực quan hoá bằng **bar chart ngang** (importance trung bình qua các mốc)
- **Nhóm feature hành vi học tập áp đảo:** `num_submitted_filled`, `active_weeks_filled`, `avg_score_filled`, `num_due`, `no_submission_despite_due` — các đặc trưng tương tác/assessment trong khoá quan trọng hơn hẳn nhóm nhân khẩu học tĩnh (`highest_education`, `num_of_prev_attempts`, `imd_*` gần như không đóng góp)

---

### 8. `modeling_snapshots_roc` — So sánh tập trung tại 3 mốc (90 / 180 / 240)

Notebook chạy lại cả pipeline 3-class lẫn binary nhưng **chỉ trên 3 mốc** (giảm thời gian, đủ đại diện early/mid/late), bổ sung phân tích **ROC-AUC**:

- **ROC 3-class** (one-vs-rest, 3 subplot Fail/Pass/Withdrawn): AUC Pass cao nhất; Fail tăng dần theo thời gian; Withdrawn yếu nhất ở giữa khoá
- **ROC binary** (1 biểu đồ): AUC tăng theo T (T=90 < 180 < 240) — hành vi sinh viên at-risk càng về cuối càng phân kỳ rõ; nhấn mạnh T=90 là mốc giá trị nhất cho **can thiệp sớm**

---

### 9. Thử nghiệm thuật toán khác + Explainable AI (@ T=180)

`testing_other_models_2_label.ipynb` — so sánh 4 thuật toán cho bài toán binary At-risk tại T=180:

**Fine-tune từng model bằng Optuna (30 trials, tối ưu F1 At-risk, SMOTE + class_weight; chỉ Logistic Regression được scale):**

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|-------|----------|-----------|--------|------|---------|
| **LightGBM** | 0.8686 | 0.8076 | 0.7973 | **0.8024** | 0.9292 |
| CatBoost | 0.8728 | 0.8464 | 0.7576 | 0.7996 | 0.9304 |
| Random Forest | 0.8681 | 0.8251 | 0.7690 | 0.7960 | 0.9248 |
| Logistic Regression | 0.8451 | 0.7533 | 0.7987 | 0.7754 | 0.9163 |

→ **LightGBM** tốt nhất theo F1 At-risk (0.8024).

**Stability check (cắt feature):** train lại cả 4 model trên **Top-10** và **Top-5** feature (chọn theo `mean_rank` của native importance), so sánh Full(15) → Top-10 → Top-5 để kiểm tra độ ổn định khi giảm feature.

**SHAP — Explainable AI** trên model tốt nhất:
- **Beeswarm** + **bar** (mean|SHAP|) cho cả 3 bộ feature — xác định feature nào đẩy dự đoán về At-risk
- **Waterfall** giải thích cục bộ 2 ca cụ thể (1 sinh viên bị đẩy mạnh về At-risk, 1 về Pass)

---

### 10. Cập nhật hạ tầng

- Thêm dependency: `optuna` (Bayesian optimization), `catboost`, `lightgbm`, `shap`
- Bổ sung `catboost_info/` vào `.gitignore`

---

## Tổng kết tuần

- Chốt được feature matrix cuối cùng **15 features, 0 NaN**, với imputation `imd_band` có cơ sở thống kê (MAR → impute theo region + indicator)
- Hoàn thành toàn bộ chuỗi modeling: baseline → 3-class & binary (SMOTE + Optuna) → so sánh 4 thuật toán → SHAP
- **Model tốt nhất:** LightGBM cho bài toán binary At-risk tại T=180 (F1 = 0.8024, ROC-AUC = 0.9292)
- **Nhận định chính:** nhóm đặc trưng hành vi trong khoá (số bài nộp, tuần hoạt động, điểm trung bình, bài đến hạn) là yếu tố dự báo rủi ro mạnh nhất; mốc T=90 có giá trị thực tiễn cao nhất cho can thiệp sớm
