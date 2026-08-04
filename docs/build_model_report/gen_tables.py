# -*- coding: utf-8 -*-
"""Sinh các bảng .tex (so sánh model, thứ hạng đặc trưng, siêu tham số) từ kết quả
thực nghiệm đã ghi nhận. Chạy: python gen_tables.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent

MODELS = ["Logistic Regression", "Random Forest", "CatBoost", "LightGBM"]

# --- Bảng so sánh model theo từng bộ đặc trưng: accuracy, precision, recall, f1, roc_auc ---
COMPARE = {
    "full": {
        "Logistic Regression": (0.8451, 0.7533, 0.7987, 0.7754, 0.9163),
        "Random Forest":       (0.8681, 0.8251, 0.7690, 0.7960, 0.9248),
        "CatBoost":            (0.8728, 0.8464, 0.7576, 0.7996, 0.9304),
        "LightGBM":            (0.8686, 0.8076, 0.7973, 0.8024, 0.9292),
    },
    "top10": {
        "Logistic Regression": (0.8536, 0.7873, 0.7711, 0.7791, 0.9157),
        "Random Forest":       (0.8631, 0.7966, 0.7938, 0.7952, 0.9260),
        "CatBoost":            (0.8614, 0.7762, 0.8235, 0.7992, 0.9303),
        "LightGBM":            (0.8655, 0.7972, 0.8023, 0.7997, 0.9304),
    },
    "top5": {
        "Logistic Regression": (0.8529, 0.7876, 0.7675, 0.7775, 0.9148),
        "Random Forest":       (0.8700, 0.8116, 0.7966, 0.8040, 0.9279),
        "CatBoost":            (0.8667, 0.7979, 0.8058, 0.8018, 0.9302),
        "LightGBM":            (0.8626, 0.7950, 0.7945, 0.7948, 0.9286),
    },
}
METRIC_HEADERS = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]

CAPTIONS = {
    "full":  (r"So sánh các mô hình trên bộ 15 đặc trưng đầy đủ (T=180). "
              r"Chỉ số Precision/Recall/F1 tính riêng cho lớp \textbf{At-risk}.",
              "tab:compare_full"),
    "top10": (r"So sánh các mô hình sau khi rút gọn về 10 đặc trưng quan trọng "
              r"nhất (Top-10).", "tab:compare_top10"),
    "top5":  (r"So sánh các mô hình sau khi rút gọn về 5 đặc trưng quan trọng "
              r"nhất (Top-5).", "tab:compare_top5"),
}


def make_compare_table(key):
    data = COMPARE[key]
    caption, label = CAPTIONS[key]
    # Giá trị lớn nhất mỗi cột -> in đậm (giống style_max trong thực nghiệm gốc)
    cols = list(zip(*data.values()))
    col_max = [max(c) for c in cols]

    rows = []
    for name in MODELS:
        vals = data[name]
        cells = []
        for v, vmax in zip(vals, col_max):
            s = f"{v:.4f}"
            cells.append(r"\textbf{%s}" % s if v == vmax else s)
        rows.append(r"    \textbf{%s} & %s \\" % (name, " & ".join(cells)))

    header = " & ".join(r"\textbf{%s}" % h for h in METRIC_HEADERS)
    lines = [
        r"\begin{table}[H]",
        r"  \centering",
        r"  \caption{%s}" % caption,
        r"  \label{%s}" % label,
        r"  \small",
        r"  \setlength{\tabcolsep}{5pt}",
        r"  \begin{tabular}{lrrrrr}",
        r"    \toprule",
        r"    \textbf{Model} & " + header + r" \\",
        r"    \midrule",
        "\n".join(rows),
        r"    \bottomrule",
        r"  \end{tabular}",
        r"\end{table}",
        "",
    ]
    return "\n".join(lines)


for key in ("full", "top10", "top5"):
    (OUT / f"table_compare_{key}.tex").write_text(make_compare_table(key), encoding="utf-8")

# --- Bảng thứ hạng đặc trưng (1 = quan trọng nhất) ---
RANKS = [
    ("num\\_submitted\\_filled",      1,  1,  1,  3,  1.50),
    ("avg\\_score\\_filled",          5,  2,  4,  1,  3.00),
    ("num\\_due",                     4,  7,  3,  7,  5.25),
    ("total\\_clicks\\_filled",       2,  4, 10,  6,  5.50),
    ("active\\_weeks\\_filled",       9,  3,  6,  4,  5.50),
    ("highest\\_education",           7,  8,  2,  9,  6.50),
    ("avg\\_days\\_early\\_filled",  11,  6,  8,  2,  6.75),
    ("avg\\_weekly\\_clicks\\_filled",3,  9, 11,  5,  7.00),
    ("num\\_failed\\_filled",         8,  5,  7, 12,  8.00),
    ("imd\\_band\\_filled",          10, 11,  9,  8,  9.50),
    ("num\\_of\\_prev\\_attempts",   13, 12,  5, 11, 10.25),
    ("no\\_submission\\_despite\\_due",6,10, 15, 15, 11.50),
    ("studied\\_credits",            15, 13, 13, 10, 12.75),
    ("disability",                   14, 14, 12, 14, 13.50),
    ("imd\\_missing",                12, 15, 14, 13, 13.50),
]

rank_rows = []
for name, lr, rf, cb, lgbm, mean_r in RANKS:
    rank_rows.append(
        r"    \code{%s} & %d & %d & %d & %d & %.2f \\" % (name, lr, rf, cb, lgbm, mean_r)
    )

rank_table = "\n".join([
    r"\begin{table}[H]",
    r"  \centering",
    r"  \caption{Thứ hạng độ quan trọng của từng đặc trưng theo mỗi mô hình "
    r"(1 = quan trọng nhất) và hạng trung bình, sắp xếp tăng dần theo hạng "
    r"trung bình.}",
    r"  \label{tab:feature_rank}",
    r"  \footnotesize",
    r"  \begin{tabular}{lrrrrr}",
    r"    \toprule",
    r"    \textbf{Đặc trưng} & \textbf{LogReg} & \textbf{RF} & \textbf{CatBoost} "
    r"& \textbf{LightGBM} & \textbf{Hạng TB} \\",
    r"    \midrule",
    "\n".join(rank_rows),
    r"    \bottomrule",
    r"  \end{tabular}",
    r"\end{table}",
    "",
])
(OUT / "table_feature_rank.tex").write_text(rank_table, encoding="utf-8")

# --- Bảng siêu tham số tốt nhất (SMOTE ratio + class_weight At-risk) theo từng bộ đặc trưng ---
BEST_PARAMS = {
    "Full (15)": {
        "Logistic Regression": (0.7918, 0.90, 1.01),
        "Random Forest":       (0.7986, 0.51, 1.10),
        "CatBoost":            (0.8074, 0.62, 1.04),
        "LightGBM":            (0.8043, 0.10, 1.46),
    },
    "Top-10": {
        "Logistic Regression": (0.7927, 0.55, 1.05),
        "Random Forest":       (0.8008, 0.50, 1.27),
        "CatBoost":            (0.8060, 0.47, 1.79),
        "LightGBM":            (0.8042, 0.18, 1.58),
    },
    "Top-5": {
        "Logistic Regression": (0.7887, 0.51, 1.03),
        "Random Forest":       (0.8021, 0.66, 1.03),
        "CatBoost":            (0.8069, 0.57, 1.33),
        "LightGBM":            (0.8043, 0.10, 1.46),
    },
}

param_rows = []
for fset in ("Full (15)", "Top-10", "Top-5"):
    for i, name in enumerate(MODELS):
        cv_f1, ratio, w = BEST_PARAMS[fset][name]
        fset_cell = (r"\multirow{4}{*}{%s}" % fset) if i == 0 else ""
        param_rows.append(
            r"    %s & \textbf{%s} & %.4f & +%.2fx & %.2f \\" % (fset_cell, name, cv_f1, ratio, w)
        )
    param_rows.append(r"    \midrule")
param_rows = param_rows[:-1]  # bỏ \midrule thừa ở cuối

param_table = "\n".join([
    r"\begin{table}[H]",
    r"  \centering",
    r"  \caption{Siêu tham số tối ưu liên quan đến xử lý mất cân bằng nhãn --- "
    r"tỷ lệ oversampling SMOTE và trọng số lớp At-risk --- được Optuna lựa chọn "
    r"cho từng mô hình và từng bộ đặc trưng, cùng F1 At-risk trung bình qua "
    r"3-fold cross-validation.}",
    r"  \label{tab:best_params}",
    r"  \small",
    r"  \resizebox{\textwidth}{!}{%",
    r"  \begin{tabular}{llrrr}",
    r"    \toprule",
    r"    \textbf{Bộ đặc trưng} & \textbf{Model} & \textbf{F1 At-risk (CV)} & "
    r"\textbf{Tỷ lệ SMOTE} & \textbf{Trọng số At-risk} \\",
    r"    \midrule",
    "\n".join(param_rows),
    r"    \bottomrule",
    r"  \end{tabular}}",
    r"\end{table}",
    "",
])
(OUT / "table_best_params.tex").write_text(param_table, encoding="utf-8")

# --- Bảng phân phối nhãn tại T=180 (train/test) ---
split_table = "\n".join([
    r"\begin{table}[H]",
    r"  \centering",
    r"  \caption{Quy mô và phân phối nhãn nhị phân tại mốc dự đoán $T=180$, sau "
    r"khi gộp Fail và Withdrawn thành At-risk.}",
    r"  \label{tab:split_t180}",
    r"  \begin{tabular}{lrrr}",
    r"    \toprule",
    r"    \textbf{Tập} & \textbf{Pass} & \textbf{At-risk} & \textbf{Tổng} \\",
    r"    \midrule",
    r"    Train & 11{,}067 (65.9\%) & 5{,}719 (34.1\%) & 16{,}786 \\",
    r"    Test  & 2{,}804 (66.5\%)  & 1{,}411 (33.5\%)  & 4{,}215  \\",
    r"    \bottomrule",
    r"  \end{tabular}",
    r"\end{table}",
    "",
])
(OUT / "table_split_t180.tex").write_text(split_table, encoding="utf-8")

# --- Bảng kết quả sơ bộ theo từng mốc dự đoán (một mô hình Logistic Regression
#     riêng cho mỗi mốc T, trước khi thu hẹp phạm vi về T=180 để so sánh nhiều
#     thuật toán) ---
SNAPSHOT_RESULTS = [
    # T, train, test, accuracy, precision_at_risk, recall_at_risk, f1_at_risk
    (30,  19988, 5043, 0.6488, 0.5750, 0.8013, 0.6695),
    (60,  19123, 4835, 0.7231, 0.6429, 0.7666, 0.6993),
    (90,  18508, 4680, 0.7402, 0.6442, 0.7857, 0.7080),
    (120, 17917, 4518, 0.7915, 0.7123, 0.7555, 0.7333),
    (150, 17386, 4363, 0.8263, 0.7524, 0.7659, 0.7591),
    (180, 16786, 4215, 0.8451, 0.7533, 0.7987, 0.7754),
    (210, 16486, 4162, 0.8659, 0.7976, 0.7894, 0.7935),
    (240, 16190, 4094, 0.8796, 0.8269, 0.7814, 0.8035),
]
f1_max = max(r[6] for r in SNAPSHOT_RESULTS)

snap_rows = []
for T, tr, te, acc, prec, rec, f1 in SNAPSHOT_RESULTS:
    f1_cell = r"\textbf{%.4f}" % f1 if f1 == f1_max else f"{f1:.4f}"
    snap_rows.append(
        r"    %d & %s & %s & %.4f & %.4f & %.4f & %s \\"
        % (T, f"{tr:,}".replace(",", "{,}"), f"{te:,}".replace(",", "{,}"),
           acc, prec, rec, f1_cell)
    )

snapshot_table = "\n".join([
    r"\begin{table}[H]",
    r"  \centering",
    r"  \caption{Kết quả sơ bộ của mô hình Logistic Regression --- một mô hình"
    r" riêng cho mỗi mốc dự đoán $T$ --- trên tập kiểm tra. Precision"
    r"/Recall/F1 tính riêng cho lớp At-risk.}",
    r"  \label{tab:snapshot_results}",
    r"  \small",
    r"  \begin{tabular}{rrrrrrr}",
    r"    \toprule",
    r"    \textbf{T (ngày)} & \textbf{Train} & \textbf{Test} & \textbf{Accuracy} "
    r"& \textbf{Precision} & \textbf{Recall} & \textbf{F1} \\",
    r"    \midrule",
    "\n".join(snap_rows),
    r"    \bottomrule",
    r"  \end{tabular}",
    r"\end{table}",
    "",
])
(OUT / "table_snapshot_results.tex").write_text(snapshot_table, encoding="utf-8")

# --- Bảng siêu tham số tối ưu theo từng mốc dự đoán ---
SNAPSHOT_PARAMS = [
    # T, cv_f1, smote_ratio, weight
    (30,  0.6734, 0.67, 1.12),
    (60,  0.7065, 0.56, 1.24),
    (90,  0.7160, 0.57, 1.33),
    (120, 0.7486, 0.69, 1.01),
    (150, 0.7767, 0.55, 1.05),
    (180, 0.7918, 0.90, 1.01),
    (210, 0.8047, 0.51, 1.03),
    (240, 0.8182, 0.42, 1.01),
]
snap_param_rows = [
    r"    %d & %.4f & +%.2fx & %.2f \\" % row for row in SNAPSHOT_PARAMS
]
snapshot_param_table = "\n".join([
    r"\begin{table}[H]",
    r"  \centering",
    r"  \caption{Siêu tham số xử lý mất cân bằng nhãn được Optuna lựa chọn cho"
    r" từng mốc dự đoán, cùng F1 At-risk trung bình qua 3-fold cross-validation.}",
    r"  \label{tab:snapshot_params}",
    r"  \begin{tabular}{rrrr}",
    r"    \toprule",
    r"    \textbf{T (ngày)} & \textbf{F1 At-risk (CV)} & \textbf{Tỷ lệ SMOTE} & "
    r"\textbf{Trọng số At-risk} \\",
    r"    \midrule",
    "\n".join(snap_param_rows),
    r"    \bottomrule",
    r"  \end{tabular}",
    r"\end{table}",
    "",
])
(OUT / "table_snapshot_params.tex").write_text(snapshot_param_table, encoding="utf-8")

print("Wrote table_compare_{full,top10,top5}.tex, table_feature_rank.tex, "
      "table_best_params.tex, table_split_t180.tex, table_snapshot_results.tex, "
      "table_snapshot_params.tex")
