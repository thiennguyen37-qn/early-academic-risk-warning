# -*- coding: utf-8 -*-
"""Sinh các bảng .tex (so sánh model, thứ hạng đặc trưng, siêu tham số) từ kết quả
thực nghiệm. Các bảng chuyên sâu tại mốc 150 ngày đọc trực tiếp từ
`results_t150.json` do notebook `testing_other_models_2_label.ipynb` xuất ra,
nên không có số liệu nào bị chép tay. Chạy: python gen_tables.py
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
REPORT = OUT.parent.parent / "full_report"          # bản báo cáo tổng hợp
RESULTS = json.loads((REPORT / "results_t150.json").read_text(encoding="utf-8"))

MODELS = ["Logistic Regression", "Random Forest", "CatBoost", "LightGBM"]
METRIC_KEYS = ["accuracy", "precision", "recall", "f1", "roc_auc"]

# --- Bảng so sánh model theo từng bộ đặc trưng: accuracy, precision, recall, f1, roc_auc ---
COMPARE = {
    key: {m: tuple(RESULTS["compare"][key][m][k] for k in METRIC_KEYS) for m in MODELS}
    for key in ("full", "top10", "top5")
}
METRIC_HEADERS = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]

CAPTIONS = {
    "full":  (r"So sánh các mô hình trên bộ 15 đặc trưng đầy đủ tại mốc 150 "
              r"ngày. Chỉ số Precision/Recall/F1 tính riêng cho lớp "
              r"\textbf{At-risk}.",
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
    (name.replace("_", "\\_"),
     r["Logistic Regression"], r["Random Forest"], r["CatBoost"], r["LightGBM"],
     r["mean_rank"])
    for name, r in RESULTS["ranks"].items()
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
    fset: {
        m: (RESULTS["tuning"][f"{fset}|{m}"]["cv_f1"],
            RESULTS["tuning"][f"{fset}|{m}"]["smote_ratio"],
            RESULTS["tuning"][f"{fset}|{m}"]["w_at_risk"])
        for m in MODELS
    }
    for fset in ("Full (15)", "Top-10", "Top-5")
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

# --- Bảng phân phối nhãn tại T=150 (train/test) ---
def _split_row(label, d):
    n = d["total"]
    return (r"    %s & %s (%.1f\%%) & %s (%.1f\%%) & %s \\"
            % (label,
               f"{d['pass']:,}".replace(",", "{,}"),    d["pass"] / n * 100,
               f"{d['at_risk']:,}".replace(",", "{,}"), d["at_risk"] / n * 100,
               f"{n:,}".replace(",", "{,}")))


split_table = "\n".join([
    r"\begin{table}[H]",
    r"  \centering",
    r"  \caption{Quy mô và phân phối nhãn nhị phân tại mốc dự đoán 150 ngày, sau "
    r"khi gộp Fail và Withdrawn thành At-risk.}",
    r"  \label{tab:split_t150}",
    r"  \begin{tabular}{lrrr}",
    r"    \toprule",
    r"    \textbf{Tập} & \textbf{Pass} & \textbf{At-risk} & \textbf{Tổng} \\",
    r"    \midrule",
    _split_row("Train", RESULTS["split"]["train"]),
    _split_row("Test ", RESULTS["split"]["test"]),
    r"    \bottomrule",
    r"  \end{tabular}",
    r"\end{table}",
    "",
])
(OUT / "table_split_t150.tex").write_text(split_table, encoding="utf-8")

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

GENERATED = [
    "table_compare_full.tex", "table_compare_top10.tex", "table_compare_top5.tex",
    "table_feature_rank.tex", "table_best_params.tex", "table_split_t150.tex",
    "table_snapshot_results.tex", "table_snapshot_params.tex",
]

# Đồng bộ sang bản báo cáo tổng hợp
for fname in GENERATED:
    (REPORT / fname).write_text((OUT / fname).read_text(encoding="utf-8"), encoding="utf-8")

print("Wrote + synced to full_report/: " + ", ".join(GENERATED))
