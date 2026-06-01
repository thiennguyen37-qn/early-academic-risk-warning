import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = Path("data/oulad.db")
DATA_DIR = Path("data/")

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
    df = pd.read_csv(DATA_DIR / f"{table}.csv")
    df.to_sql(table, conn, if_exists="replace", index=False)
    print(f"✅ {table}: {len(df):,} rows")

conn.close()
print("\nXong! File database: data/oulad.db")