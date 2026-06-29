# Worklog — Week 5

## Mục tiêu tuần

Củng cố project sau giai đoạn modeling: dọn dẹp hạ tầng, chuẩn hoá dependencies, thêm script tái lập model production, rerun lại các notebook theo thứ tự sạch, và hoàn thiện tài liệu (README, cấu trúc project).

---

## Công việc đã thực hiện

### 1. Dọn dẹp dependencies

- **Loại `mlxtend` và `ipynb`** khỏi `requirements.txt` — cả hai package đều không được import ở bất kỳ notebook hoặc module `src` nào; loại bỏ để tránh cài thừa
- **Thêm `scipy` và `joblib`** vào `requirements.txt` dưới dạng explicit dependency — hai package này đã được sử dụng trực tiếp (scipy cho Mann-Whitney / Chi-square, joblib cho serialize artifact) nhưng trước đây chỉ là transitive dependency, không được khai báo rõ

---

### 2. Sửa lỗi tham chiếu notebook

- **`notebooks/preprocessing.ipynb`**: sửa tham chiếu stale từ `demo.ipynb` sang `EDA.ipynb` — đầu vào thực tế (`train.parquet`, `test.parquet`) được sinh bởi `EDA.ipynb`, không phải `demo.ipynb` (đã xoá)

---

### 3. Đổi tên notebook `aggregate_data` → `modeling_snapshots_roc`

Notebook này không thực hiện tổng hợp dữ liệu; nội dung là chạy lại pipeline 3-class và binary tại 3 mốc (T = 90 / 180 / 240) kèm phân tích ROC-AUC. Đổi tên để phản ánh đúng nội dung:

- `notebooks/aggregate_data.ipynb` → `notebooks/modeling_snapshots_roc.ipynb`
- Cập nhật reference trong `worklog/Week 4.md`

---

### 4. Sửa `.gitignore` — neo rule `models/` vào thư mục gốc

Pattern `models/` (không neo) cũng khớp với `src/models/`, khiến source code trong `src/models/` bị shadow bởi gitignore. Sửa thành `/models/` để chỉ ignore thư mục artifacts cấp cao nhất:

```gitignore
# trước
models/

# sau
/models/
```

---

### 5. Thêm script tái lập model tốt nhất — `src/models/train_best_model.py`

Script độc lập, tái lập đúng nhánh LightGBM trong `testing_other_models_2_label.ipynb` và serialize artifact ra `models/best_lgbm_t180.joblib`.

**Chi tiết:**

- Tái lập pipeline: **Optuna 30 trials + SMOTE + class_weight**, tối ưu F1 At-risk qua 3-fold StratifiedKFold
- Prediction point: **T = 180**; nhãn binary Fail + Withdrawn → At-risk (1), Pass → 0
- Mọi thành phần ngẫu nhiên cố định theo `RANDOM_SEED` → kết quả trùng với notebook (F1 At-risk ≈ 0.8024)
- Artifact `models/best_lgbm_t180.joblib` là dict chứa: model, feature names, prediction_point, label_map, best_params, test_metrics
- Artifact nằm trong `/models/` (gitignored, sinh lại được)

**Chạy:**

```bash
python -m src.models.train_best_model
```

---

### 6. Rerun EDA notebook theo thứ tự sạch

`notebooks/EDA.ipynb` trước đây có cell execution count không theo thứ tự (đếm đến 75 cho 60 cells — bằng chứng notebook đã được chạy chắp vá). Rerun toàn bộ bằng Restart & Run All:

- Các output được tái tạo theo thứ tự tuần tự từ 1 đến hết
- `train.parquet` / `test.parquet` sinh ra bit-identical với trước (split deterministic theo `RANDOM_SEED`) → các notebook downstream không bị ảnh hưởng

---

### 7. Rerun `testing_other_models_2_label.ipynb`

Chạy lại notebook so sánh 4 thuật toán + SHAP để đảm bảo output hiện tại khớp với code, không còn stale output từ các lần chạy lẻ tẻ trước.

---

### 8. Hoàn thiện README

Viết lại và bổ sung README với đầy đủ các mục cần thiết để người mới có thể hiểu và tái lập project:

| Mục | Nội dung |
|-----|----------|
| **Background** | Bối cảnh bài toán learning analytics, giới thiệu dataset OULAD |
| **Problem Definition** | Bài toán 3-class (Pass / Fail / Withdrawn), 8 mốc dự đoán, tiêu chí đánh giá ưu tiên recall |
| **Research Gap** | Khoảng trống nghiên cứu so với các công trình hiện có trên OULAD |
| **Proposed Approach** | Feature engineering theo thời gian, 3-class + binary, XAI |
| **Objectives** | Mục tiêu cụ thể của project |
| **Dataset** | Bảng mô tả 7 file CSV của OULAD (kích thước, nội dung) |
| **Project Structure** | Cây thư mục có chú thích từng file/folder |
| **How to Run** | Hướng dẫn cài đặt môi trường → chuẩn bị dữ liệu → chạy pipeline (6 bước theo thứ tự) → train best model |

---

## Tổng kết tuần

- Project được dọn dẹp và chuẩn hoá: dependencies gọn hơn, notebook reference đúng, gitignore không còn shadow source code
- Thêm `train_best_model.py` để tái lập model production LightGBM một lệnh, không cần mở notebook
- README đủ để người ngoài có thể hiểu bài toán và tái chạy toàn bộ pipeline từ đầu
- Mọi notebook đã có output sạch theo thứ tự tuần tự
