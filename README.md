# Early Academic Risk Warning

## Background

Sự phát triển mạnh mẽ của hình thức học trực tuyến và học kết hợp (blended learning) đã tạo ra lượng lớn dữ liệu về hành vi học tập của sinh viên. Điều này mở ra cơ hội ứng dụng các phương pháp học máy và phân tích dữ liệu nhằm hỗ trợ quá trình ra quyết định trong giáo dục. Trong đó, việc phát hiện sớm sinh viên có nguy cơ trượt môn hoặc bỏ học là một bài toán quan trọng, giúp giảng viên và cố vấn học tập có thể đưa ra các biện pháp can thiệp kịp thời trước khi kết quả học tập trở nên khó cải thiện.

Project này sử dụng bộ dữ liệu **OULAD (Open University Learning Analytics Dataset)** — một bộ dữ liệu công khai nổi tiếng trong lĩnh vực learning analytics. Bộ dữ liệu bao gồm thông tin nhân khẩu học, lịch sử tương tác của sinh viên với môi trường học tập ảo (Virtual Learning Environment - VLE), cùng kết quả đánh giá học tập của 32.593 sinh viên thuộc 22 khóa học khác nhau. OULAD là nền tảng phù hợp để xây dựng các mô hình cảnh báo sớm rủi ro học tập và phân tích các yếu tố ảnh hưởng đến kết quả học tập của sinh viên.


---

## Problem Definition

Bài toán được xây dựng dưới dạng **phân loại 3 nhãn**, trong đó biến mục tiêu là `final_result` ∈ {Pass, Fail, Withdrawn}. Nhãn gốc Distinction (hoàn thành xuất sắc) được gộp vào Pass, vì cả hai đều thuộc nhóm hoàn thành khoá học và không cần can thiệp.

| Nhãn | Ý nghĩa |
|------|---------|
| Pass | Hoàn thành khoá học đạt yêu cầu (bao gồm cả Distinction) |
| Fail | Hoàn thành khoá học nhưng không đạt |
| Withdrawn | Bỏ học giữa chừng |

Sinh viên thuộc nhóm **Fail** hoặc **Withdrawn** được xem là *có rủi ro*, do đó **Recall** cho hai nhãn này là tiêu chí đánh giá ưu tiên — bỏ sót một sinh viên có rủi ro tốn kém hơn nhiều so với cảnh báo nhầm.

Dự đoán được thực hiện tại **8 mốc thời gian**: ngày **30, 60, 90, 120, 150, 180, 210, 240** của khoá học, chỉ sử dụng dữ liệu có sẵn đến thời điểm đó. Sinh viên đã bỏ học trước mỗi mốc dự đoán sẽ bị loại khỏi tập dữ liệu tại mốc đó, đảm bảo model chỉ hoạt động trên những sinh viên đang còn học.

---

## Research Gap

Các nghiên cứu hiện có trên OULAD chủ yếu giải quyết bài toán **phân loại nhị phân** (bỏ học / không bỏ học, đậu / trượt), ít nghiên cứu phân biệt hai nhóm rủi ro **Fail** và **Withdrawn** — vốn có cơ chế khác nhau và đòi hỏi biện pháp can thiệp khác nhau. Dự đoán theo thời gian tại nhiều mốc kiểm tra vẫn chưa được khai thác triệt để. Ngoài ra, việc áp dụng **XAI (Explainable AI)** để làm cho kết quả dự đoán có thể giải thích được vẫn còn rất hạn chế. 

---

## Proposed Approach

Dự án xây dựng một pipeline dự đoán theo thời gian, có khả năng giải thích, bao gồm:

1. **Feature Engineering theo thời gian**: xây dựng feature tại mỗi mốc từ cả ba nhóm — nhân khẩu học, hành vi tương tác VLE tích luỹ, và hành vi nộp bài kiểm tra
2. **Mô hình phân loại 3 nhãn**: tối ưu hoá recall cho nhãn Fail và Withdrawn, kết hợp xử lý mất cân bằng nhãn (class imbalance)
3. **Giải thích kết quả (XAI)**: cung cấp lý do dự đoán theo từng sinh viên, phù hợp để cố vấn học tập hành động

---

## Objectives

- Dự đoán kết quả học tập theo 3 nhãn (Pass / Fail / Withdrawn) tại 8 mốc ngày 30, 60, 90, 120, 150, 180, 210, 240
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

---

## Project Structure

```
early-academic-risk-warning/
├── config.py                       # Hằng số tập trung: paths, snapshots, features, seed
├── requirements.txt
├── data/
│   ├── raw/                        # 7 file CSV gốc của OULAD (không commit)
│   ├── oulad.db                    # SQLite sinh từ raw (không commit)
│   └── processed/                  # train/test + X/y parquet (không commit, sinh lại được)
├── src/
│   ├── database/setup_database.py  # Nạp 7 CSV vào SQLite
│   ├── features/build_features.py  # Snapshot dataset + hàm fill-in / imputation
│   └── models/train_best_model.py  # Train & lưu model tốt nhất (LightGBM @ T=180)
├── notebooks/
│   ├── EDA.ipynb                       # EDA + dựng temporal dataset → train/test.parquet
│   ├── preprocessing.ipynb             # Imputation + encoding → X/y parquet (15 features)
│   ├── baseline.ipynb                  # Baseline HistGB 3-class (8 mốc)
│   ├── modeling.ipynb                  # 3-class: SMOTE + Optuna 
│   ├── modeling_2label.ipynb           # Binary At-risk: SMOTE + Optuna
│   ├── modeling_snapshots_roc.ipynb    # 3-class + binary tại 3 mốc + ROC-AUC
│   └── testing_other_models_2_label.ipynb  # So sánh 4 thuật toán + SHAP (@ T=180)
├── models/                         # Artifact đã train (không commit, sinh lại được)
├── docs/                           # Data Overview + papers tham khảo
└── worklog/                        # Nhật ký công việc theo tuần
```

---

## How to Run

**1. Cài đặt môi trường**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Chuẩn bị dữ liệu** — đặt 7 file CSV của OULAD vào `data/raw/`, rồi nạp vào SQLite:

```bash
python -m src.database.setup_database
```

**3. Chạy pipeline** (theo thứ tự, mỗi notebook sinh đầu vào cho bước sau):

| Bước | Notebook | Đầu ra |
|------|----------|--------|
| 1 | `notebooks/EDA.ipynb` | `data/processed/train.parquet`, `test.parquet` |
| 2 | `notebooks/preprocessing.ipynb` | `X_train`, `X_test`, `y_train`, `y_test`, `*_meta` parquet |
| 3 | `notebooks/baseline.ipynb` | Baseline 3-class để đối chiếu |
| 4 | `notebooks/modeling.ipynb` / `modeling_2label.ipynb` | Model 3-class / binary (8 mốc) |
| 5 | `notebooks/modeling_snapshots_roc.ipynb` | So sánh 3 mốc + ROC-AUC |
| 6 | `notebooks/testing_other_models_2_label.ipynb` | So sánh 4 thuật toán + SHAP |

**4. (Tuỳ chọn) Train & lưu model tốt nhất** ra `models/best_lgbm_t180.joblib`:

```bash
python -m src.models.train_best_model
```

---
