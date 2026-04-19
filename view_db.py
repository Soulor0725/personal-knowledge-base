import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'knowledge_base.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("=== 数据库表 ===")
for t in tables:
    print(f"  - {t[0]}")

print("\n=== articles 表内容 ===")
cursor.execute("SELECT id, title, category, is_favorite, views FROM articles")
for row in cursor.fetchall():
    print(f"  ID:{row[0]} | {row[1]} | 分类:{row[2]} | 收藏:{row[3]} | 浏览:{row[4]}")

print("\n=== categories 表内容 ===")
cursor.execute("SELECT * FROM categories")
for row in cursor.fetchall():
    print(f"  {row}")

conn.close()
