# -*- coding: utf-8 -*-
"""Sinh các hình minh hoạ toán học (hàm sigmoid, log-loss) cho phần cơ sở lý
thuyết của Logistic Regression. Chạy: python gen_figures.py
"""
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent / "figures"

# --- Hàm sigmoid ---
z = np.linspace(-8, 8, 400)
sigmoid = 1 / (1 + np.exp(-z))

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

ax = axes[0]
ax.plot(z, sigmoid, color='tab:blue', linewidth=2)
ax.axhline(0.5, color='gray', linestyle='--', linewidth=1)
ax.axvline(0, color='gray', linestyle='--', linewidth=1)
ax.set_xlabel(r'$z = \mathbf{w}^\top \mathbf{x} + b$')
ax.set_ylabel(r'$\sigma(z)$')
ax.set_title('Hàm sigmoid')
ax.grid(alpha=0.3)

# --- Hàm mất mát log-loss cho y=1 và y=0 ---
p = np.linspace(0.001, 0.999, 400)
loss_y1 = -np.log(p)
loss_y0 = -np.log(1 - p)

ax = axes[1]
ax.plot(p, loss_y1, color='tab:red', linewidth=2, label=r'$y=1$: $-\log(\hat{p})$')
ax.plot(p, loss_y0, color='tab:orange', linewidth=2, label=r'$y=0$: $-\log(1-\hat{p})$')
ax.set_xlabel(r'$\hat{p}$ (xác suất dự báo)')
ax.set_ylabel('Log-loss')
ax.set_title('Hàm mất mát Binary Cross-Entropy')
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(OUT / 'sigmoid_logloss.png', dpi=150)
print('Wrote sigmoid_logloss.png')
