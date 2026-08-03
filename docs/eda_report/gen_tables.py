# -*- coding: utf-8 -*-
"""Sinh hai bảng crosstab imd_band (theo region và theo education) ra file .tex.
Chạy: python gen_tables.py  (dùng train.parquet đã lưu từ notebook EDA).
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
train = pd.read_parquet(ROOT / "data/processed/train.parquet")

DEMO = ["gender", "region", "age_band", "imd_band", "highest_education", "disability"]
us = train[["id_student"] + DEMO].drop_duplicates(subset="id_student")

imd_order = ["0-10%", "10-20", "20-30%", "30-40%", "40-50%",
             "50-60%", "60-70%", "70-80%", "80-90%", "90-100%", "?"]
hdr = ["0-10", "10-20", "20-30", "30-40", "40-50",
       "50-60", "60-70", "70-80", "80-90", "90-100", "?"]
edu_order = ["No Formal quals", "Lower Than A Level", "A Level or Equivalent",
             "HE Qualification", "Post Graduate Qualification"]


def cell(v, lo, hi):
    t = 0.0 if hi == lo else (v - lo) / (hi - lo)
    p = int(round(t * 70))
    return r"\cellcolor{orange!%d}%.2f" % (p, v)


def body(df):
    lines = []
    for name in df.index:
        row = df.loc[name]
        lo, hi = row.min(), row.max()
        cells = " & ".join(cell(row[b], lo, hi) for b in imd_order)
        disp = str(name).replace("&", r"\&")
        lines.append(r"\textbf{%s} & %s \\" % (disp, cells))
    return "\n".join(lines)


def make_table(df, caption, label, first_col):
    colspec = "l" + "r" * len(imd_order)
    head = " & ".join([r"\textbf{%s}" % first_col] +
                      [r"\textbf{%s}" % h for h in hdr])
    return "\n".join([
        r"\begin{table}[H]",
        r"  \centering",
        r"  \caption{%s}" % caption,
        r"  \label{%s}" % label,
        r"  \footnotesize",
        r"  \setlength{\tabcolsep}{3pt}",
        r"  \resizebox{\textwidth}{!}{%",
        r"  \begin{tabular}{%s}" % colspec,
        r"    \toprule",
        "    " + head + r" \\",
        r"    \midrule",
        "\n".join("    " + ln for ln in body(df).splitlines()),
        r"    \bottomrule",
        r"  \end{tabular}}",
        r"\end{table}",
        "",
    ])


r = (pd.crosstab(us["region"], us["imd_band"], normalize="index") * 100
     ).round(2).reindex(columns=imd_order).sort_values("?", ascending=False)
e = (pd.crosstab(us["highest_education"], us["imd_band"], normalize="index") * 100
     ).round(2).reindex(edu_order).reindex(columns=imd_order)

out = Path(__file__).resolve().parent
(out / "table_imd_region.tex").write_text(
    make_table(r,
               r"Phân phối \code{imd\_band} (\%) theo Region (chuẩn hoá theo hàng, "
               r"sắp xếp giảm dần theo cột \code{'?'}). Màu đậm hơn = tỷ trọng cao hơn trong hàng.",
               "tab:imd_region", "Region"),
    encoding="utf-8")
(out / "table_imd_edu.tex").write_text(
    make_table(e,
               r"Phân phối \code{imd\_band} (\%) theo trình độ học vấn "
               r"(chuẩn hoá theo hàng). Màu đậm hơn = tỷ trọng cao hơn trong hàng.",
               "tab:imd_edu", "Highest education"),
    encoding="utf-8")
print("Wrote table_imd_region.tex and table_imd_edu.tex")
