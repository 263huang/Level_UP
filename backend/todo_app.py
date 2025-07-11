"""
文件名：todo_app.py
功能：提供待办事项（Todo）相关的Flask路由接口，包括增删改查
主要内容：
    - 待办事项RESTful接口
"""
from flask import Blueprint, request, jsonify, session
from backend.services.todo_service import init_todo_db, get_todos, add_todo, update_todo, delete_todo

todo_app = Blueprint('todo_app', __name__)

# 初始化数据库表
init_todo_db()

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

@todo_app.route('/todos', methods=['GET'])
@login_required
def api_get_todos():
    """
    获取当前用户的所有待办事项
    返回：待办事项列表
    """
    user_id = session['user_id']
    todos = get_todos(user_id)
    return jsonify({'success': True, 'data': todos})

@todo_app.route('/todos', methods=['POST'])
@login_required
def api_add_todo():
    """
    新增待办事项
    参数：text
    返回：操作结果
    """
    user_id = session['user_id']
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'success': False, 'error': '待办内容不能为空'})
    add_todo(user_id, text)
    return jsonify({'success': True})

@todo_app.route('/todos/<int:todo_id>', methods=['PUT'])
@login_required
def api_update_todo(todo_id):
    """
    更新待办事项完成状态
    参数：completed
    返回：操作结果
    """
    user_id = session['user_id']
    data = request.get_json()
    completed = data.get('completed', False)
    update_todo(todo_id, completed, user_id)
    return jsonify({'success': True})

@todo_app.route('/todos/<int:todo_id>', methods=['DELETE'])
@login_required
def api_delete_todo(todo_id):
    """
    删除待办事项
    返回：操作结果
    """
    user_id = session['user_id']
    delete_todo(todo_id, user_id)
    return jsonify({'success': True}) 