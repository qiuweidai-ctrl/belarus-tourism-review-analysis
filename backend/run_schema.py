"""Execute schema.sql against the MySQL database."""
import os
import pymysql

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, 'schema.sql')

conn = pymysql.connect(host='localhost', user='root', password='123456', charset='utf8mb4')
cursor = conn.cursor()

# Drop and recreate database
cursor.execute("DROP DATABASE IF EXISTS belarus_tourism")
cursor.execute("CREATE DATABASE belarus_tourism CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
cursor.execute("USE belarus_tourism")
conn.commit()
print("Database created")

# Read and split schema.sql
with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove comments and split by semicolon
statements = []
current = []
for line in content.splitlines():
    stripped = line.strip()
    if stripped.startswith('--') or not stripped:
        continue
    current.append(line)
    if line.rstrip().endswith(';'):
        stmt = '\n'.join(current)
        stmt = stmt.rstrip(';').strip()
        if stmt:
            statements.append(stmt)
        current = []

# Execute each statement
for i, stmt in enumerate(statements):
    try:
        cursor.execute(stmt)
        conn.commit()
        print(f"  [{i+1}/{len(statements)}] OK")
    except Exception as e:
        print(f"  [{i+1}/{len(statements)}] ERROR: {e}")
        print(f"  Statement: {stmt[:100]}...")

cursor.close()
conn.close()
print("\nSchema applied. Total statements:", len(statements))
