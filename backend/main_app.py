"""
文件名：main_app.py
功能：LevelUP主Flask应用，整合用户、目标、roadmap、md、todo等子模块，提供统一后端接口
主要内容：
    - 用户注册、登录、登出、登录校验
    - 学习目标的增删改查与搜索
    - Blueprint注册（roadmap、md、todo子模块）
    - favicon路由
"""
from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import os
import sys
import sqlite3

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.sign_in_service import init_user_db, add_user, verify_user
from backend.services.target_service import init_target_db, add_target, get_targets, update_target, delete_target, search_targets
from backend.roadmap_app import roadmap_app
from backend.md_app import md_app, init_db
from backend.todo_app import todo_app
from backend.services.roadmap_service import init_roadmap_db

app = Flask(__name__)
app.secret_key = os.urandom(24)  # 用于session加密

# 配置CORS
CORS(app, supports_credentials=True)

# 修改session配置
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 改为Lax
app.config['SESSION_COOKIE_SECURE'] = False    # 开发环境设为False
app.config['SESSION_COOKIE_HTTPONLY'] = True   # 增加安全性
# app.config['SESSION_COOKIE_DOMAIN'] = 'localhost'  # 注释掉，避免跨端口 cookie 问题

# 初始化数据库
init_user_db()
init_target_db()
init_db()
init_roadmap_db()

def ensure_node_order_column():
    """
    数据库迁移：确保roadmap_main_nodes表有node_order字段
    """
    conn = sqlite3.connect('levelup.db')  # 路径要和你实际用的一致
    c = conn.cursor()
    # 检查字段是否存在
    c.execute("PRAGMA table_info(roadmap_main_nodes);")
    columns = [row[1] for row in c.fetchall()]
    if 'node_order' not in columns:
        print("[DB MIGRATION] Adding node_order column to roadmap_main_nodes...")
        c.execute('ALTER TABLE roadmap_main_nodes ADD COLUMN node_order INTEGER DEFAULT 0;')
        conn.commit()
        print("[DB MIGRATION] node_order column added.")
    conn.close()

ensure_node_order_column()

# 添加 favicon 路由，避免 404 报错
@app.route('/favicon.ico')
def favicon():
    """
    返回favicon.ico，防止浏览器404
    """
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# 登录验证装饰器
def login_required(f):
    """
    登录校验装饰器，未登录则返回401
    """
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': '请先登录'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/register', methods=['POST'])
def register():
    """
    用户注册接口
    参数：username, password
    返回：注册结果
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'error': '用户名和密码不能为空'})
    
    success, message = add_user(username, password)
    if success:
        return jsonify({'success': True, 'message': '注册成功'})
    else:
        return jsonify({'success': False, 'error': message})

@app.route('/login', methods=['POST'])
def login():
    """
    用户登录接口
    参数：username, password
    返回：登录结果，成功时写入session
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    print(f"收到用户名: [{username}], 密码: [{password}]")  # 调试日志
    if not username or not password:
        return jsonify({'success': False, 'error': '用户名和密码不能为空'})
    
    success, message = verify_user(username, password)
    if success:
        session['user_id'] = username
        return jsonify({
            'success': True, 
            'message': '登录成功',
            'user': {'username': username}
        })
    else:
        return jsonify({'success': False, 'error': message})

@app.route('/logout', methods=['POST'])
def logout():
    """
    用户登出接口，清除session
    返回：登出结果
    """
    session.pop('user_id', None)
    return jsonify({'success': True, 'message': '退出成功'})

@app.route('/check_login', methods=['GET'])
def check_login():
    """
    检查当前session是否已登录
    返回：登录状态
    """
    if 'user_id' in session:
        return jsonify({
            'success': True, 
            'user': {'username': session['user_id']}
        })
    return jsonify({'success': False, 'error': '未登录'})

@app.route('/targets', methods=['GET'])
@login_required
def get_user_targets():
    """
    获取当前用户的所有学习目标
    返回：目标列表
    """
    user_id = session['user_id']
    targets = get_targets(user_id)
    return jsonify(targets)

@app.route('/targets', methods=['POST'])
@login_required
def create_target():
    """
    新建学习目标
    参数：title, progress, tags
    返回：操作结果
    """
    user_id = session['user_id']
    data = request.get_json()
    
    title = data.get('title')
    progress = data.get('progress', 0)
    tags = data.get('tags', [])
    
    if not title:
        return jsonify({'success': False, 'error': '标题不能为空'})
    
    success, message = add_target(title, progress, tags, user_id)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message})

@app.route('/targets/<int:target_id>', methods=['PUT'])
@login_required
def update_user_target(target_id):
    """
    更新学习目标
    参数：title, progress, tags
    返回：操作结果
    """
    user_id = session['user_id']
    data = request.get_json()
    
    title = data.get('title')
    progress = data.get('progress', 0)
    tags = data.get('tags', [])
    
    if not title:
        return jsonify({'success': False, 'error': '标题不能为空'})
    
    success, message = update_target(target_id, title, progress, tags, user_id)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message})

@app.route('/targets/<int:target_id>', methods=['DELETE'])
@login_required
def delete_user_target(target_id):
    """
    删除学习目标
    返回：操作结果
    """
    user_id = session['user_id']
    success, message = delete_target(target_id, user_id)
    if success:
        return jsonify({'success': True, 'message': message})
    else:
        return jsonify({'success': False, 'error': message})

@app.route('/search', methods=['GET'])
@login_required
def search_user_targets():
    """
    搜索学习目标（标题或标签模糊匹配）
    参数：query
    返回：目标列表
    """
    user_id = session['user_id']
    query = request.args.get('query', '')
    
    if not query:
        targets = get_targets(user_id)
    else:
        targets = search_targets(query, user_id)
    
    return jsonify(targets)

# 注册子模块蓝图
app.register_blueprint(roadmap_app)
app.register_blueprint(md_app)
app.register_blueprint(todo_app)

if __name__ == '__main__':
    # 启动主Flask应用
    app.run(port=5000, debug=True)
