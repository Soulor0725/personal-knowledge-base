import sqlite3

# 连接数据库
conn = sqlite3.connect('knowledge_base.db')
cursor = conn.cursor()

# 检查表结构
print('=== articles表结构 ===')
cursor.execute('PRAGMA table_info(articles);')
for row in cursor.fetchall():
    print(row)

# 检查数据
print('\n=== 文章数据 ===')
cursor.execute('SELECT id, title, category FROM articles LIMIT 5;')
for row in cursor.fetchall():
    print(row)

# 关闭连接
conn.close()