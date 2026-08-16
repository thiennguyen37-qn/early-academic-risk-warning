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


(OUT / "table_compare_full.tex").write_text(make_compare_table("full"), encoding="utf-8")

# --- Bảng rút gọn đặc trưng: chỉ CatBoost, so sánh Full / Top-10 / Top-5 ---
FEATURE_SETS = [
    ("Full (15)", "full"),
    ("Top-10",    "top10"),
    ("Top-5",     "top5"),
]
FOCUS_MODEL = RESULTS["best_model"]          # CatBoost

fs_vals = {
    label: tuple(RESULTS["compare"][key][FOCUS_MODEL][k] for k in METRIC_KEYS)
    for label, key in FEATURE_SETS
}
fs_col_max = [max(c) for c in zip(*fs_vals.values())]

fs_rows = []
for label, _ in FEATURE_SETS:
    cells = [
        (r"\textbf{%s}" % f"{v:.4f}") if v == vmax else f"{v:.4f}"
        for v, vmax in zip(fs_vals[label], fs_col_max)
    ]
    n_feat = len(RESULTS["feature_sets"]["full" if label.startswith("Full")
                                         else ("top10" if label == "Top-10" else "top5")])
    fs_rows.append(r"    \textbf{%s} & %d & %s \\" % (label, n_feat, " & ".join(cells)))

feature_set_table = "\n".join([
    r"\begin{table}[H]",
    r"  \centering",
    r"  \caption{Hiệu suất của %s --- mô hình tốt nhất ở bước so sánh thuật "
    r"toán --- trên ba bộ đặc trưng tại mốc 150 ngày. Chỉ số "
    r"Precision/Recall/F1 tính riêng cho lớp \textbf{At-risk}.}" % FOCUS_MODEL,
    r"  \label{tab:compare_featuresets}",
    r"  \small",
    r"  \setlength{\tabcolsep}{5pt}",
    r"  \begin{tabular}{lrrrrrr}",
    r"    \toprule",
    r"    \textbf{Bộ đặc trưng} & \textbf{Số đặc trưng} & "
    + " & ".join(r"\textbf{%s}" % h for h in METRIC_HEADERS) + r" \\",
    r"    \midrule",
    "\n".join(fs_rows),
    r"    \bottomrule",
    r"  \end{tabular}",
    r"\end{table}",
    "",
])
(OUT / "table_compare_featuresets.tex").write_text(feature_set_table, encoding="utf-8")

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

# Bảng siêu tham số tối ưu theo từng bộ đặc trưng đã được gỡ khỏi báo cáo:
# phần rút gọn đặc trưng chỉ tập trung vào hiệu suất của CatBoost, không đi sâu
# vào siêu tham số. Số liệu vẫn còn trong results_t150.json nếu cần dựng lại.

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
    (30,  19988, 5043, 0.6443, 0.5698, 0.8115, 0.6695),
    (60,  19123, 4835, 0.7369, 0.6734, 0.7258, 0.6986),
    (90,  18508, 4680, 0.7402, 0.6442, 0.7857, 0.7080),
    (120, 17917, 4518, 0.7900, 0.7096, 0.7555, 0.7318),
    (150, 17386, 4363, 0.8260, 0.7561, 0.7575, 0.7568),
    (180, 16786, 4215, 0.8458, 0.7552, 0.7980, 0.7760),
    (210, 16486, 4162, 0.8640, 0.7960, 0.7842, 0.7901),
    (240, 16190, 4094, 0.8774, 0.8152, 0.7899, 0.8024),
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
    (30,  0.6723, 0.56, 1.24),
    (60,  0.7065, 0.63, 1.01),
    (90,  0.7160, 0.57, 1.33),
    (120, 0.7485, 0.53, 1.13),
    (150, 0.7762, 0.43, 1.11),
    (180, 0.7923, 0.88, 1.01),
    (210, 0.8042, 0.51, 1.03),
    (240, 0.8174, 0.51, 1.03),
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

# --- Bảng hiệu chỉnh ngưỡng + bootstrap (từ notebook threshold_bootstrap.ipynb) ---
THR_PATH = REPORT / "results_threshold_t150.json"
THR_TABLES = []

