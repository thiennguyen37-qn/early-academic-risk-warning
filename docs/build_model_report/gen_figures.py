# -*- coding: utf-8 -*-
"""Sinh biểu đồ xu hướng hiệu suất theo từng mốc dự đoán (T) từ kết quả thực
nghiệm đã ghi nhận (mô hình Logistic Regression, một mô hình riêng cho mỗi
mốc). Chạy: python gen_figures.py
"""
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent / "figures"

T = [30, 60, 90, 120, 150, 180, 210, 240]
ACCURACY   = [0.6488, 0.7231, 0.7402, 0.7915, 0.8263, 0.8451, 0.8659, 0.8796]
PRECISION  = [0.5750, 0.6429, 0.6442, 0.7123, 0.7524, 0.7533, 0.7976, 0.8269]
RECALL     = [0.8013, 0.7666, 0.7857, 0.7555, 0.7659, 0.7987, 0.7894, 0.7814]
F1         = [0.6695, 0.6993, 0.7080, 0.7333, 0.7591, 0.7754, 0.7935, 0.8035]

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(T, ACCURACY,  marker='o', linewidth=2, color='tab:blue',   label='Accuracy')
ax.plot(T, PRECISION, marker='o', linewidth=2, color='tab:orange', label='Precision (At-risk)')
ax.plot(T, RECALL,    marker='o', linewidth=2, color='tab:green',  label='Recall (At-risk)')
ax.plot(T, F1,        marker='o', linewidth=2, color='tab:red',    label='F1 (At-risk)')

ax.set_xlabel('Mốc dự đoán T (ngày)')
ax.set_ylabel('Score')
ax.set_title('Hiệu suất mô hình theo từng mốc dự đoán (mỗi mốc một mô hình riêng)')
ax.set_xticks(T)
ax.grid(axis='y', linestyle='--', alpha=0.4)
ax.legend(loc='lower right')
plt.tight_layout()
plt.savefig(OUT / 'trend_by_snapshot.png', dpi=150)
print('Wrote trend_by_snapshot.png')
