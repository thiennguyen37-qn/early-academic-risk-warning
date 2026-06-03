from pathlib import Path

# --- Paths ---
DATA_DIR = Path("data/")

RAW_FILES = {
    "courses":              DATA_DIR / "courses.csv",
    "assessments":          DATA_DIR / "assessments.csv",
    "vle":                  DATA_DIR / "vle.csv",
    "student_info":         DATA_DIR / "studentInfo.csv",
    "student_registration": DATA_DIR / "studentRegistration.csv",
    "student_assessment":   DATA_DIR / "studentAssessment.csv",
    "student_vle":          DATA_DIR / "studentVle.csv",
}

# --- Target ---
TARGET_COL = "final_result"
CLASSES = ["Distinction", "Pass", "Fail", "Withdrawn"]
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
