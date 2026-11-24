import sqlite3
import os

conn = sqlite3.connect("krishi.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in krishi.db:", tables)

for (table_name,) in tables:
    cursor.execute(f"PRAGMA table_info({table_name})")
    cols = [col[1] for col in cursor.fetchall()]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    cnt = cursor.fetchone()[0]
    print(f"Table '{table_name}' ({cnt} rows): {cols}")
    if cnt > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 2")
        print(f"  Sample row: {cursor.fetchall()}")
