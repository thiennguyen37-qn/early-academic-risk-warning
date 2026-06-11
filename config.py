from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR     = PROJECT_ROOT / "data"
RAW_DIR      = DATA_DIR / "raw"
DB_PATH      = DATA_DIR / "oulad.db"

# --- Temporal snapshots (days from course start) ---
SNAPSHOTS = [30, 60, 90, 120, 150, 180, 210, 240]

# --- Features ---
STATIC_FEATURES = [
    "gender",
    "region",
    "age_band",
    "imd_band",
    "highest_education",
    "num_of_prev_attempts",
    "studied_credits",
    "disability",
]

# --- Reproducibility ---
RANDOM_SEED = 42
