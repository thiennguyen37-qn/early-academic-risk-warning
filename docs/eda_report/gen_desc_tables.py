# -*- coding: utf-8 -*-
"""Sinh các bảng thống kê mô tả (describe / group-mean) ra file .tex."""
import pandas as pd
import sqlite3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from config import DB_PATH

OUT = Path(__file__).resolve().parent
t = pd.read_parquet(ROOT / "data/processed/train.parquet")
DYN = ['total_clicks', 'active_weeks', 'avg_weekly_clicks',
       'num_submitted', 'avg_score', 'num_failed', 'avg_days_early']


def code(s):
    return r'\code{%s}' % str(s).replace('_', r'\_')


def num(x, dec=2, thousands=False):
    if pd.isna(x):
        return '--'
    if thousands and float(x).is_integer():
        return '{:,}'.format(int(x))
    return ('{:,.%df}' % dec).format(x)


def table(caption, label, header, rows, colspec, resize=True, small=True):
    body = '\n'.join('    ' + ' & '.join(r) + r' \\' for r in rows)
    head = ' & '.join(r'\textbf{%s}' % h for h in header)
    tab = [
        r'\begin{table}[H]', r'  \centering',
        r'  \caption{%s}' % caption, r'  \label{%s}' % label,
    ]
    if small:
        tab += [r'  \footnotesize', r'  \setlength{\tabcolsep}{4pt}']
    inner = [r'  \begin{tabular}{%s}' % colspec, r'    \toprule',
             '    ' + head + r' \\', r'    \midrule', body,
             r'    \bottomrule', r'  \end{tabular}']
    if resize:
        tab += [r'  \resizebox{\textwidth}{!}{%'] + inner + [r'  }']
    else:
        tab += inner
    tab += [r'\end{table}', '']
    return '\n'.join(tab)


STAT = ['N', 'Trung bình', 'Độ lệch chuẩn', 'Min', 'Q1', 'Trung vị', 'Q3', 'Max']


def describe_rows(df, cols, labelfn):
    rows = []
    d = df[cols].describe()
    for c in cols:
        s = d[c]
        rows.append([labelfn(c), num(s['count'], 0, True), num(s['mean']),
                     num(s['std']), num(s['min']), num(s['25%']),
                     num(s['50%']), num(s['75%']), num(s['max'])])
    return rows


# ---- T0: Assessment describe(object) ----
conn = sqlite3.connect(DB_PATH)
a = pd.read_sql('SELECT * FROM assessments', conn).merge(
    pd.read_sql('SELECT * FROM courses', conn), on=['code_module', 'code_presentation'])
rows0 = []
for c in ['code_module', 'code_presentation', 'assessment_type']:
    d = a[c].describe()
    rows0.append([code(c), num(d['count'], 0, True), str(int(d['unique'])),
                  code(d['top']) if c != 'assessment_type' else str(d['top']),
                  str(int(d['freq']))])
(OUT / 'table_desc_assessment.tex').write_text(table(
    r'Thống kê mô tả các biến phân loại của dữ liệu đánh giá.',
    'tab:desc_assessment',
    ['Biến', 'N', 'Số nhóm', 'Giá trị phổ biến', 'Tần suất'],
    rows0, 'lrrrr', resize=False), encoding='utf-8')

# ---- T1: VLE describe ----
vwa = pd.read_sql('''
 SELECT id_student, code_module, code_presentation,
   CAST(FLOOR(CAST(date AS FLOAT)/7) AS INTEGER) AS week,
   SUM(sum_click) AS weekly_clicks
 FROM studentVle GROUP BY id_student, code_module, code_presentation, week
''', conn)
rows1 = describe_rows(vwa, ['week', 'weekly_clicks'], code)
(OUT / 'table_desc_vle.tex').write_text(table(
    r'Thống kê mô tả dữ liệu tương tác VLE theo tuần.',
    'tab:desc_vle', ['Biến'] + STAT, rows1, 'l' + 'r' * 8), encoding='utf-8')

# ---- T2: Dynamic describe ----
rows2 = describe_rows(t, DYN, code)
(OUT / 'table_desc_dynamic.tex').write_text(table(
    r'Thống kê mô tả các đặc trưng động (tính trên tập huấn luyện).',
    'tab:desc_dynamic', ['Đặc trưng'] + STAT, rows2, 'l' + 'r' * 8), encoding='utf-8')

# ---- T3: studied_credits by is_retake ----
sap = t[['id_student', 'code_module', 'code_presentation',
         'num_of_prev_attempts', 'studied_credits', 'final_result']].drop_duplicates()
sap['is_retake'] = (sap['num_of_prev_attempts'] > 0).astype(int)
rows3 = []
for v, lab in [(0, 'Học lần đầu'), (1, 'Học lại')]:
    s = sap[sap['is_retake'] == v]['studied_credits'].describe()
    rows3.append([lab, num(s['count'], 0, True), num(s['mean']), num(s['std']),
                  num(s['min']), num(s['25%']), num(s['50%']), num(s['75%']), num(s['max'])])
(OUT / 'table_desc_credits.tex').write_text(table(
    r'Thống kê mô tả số tín chỉ (\code{studied\_credits}) theo nhóm học lần đầu / học lại.',
    'tab:desc_credits', ['Nhóm'] + STAT, rows3, 'l' + 'r' * 8), encoding='utf-8')

# ---- T4: static mean by final_result ----
us = t[['id_student', 'age_band', 'disability']].drop_duplicates('id_student').copy()
us['disab'] = (us['disability'] == 'Y').astype(int)
us['u35'] = (us['age_band'] == '0-35').astype(int)
adf = sap.merge(us[['id_student', 'disab', 'u35']], on='id_student')
g = adf.groupby('final_result')
rows4 = []
for res in ['Pass', 'Fail', 'Withdrawn']:
    r = g.get_group(res)
    rows4.append([r'\textbf{%s}' % res,
                  num(r['is_retake'].mean() * 100, 1) + r'\%',
                  num(r['studied_credits'].mean()),
                  num(r['num_of_prev_attempts'].mean()),
                  num(r['disab'].mean() * 100, 1) + r'\%',
                  num(r['u35'].mean() * 100, 1) + r'\%'])
(OUT / 'table_mean_static.tex').write_text(table(
    r'Giá trị trung bình các đặc trưng tĩnh theo nhóm kết quả.',
    'tab:mean_static',
    ['Nhóm', 'Tỷ lệ học lại', 'Số tín chỉ TB', 'Số lần học trước TB',
     'Tỷ lệ khuyết tật', r'Tỷ lệ tuổi $\le 35$'],
    rows4, 'lccccc', resize=True), encoding='utf-8')

# ---- T5: dynamic mean by final_result ----
gd = t.groupby('final_result')[DYN].mean()
rows5 = []
for res in ['Pass', 'Fail', 'Withdrawn']:
    rows5.append([r'\textbf{%s}' % res] + [num(gd.loc[res, c]) for c in DYN])
(OUT / 'table_mean_dynamic.tex').write_text(table(
    r'Giá trị trung bình các đặc trưng động theo nhóm kết quả.',
    'tab:mean_dynamic', ['Nhóm'] + [code(c) for c in DYN],
    rows5, 'l' + 'r' * 7), encoding='utf-8')

print('Wrote 6 describe/mean tables.')
