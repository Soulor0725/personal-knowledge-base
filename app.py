from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
import jwt
from passlib.hash import pbkdf2_sha256
from functools import wraps

app = Flask(__name__, static_folder='static')
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # 实际部署时应使用环境变量

DATABASE = 'knowledge_base.db'
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def generate_token(user_id):
    """生成JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)  # 7天过期
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    """登录装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '未提供认证token'}), 401
        
        token = token.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': '无效或过期的token'}), 401
        
        g.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 创建文章表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT DEFAULT '未分类',
            tags TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            views INTEGER DEFAULT 0,
            is_favorite INTEGER DEFAULT 0,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # 创建分类表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT DEFAULT '#667eea',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')


    # 检查是否已有分类，如果没有则插入默认分类
    cursor.execute('SELECT COUNT(*) FROM categories')
    count = cursor.fetchone()[0]
    if count == 0:
        # 只在数据库为空时插入默认分类
        cursor.execute("INSERT INTO categories (name, color) VALUES ('技术', '#667eea')")
        cursor.execute("INSERT INTO categories (name, color) VALUES ('生活', '#764ba2')")
        cursor.execute("INSERT INTO categories (name, color) VALUES ('学习', '#f093fb')")
        cursor.execute("INSERT INTO categories (name, color) VALUES ('工作', '#4facfe')")

    conn.commit()
    conn.close()

@app.route('/api/test', methods=['GET'])
def test():
    """测试路由"""
    return jsonify({'message': 'Test endpoint works!'})

