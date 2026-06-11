import sys
import sqlite3
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from config import RAW_DIR, DB_PATH

TABLES = [
    "assessments",
    "courses",
    "studentAssessment",
    "studentInfo",
    "studentRegistration",
    "studentVle",
    "vle",
]

conn = sqlite3.connect(DB_PATH)

print("Bắt đầu load data vào SQLite...\n")

for table in TABLES:
    df = pd.read_csv(RAW_DIR / f"{table}.csv")
    df.to_sql(table, conn, if_exists="replace", index=False)
    print(f"✅ {table}: {len(df):,} rows")

conn.close()
print(f"\nXong! File database: {DB_PATH}")