if THR_PATH.exists():
    THR = json.loads(THR_PATH.read_text(encoding="utf-8"))

    # (a) Các chỉ số tại một số mức ngưỡng
    thr_rows = []
    for r in THR["threshold_table"]:
        mark = r"\textbf{%.2f}" % r["threshold"] if r["threshold"] == THR["baseline_threshold"] \
               else "%.2f" % r["threshold"]
        thr_rows.append(
            r"    %s & %.4f & %.4f & %.4f & %d & %d & %d \\"
            % (mark, r["recall"], r["precision"], r["f1"], r["TP"], r["FN"], r["FP"])
        )
    thr_table = "\n".join([
        r"\begin{table}[H]",
        r"  \centering",
        r"  \caption{Ảnh hưởng của ngưỡng phân loại lên kết quả dự báo của %s "
        r"tại mốc 150 ngày. Tập kiểm tra có %s sinh viên At-risk thực tế; hàng "
        r"in đậm là ngưỡng mặc định.}"
        % (THR["model"], f"{THR['n_at_risk_test']:,}".replace(",", "{,}")),
        r"  \label{tab:threshold}",
        r"  \small",
        r"  \begin{tabular}{rrrrrrr}",
        r"    \toprule",
        r"    \textbf{Ngưỡng} & \textbf{Recall} & \textbf{Precision} & \textbf{F1} "
        r"& \textbf{Bắt được} & \textbf{Bỏ sót} & \textbf{Cảnh báo nhầm} \\",
        r"    \midrule",
        "\n".join(thr_rows),
        r"    \bottomrule",
        r"  \end{tabular}",
        r"\end{table}",
        "",
    ])
    (OUT / "table_threshold.tex").write_text(thr_table, encoding="utf-8")
    THR_TABLES.append("table_threshold.tex")

    # (b) Ngưỡng cần dùng để đạt recall mục tiêu
    tgt_rows = [
        r"    %.0f\%% & %.3f & %.4f & %.4f & $+$%d & $+$%d & %d & %s \\"
        % (r["target"] * 100, r["threshold"], r["recall"], r["precision"],
           r["extra_TP"], r["extra_FP"], r["FN"],
           ("%.1f" % r["cost"]) if r["cost"] is not None else "---")
        for r in THR["target_recall"]
    ]
    tgt_table = "\n".join([
        r"\begin{table}[H]",
        r"  \centering",
        r"  \caption{Ngưỡng cần dùng để đạt các mức recall mục tiêu, và cái giá "
        r"phải trả. Cột ``Bắt thêm'' và ``Nhầm thêm'' so với ngưỡng mặc định "
        r"0.5; cột cuối là số cảnh báo nhầm phát sinh trên mỗi sinh viên "
        r"At-risk bắt thêm được.}",
        r"  \label{tab:target_recall}",
        r"  \small",
        r"  \setlength{\tabcolsep}{5pt}",
        r"  \begin{tabular}{rrrrrrrr}",
        r"    \toprule",
        r"    \textbf{Recall} & \textbf{Ngưỡng} & \textbf{Recall} & "
        r"\textbf{Precision} & \textbf{Bắt} & \textbf{Nhầm} & \textbf{Còn} & "
        r"\textbf{Nhầm/} \\",
        r"    \textbf{mục tiêu} & & \textbf{thực tế} & & \textbf{thêm} & "
        r"\textbf{thêm} & \textbf{bỏ sót} & \textbf{1 ca} \\",
        r"    \midrule",
        "\n".join(tgt_rows),
        r"    \bottomrule",
        r"  \end{tabular}",
        r"\end{table}",
        "",
    ])
    (OUT / "table_target_recall.tex").write_text(tgt_table, encoding="utf-8")
    THR_TABLES.append("table_target_recall.tex")

    # (c) Khoảng tin cậy bootstrap
    CI_LABEL = {"accuracy": "Accuracy", "precision": "Precision (At-risk)",
                "recall": "Recall (At-risk)", "f1": "F1 (At-risk)",
                "roc_auc": "ROC-AUC"}
    ci_rows = [
        r"    %s & %.4f & $[%.4f;\ %.4f]$ & %.4f & %.4f \\"
        % (CI_LABEL[r["metric"]], r["point"], r["ci_low"], r["ci_high"],
           r["width"], r["se"])
        for r in THR["bootstrap_ci"]
    ]
    ci_table = "\n".join([
        r"\begin{table}[H]",
        r"  \centering",
        r"  \caption{Khoảng tin cậy 95\%% của các chỉ số đánh giá, ước lượng "
        r"bằng bootstrap trên tập kiểm tra ($B = %s$ lần lấy mẫu có hoàn lại) "
        r"tại ngưỡng mặc định 0.5.}" % f"{THR['n_boot']:,}".replace(",", "{,}"),
        r"  \label{tab:bootstrap_ci}",
        r"  \small",
        r"  \begin{tabular}{lrrrr}",
        r"    \toprule",
        r"    \textbf{Chỉ số} & \textbf{Ước lượng điểm} & \textbf{KTC 95\%} & "
        r"\textbf{Độ rộng} & \textbf{Sai số chuẩn} \\",
        r"    \midrule",
        "\n".join(ci_rows),
        r"    \bottomrule",
        r"  \end{tabular}",
        r"\end{table}",
        "",
    ])
    (OUT / "table_bootstrap_ci.tex").write_text(ci_table, encoding="utf-8")
    THR_TABLES.append("table_bootstrap_ci.tex")
else:
    print(f"[!] Chưa có {THR_PATH.name} — bỏ qua bảng ngưỡng/bootstrap.")

GENERATED = [
    "table_compare_full.tex", "table_compare_featuresets.tex",
    "table_feature_rank.tex", "table_split_t150.tex",
    "table_snapshot_results.tex", "table_snapshot_params.tex",
] + THR_TABLES

# Đồng bộ sang bản báo cáo tổng hợp
for fname in GENERATED:
    (REPORT / fname).write_text((OUT / fname).read_text(encoding="utf-8"), encoding="utf-8")

print("Wrote + synced to full_report/: " + ", ".join(GENERATED))