@app.route('/api/test2')
def test2():
    """测试路由2"""
    return jsonify({'message': 'Test2 endpoint works!'})

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()
    username = data.get('username').strip()
    password = data.get('password')
    name = data.get('name', '').strip()  # 添加中文名字字段
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    if len(username) < 3 or len(password) < 6:
        return jsonify({'error': '用户名至少3个字符，密码至少6个字符'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        hashed_password = pbkdf2_sha256.hash(password)
        cursor.execute('INSERT INTO users (username, password, name) VALUES (?, ?, ?)', (username, hashed_password, name))
        user_id = cursor.lastrowid
        db.commit()
        
        token = generate_token(user_id)
        return jsonify({'id': user_id, 'username': username, 'name': name, 'token': token, 'message': '注册成功'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': '用户名已存在'}), 400

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username').strip()
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user or not pbkdf2_sha256.verify(password, user['password']):
        return jsonify({'error': '用户名或密码错误'}), 401
    
    token = generate_token(user['id'])
    # 检查 user 中是否有 'name' 列
    name = user['name'] if 'name' in user.keys() else ''
    return jsonify({'id': user['id'], 'username': user['username'], 'name': name, 'token': token, 'message': '登录成功'})

@app.route('/')
def index():
    """返回首页"""
    return send_from_directory('static', 'index.html')

@app.route('/api/auth/me', methods=['GET', 'PUT'])
@login_required
def get_current_user():
    """获取或更新当前用户信息"""
    if request.method == 'GET':
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, username, name, avatar, created_at FROM users WHERE id = ?', (g.user_id,))
        user = cursor.fetchone()
        return jsonify(dict(user))
    elif request.method == 'PUT':
        data = request.get_json()
        name = data.get('name', '').strip()
        avatar = data.get('avatar', '')
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute('UPDATE users SET name = ?, avatar = ? WHERE id = ?', (name, avatar, g.user_id))
            db.commit()
            
            # 返回更新后的用户信息
            cursor.execute('SELECT id, username, name, avatar, created_at FROM users WHERE id = ?', (g.user_id,))
            user = cursor.fetchone()
            return jsonify(dict(user))
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/articles', methods=['GET'])
@login_required
def get_articles():
    db = get_db()
    cursor = db.cursor()

    category = request.args.get('category')
    tag = request.args.get('tag')
    search = request.args.get('search')
    favorite = request.args.get('favorite')

    query = 'SELECT * FROM articles WHERE user_id = ?'
    params = [g.user_id]

    if category:
        query += ' AND category = ?'
        params.append(category)
    if tag:
        query += ' AND tags LIKE ?'
        params.append(f'%{tag}%')
    if search:
        query += ' AND (title LIKE ? OR content LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])
    if favorite == 'true':
        query += ' AND is_favorite = 1'

    query += ' ORDER BY updated_at DESC'
    cursor.execute(query, params)
    articles = [dict(row) for row in cursor.fetchall()]
    return jsonify(articles)

@app.route('/api/articles/navigate', methods=['GET'])
@login_required
def get_navigate_article():
    current_id = request.args.get('current_id', type=int)
    direction = request.args.get('direction', 'next')
    
    print(f"=== 导航请求 ===")
    print(f"当前ID: {current_id}")
    print(f"方向: {direction}")
    
    if not current_id:
        print("缺少参数")
        return jsonify({'error': '缺少参数'}), 400
    
    # 获取当前用户ID
    user_id = g.user_id
    print(f"用户ID: {user_id}")
    
    try:
        db = get_db()
        cursor = db.cursor()
        
        # 先查询所有文章的ID，看看有哪些文章
        cursor.execute('SELECT id FROM articles WHERE user_id = ? ORDER BY id ASC', (user_id,))
        all_ids = [row[0] for row in cursor.fetchall()]
        print(f"所有文章ID: {all_ids}")
        
        if direction == 'prev':
            # 上一篇：找到比当前ID小的最大ID
            query = '''
                SELECT * FROM articles 
                WHERE id < ? AND user_id = ? 
                ORDER BY id DESC 
                LIMIT 1
            '''
            print("查询上一篇文章")
        else:
            # 下一篇：找到比当前ID大的最小ID
            query = '''
                SELECT * FROM articles 
                WHERE id > ? AND user_id = ? 
                ORDER BY id ASC 
                LIMIT 1
            '''
            print("查询下一篇文章")
        
        cursor.execute(query, (current_id, user_id))
        article = cursor.fetchone()
        
        if article:
            # 转换为字典
            article_dict = {
                'id': article[0],
                'title': article[1],
                'content': article[2],
                'category': article[3],
                'tags': article[4],
                'created_at': article[5],
                'updated_at': article[6],
                'is_draft': article[9],
                'is_favorite': article[8],
                'is_top': 0,  # 表中没有is_top列，默认为0
                'views': article[7],
                'user_id': article[10]
            }
            print(f"找到文章: {article_dict['id']} - {article_dict['title']}")
            return jsonify({'article': article_dict})
        else:
            print("没有找到文章")
            return jsonify({'article': None})
    except Exception as e:
        print(f"错误: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/articles/<int:article_id>', methods=['GET'])
@login_required
def get_article(article_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM articles WHERE id = ? AND user_id = ?', (article_id, g.user_id))
    article = cursor.fetchone()
    if article:
        cursor.execute('UPDATE articles SET views = views + 1 WHERE id = ?', (article_id,))
        db.commit()
        return jsonify(dict(article))
    return jsonify({'error': '文章不存在'}), 404

@app.route('/api/articles', methods=['POST'])
@login_required
def create_article():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    category = data.get('category', '未分类')
    tags = data.get('tags', '')
    is_draft = data.get('is_draft', 0)

    if not is_draft and (not title or not content):
        return jsonify({'error': '标题和内容不能为空'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO articles (title, content, category, tags, is_draft, user_id) VALUES (?, ?, ?, ?, ?, ?)',
                  (title, content, category, tags, int(is_draft), g.user_id))
    article_id = cursor.lastrowid
    db.commit()
    return jsonify({'id': article_id, 'message': '创建成功'}), 201

@app.route('/api/articles/<int:article_id>', methods=['PUT'])
@login_required
def update_article(article_id):
    data = request.get_json()
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id FROM articles WHERE id = ? AND user_id = ?', (article_id, g.user_id))
    if not cursor.fetchone():
        return jsonify({'error': '文章不存在'}), 404

    updates = []
    params = []
    if 'title' in data:
        updates.append('title = ?')
        params.append(data['title'])
    if 'content' in data:
        updates.append('content = ?')
        params.append(data['content'])
    if 'category' in data:
        updates.append('category = ?')
        params.append(data['category'])
    if 'tags' in data:
        updates.append('tags = ?')
        params.append(data['tags'])
    if 'is_favorite' in data:
        updates.append('is_favorite = ?')
        params.append(int(data['is_favorite']))
    if 'is_draft' in data:
        updates.append('is_draft = ?')
        params.append(int(data['is_draft']))

    updates.append('updated_at = ?')
    params.append(datetime.now())
    params.append(article_id)
    params.append(g.user_id)

    cursor.execute(f"UPDATE articles SET {', '.join(updates)} WHERE id = ? AND user_id = ?", params)
    db.commit()
    return jsonify({'message': '更新成功'})

@app.route('/api/articles/<int:article_id>', methods=['DELETE'])
@login_required
def delete_article(article_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM articles WHERE id = ? AND user_id = ?', (article_id, g.user_id))
    if cursor.rowcount == 0:
        return jsonify({'error': '文章不存在'}), 404
    db.commit()
    return jsonify({'message': '删除成功'})

@app.route('/api/articles/<int:article_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(article_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE articles SET is_favorite = NOT is_favorite WHERE id = ? AND user_id = ?', (article_id, g.user_id))
    if cursor.rowcount == 0:
        return jsonify({'error': '文章不存在'}), 404
    cursor.execute('SELECT is_favorite FROM articles WHERE id = ?', (article_id,))
    is_favorite = cursor.fetchone()[0]
    db.commit()
    return jsonify({'is_favorite': bool(is_favorite)})

@app.route('/api/categories', methods=['GET'])
@login_required
def get_categories():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT c.*, COUNT(a.id) as article_count
        FROM categories c
        LEFT JOIN articles a ON c.name = a.category AND a.user_id = ?
        GROUP BY c.id
        ORDER BY c.created_at
    ''', (g.user_id,))
    categories = [dict(row) for row in cursor.fetchall()]
    return jsonify(categories)

@app.route('/api/categories', methods=['POST'])
@login_required
def create_category():
    data = request.get_json()
    name = data.get('name', '').strip()
    color = data.get('color', '#667eea')
    if not name:
        return jsonify({'error': '分类名称不能为空'}), 400
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('INSERT INTO categories (name, color) VALUES (?, ?)', (name, color))
        category_id = cursor.lastrowid
        db.commit()
        return jsonify({'id': category_id, 'message': '创建成功'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': '分类已存在'}), 400

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
    db.commit()
    return jsonify({'message': '删除成功'})

@app.route('/api/categories/<category_name>', methods=['DELETE'])
@login_required
def delete_category_by_name(category_name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM categories WHERE name = ?', (category_name,))
    db.commit()
    return jsonify({'message': '删除成功'})

@app.route('/api/stats', methods=['GET'])
@login_required
def get_stats():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM articles WHERE user_id = ?', (g.user_id,))
    total_articles = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM articles WHERE is_favorite = 1 AND user_id = ?', (g.user_id,))
    favorites = cursor.fetchone()[0]
    cursor.execute('SELECT SUM(views) FROM articles WHERE user_id = ?', (g.user_id,))
    total_views = cursor.fetchone()[0] or 0
    cursor.execute('SELECT COUNT(DISTINCT category) FROM articles WHERE user_id = ?', (g.user_id,))
    categories_used = cursor.fetchone()[0]
    return jsonify({
        'total_articles': total_articles,
        'favorites': favorites,
        'total_views': total_views,
        'categories_used': categories_used
    })

@app.route('/api/tags', methods=['GET'])
@login_required
def get_all_tags():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT tags FROM articles WHERE tags != "" AND user_id = ?', (g.user_id,))
    all_tags = []
    for row in cursor.fetchall():
        if row[0]:
            tags = [t.strip() for t in row[0].split(',') if t.strip()]
            all_tags.extend(tags)
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
    return jsonify([{'name': tag, 'count': count} for tag, count in sorted_tags])

@app.route('/api/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': '没有文件上传'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        filename = secure_filename(file.filename)
        # 生成唯一文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        # 返回相对路径
        url = f"/static/uploads/{filename}"
        return jsonify({'url': url, 'filename': filename})
    return jsonify({'error': '不支持的文件类型'}), 400

if __name__ == '__main__':
    init_db()
    print("=" * 60)
    print("  个人知识库服务已启动！")
    print("  访问地址: http://localhost:5000")
    print("  按 Ctrl+C 停止服务")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
