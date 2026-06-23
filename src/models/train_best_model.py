"""Train & lưu model tốt nhất: LightGBM cho bài toán binary At-risk @ T=180.

Tái lập đúng nhánh LightGBM trong `notebooks/testing_other_models_2_label.ipynb`
(Optuna 30 trials + SMOTE + class_weight, tối ưu F1 At-risk qua 3-fold CV) rồi
retrain best params trên full train và serialize artifact ra `models/`.

Vì mọi thành phần ngẫu nhiên đều cố định theo `RANDOM_SEED`, script này cho ra
kết quả trùng với notebook (F1 At-risk ≈ 0.8024).

Chạy từ thư mục gốc project:
    python -m src.models.train_best_model
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import joblib

import optuna
from imblearn.over_sampling import SMOTE
from lightgbm import LGBMClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    f1_score, precision_score, recall_score, accuracy_score, roc_auc_score,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))
from config import RANDOM_SEED  # noqa: E402

optuna.logging.set_verbosity(optuna.logging.WARNING)

PREDICTION_POINT = 180
N_TRIALS = 30
DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUT_DIR = PROJECT_ROOT / "models"
OUT_PATH = OUT_DIR / "best_lgbm_t180.joblib"

# Gộp Fail (0) + Withdrawn (2) -> At-risk (1); Pass (1) -> 0
LABEL_MAP = {0: 1, 1: 0, 2: 1}


def load_snapshot():
    """Load feature matrix @ T=180, gộp nhãn binary At-risk."""
    X_train = pd.read_parquet(DATA_DIR / "X_train.parquet")
    X_test = pd.read_parquet(DATA_DIR / "X_test.parquet")
    y_train = pd.read_parquet(DATA_DIR / "y_train.parquet").squeeze()
    y_test = pd.read_parquet(DATA_DIR / "y_test.parquet").squeeze()
    train_meta = pd.read_parquet(DATA_DIR / "train_meta.parquet")
    test_meta = pd.read_parquet(DATA_DIR / "test_meta.parquet")

    mask_tr = (train_meta["prediction_point"] == PREDICTION_POINT).values
    mask_te = (test_meta["prediction_point"] == PREDICTION_POINT).values

    X_tr = X_train[mask_tr].reset_index(drop=True).fillna(0)
    X_te = X_test[mask_te].reset_index(drop=True).fillna(0)
    y_tr = y_train[mask_tr].reset_index(drop=True).map(LABEL_MAP)
    y_te = y_test[mask_te].reset_index(drop=True).map(LABEL_MAP)
    return X_tr, X_te, y_tr, y_te


def safe_smote_bin(X, y, ratio_at_risk):
    """Oversample At-risk: new_count = int((1 + ratio) * N_current)."""
    y_arr = np.asarray(y)
    n_at_risk = int((y_arr == 1).sum())
    target = {1: int((1 + ratio_at_risk) * n_at_risk)}
    k = max(1, min(5, n_at_risk - 1))
    sm = SMOTE(sampling_strategy=target, random_state=RANDOM_SEED, k_neighbors=k)
    return sm.fit_resample(np.asarray(X), y_arr)


def suggest_lgbm(trial):
    return {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500),
        "num_leaves": trial.suggest_int("num_leaves", 15, 63),
        "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
        "max_depth": trial.suggest_int("max_depth", 3, 10),
        "min_child_samples": trial.suggest_int("min_child_samples", 10, 100),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-4, 10.0, log=True),
    }


def make_lgbm(params, w_at_risk):
    return LGBMClassifier(
        **params, class_weight={0: 1.0, 1: w_at_risk},
        random_state=RANDOM_SEED, n_jobs=-1, verbose=-1,
    )


def tune(X_tr, y_tr):
    """Optuna tuning: hyperparameter + SMOTE ratio + class_weight, tối ưu F1 At-risk."""
    Xtr, ytr = np.asarray(X_tr), np.asarray(y_tr)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=RANDOM_SEED)

    def objective(trial):
        params = suggest_lgbm(trial)
        ratio = trial.suggest_float("smote_ratio_at_risk", 0.1, 0.9)
        w = trial.suggest_float("w_at_risk", 1.0, 8.0)

        scores = []
        for tr_idx, val_idx in cv.split(Xtr, ytr):
            Xf_tr, yf_tr = Xtr[tr_idx], ytr[tr_idx]
            Xf_val, yf_val = Xtr[val_idx], ytr[val_idx]
            Xf_sm, yf_sm = safe_smote_bin(Xf_tr, yf_tr, ratio)
            m = make_lgbm(params, w)
            m.fit(Xf_sm, yf_sm)
            scores.append(f1_score(yf_val, m.predict(Xf_val), pos_label=1, zero_division=0))
        return float(np.mean(scores))

    study = optuna.create_study(
        direction="maximize",
        sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED),
    )
    study.optimize(objective, n_trials=N_TRIALS, show_progress_bar=True)
    return study


def main():
    print(f"Loading snapshot @ T={PREDICTION_POINT} ...")
    X_tr, X_te, y_tr, y_te = load_snapshot()
    print(f"Train: {X_tr.shape} | Test: {X_te.shape}")
    print(f"Train dist: {y_tr.value_counts().to_dict()}")

    print(f"\nTuning LightGBM ({N_TRIALS} trials) ...")
    study = tune(X_tr, y_tr)
    bp = study.best_params
    best_ratio = bp["smote_ratio_at_risk"]
    best_w = bp["w_at_risk"]
    model_params = {k: v for k, v in bp.items()
                    if k not in ("smote_ratio_at_risk", "w_at_risk")}
    print(f"Best F1 At-risk (CV): {study.best_value:.4f}")
    print(f"SMOTE -> At-risk: +{best_ratio:.2f}x | class_weight At-risk: {best_w:.2f}")

    # Retrain best params trên full train
    X_sm, y_sm = safe_smote_bin(X_tr, y_tr, best_ratio)
    model = make_lgbm(model_params, best_w)
    model.fit(X_sm, y_sm)

    # Đánh giá trên test
    y_pred = model.predict(np.asarray(X_te))
    y_proba = model.predict_proba(np.asarray(X_te))[:, 1]
    metrics = {
        "accuracy": round(accuracy_score(y_te, y_pred), 4),
        "precision_at_risk": round(precision_score(y_te, y_pred, pos_label=1, zero_division=0), 4),
        "recall_at_risk": round(recall_score(y_te, y_pred, pos_label=1, zero_division=0), 4),
        "f1_at_risk": round(f1_score(y_te, y_pred, pos_label=1, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_te, y_proba), 4),
    }
    print("\nTest metrics:")
    for k, v in metrics.items():
        print(f"  {k:18s}: {v}")

    # Serialize artifact (kèm metadata để tái sử dụng downstream)
    OUT_DIR.mkdir(exist_ok=True)
    artifact = {
        "model": model,
        "feature_names": list(X_tr.columns),
        "prediction_point": PREDICTION_POINT,
        "label_map": {"Pass": 0, "At-risk": 1},
        "best_params": bp,
        "test_metrics": metrics,
    }
    joblib.dump(artifact, OUT_PATH)
    print(f"\nSaved artifact -> {OUT_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
