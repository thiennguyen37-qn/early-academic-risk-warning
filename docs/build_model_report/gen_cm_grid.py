# -*- coding: utf-8 -*-
"""Sinh grid ma trận nhầm lẫn (2 hàng x 2 cột) trên tập kiểm tra tại bốn mốc
dự đoán tiêu biểu (T=30, 90, 180, 240), mô hình Logistic Regression (một mô
hình riêng cho mỗi mốc). Chạy: python gen_cm_grid.py
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
from pathlib import Path

OUT = Path(__file__).resolve().parent / "figures"

TARGET_NAMES = ["Pass", "At-risk"]

# [[TN, FP], [FN, TP]] ứng với (Pass, At-risk)
CM = {
    30:  [[1478, 1326], [445, 1764]],
    90:  [[1990,  814], [402, 1474]],
    180: [[2435,  369], [284, 1127]],
    240: [[2593,  211], [282, 1098]],
}

fig, axes = plt.subplots(2, 2, figsize=(8, 8))

for ax, T in zip(axes.flat, CM.keys()):
    cm = np.array(CM[T])
    ConfusionMatrixDisplay(cm, display_labels=TARGET_NAMES).plot(
        ax=ax, colorbar=False, cmap="viridis"
    )
    ax.set_title(f"T={T}")

plt.tight_layout()
plt.savefig(OUT / "cm_grid_snapshots.png", dpi=150)
print("Wrote cm_grid_snapshots.png (2x2, T=30/90/180/240)")
