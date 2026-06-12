from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR     = PROJECT_ROOT / "data"
RAW_DIR      = DATA_DIR / "raw"
DB_PATH      = DATA_DIR / "oulad.db"

# --- Temporal snapshots (days from course start) ---
SNAPSHOTS = [30, 60, 90, 120, 150, 180, 210, 240]

# --- Features ---
DEMOGRAPHIC_COLS = [
    "gender",
    "region",
    "age_band",
    "imd_band",
    "highest_education",
    "disability",
]

BEHAVIORAL_STATIC_COLS = [
    "num_of_prev_attempts",
    "studied_credits",
]

STATIC_FEATURES = DEMOGRAPHIC_COLS + BEHAVIORAL_STATIC_COLS

# --- Reproducibility ---
RANDOM_SEED = 42
