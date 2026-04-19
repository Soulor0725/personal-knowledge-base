import sqlite3

# 连接数据库
conn = sqlite3.connect('knowledge_base.db')
cursor = conn.cursor()

# 为users表添加avatar字段
try:
    cursor.execute('ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT "";')
    conn.commit()
    print('成功为users表添加avatar字段')
except sqlite3.OperationalError as e:
    print(f'错误: {e}')

# 检查修改后的表结构
print('\n=== users表结构 ===')
cursor.execute('PRAGMA table_info(users);')
for row in cursor.fetchall():
    print(row)

# 关闭连接
conn.close()