from pathlib import Path

# --- Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR     = PROJECT_ROOT / "data"
RAW_DIR      = DATA_DIR / "raw"
DB_PATH      = DATA_DIR / "oulad.db"

RAW_FILES = {
    "courses":              RAW_DIR / "courses.csv",
    "assessments":          RAW_DIR / "assessments.csv",
    "vle":                  RAW_DIR / "vle.csv",
    "student_info":         RAW_DIR / "studentInfo.csv",
    "student_registration": RAW_DIR / "studentRegistration.csv",
    "student_assessment":   RAW_DIR / "studentAssessment.csv",
    "student_vle":          RAW_DIR / "studentVle.csv",
}

# --- Target ---
TARGET_COL = "final_result"
CLASSES = ["Pass", "Fail", "Withdrawn"] 
AT_RISK_CLASSES = ["Fail", "Withdrawn"]

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
