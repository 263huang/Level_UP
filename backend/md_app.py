"""
文件名：md_app.py
功能：提供md文件（笔记）相关的Flask路由接口，包括文件的增删改查、搜索、roadmap进度获取等
主要内容：
    - md文件的RESTful接口
    - 文件内容获取与保存
    - 文件搜索与roadmap进度接口
"""
# app.py 完整修改版本

from flask import Blueprint, render_template, request, jsonify
import sqlite3
from flask_cors import CORS
from backend.services.file_service import get_files, add_file, get_file_content, update_file, delete_file, init_file_db
from backend.services.roadmap_service import get_roadmap_progress

md_app = Blueprint('md_app', __name__)
CORS(md_app, supports_credentials=True)

# 初始化数据库
# 用于外部调用
# def init_db():
#     init_file_db()
def init_db():
    """
    初始化文件数据库表
    """
    init_file_db()

# 获取文件树页面
@md_app.route('/')
def index():
    """
    渲染md编辑器主页面
    """
    return render_template('index_md.html')

# API: 获取文件列表
@md_app.route('/api/files', methods=['GET'])
def get_files_route():
    """
    获取指定用户的所有文件列表
    参数：user_id
    返回：文件列表
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "缺少user_id"}), 400
    try:
        files = get_files(user_id)
        return jsonify({"success": True, "data": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# API: 创建保存文件/目录
@md_app.route('/api/files', methods=['POST'])
def save_or_create_file():
    """
    新建或保存文件
    参数：name, content, tags, user_id
    返回：文件信息
    """
    data = request.json
    name = data.get('name')
    content = data.get('content', '')
    tags = data.get('tags', '')
    user_id = data.get('user_id')
    if not name or not user_id:
        return jsonify({"success": False, "error": "文件名和user_id不能为空"}), 400
    try:
        file_data, err = add_file(name, content, tags, user_id)
        if err:
            return jsonify({"success": False, "error": err}), 409
        return jsonify({
            "success": True,
            "message": "文件创建成功",
            "data": {
                "id": file_data[0],
                "name": file_data[1],
                "content": file_data[2],
                "parent_id": file_data[3],
                "is_dir": bool(file_data[4]),
                "tags": file_data[5],
                "user_id": file_data[6],
                "created_at": file_data[7],
                "updated_at": file_data[8]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"创建文件时出错: {str(e)}"}), 500

# API: 获取文件内容
@md_app.route('/api/files/<int:file_id>', methods=['GET'])
def get_file_content_route(file_id):
    """
    获取指定文件内容
    参数：file_id
    返回：文件内容
    """
    try:
        result = get_file_content(file_id)
        if not result:
            return jsonify({"success": False, "error": "文件不存在"}), 404
        file_id, name, content, is_dir, parent_id, tags = result
        return jsonify({
            "success": True,
            "data": {
                "id": file_id,
                "name": name,
                "content": content or "",
                "is_dir": bool(is_dir),
                "parent_id": parent_id,
                "tags": tags
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"获取文件内容失败: {str(e)}"}), 500

# API: 更新文件内容
@md_app.route('/api/files/<int:file_id>', methods=['PUT'])
def update_file_content_route(file_id):
    """
    更新指定文件内容
    参数：file_id, name, content, tags, user_id
    返回：文件信息
    """
    try:
        data = request.get_json()
        name = data.get('name')
        content = data.get('content')
        tags = data.get('tags')
        user_id = data.get('user_id')
        if not user_id:
            return jsonify({"success": False, "error": "缺少user_id"}), 400
        if not name and not content and not tags:
            return jsonify({"success": False, "error": "必须提供name、content或tags字段"}), 400
        file_data, err = update_file(file_id, name, content, tags, user_id)
        if err:
            return jsonify({"success": False, "error": err}), 404
        return jsonify({
            "success": True,
            "message": "文件更新成功",
            "data": {
                "id": file_data[0],
                "name": file_data[1],
                "content": file_data[2],
                "parent_id": file_data[3],
                "is_dir": bool(file_data[4]),
                "tags": file_data[5],
                "user_id": file_data[6],
                "created_at": file_data[7],
                "updated_at": file_data[8]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# API: 删除文件/目录
@md_app.route('/api/files/<int:file_id>', methods=['DELETE'])
def delete_file_route(file_id):
    """
    删除指定文件
    参数：file_id, user_id
    返回：操作结果
    """
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"success": False, "error": "缺少user_id"}), 400
    try:
        file_name, err = delete_file(file_id, user_id)
        if err:
            return jsonify({"success": False, "error": err}), 500
        return jsonify({
                "success": True,
                "message": "文件删除成功",
                "data": {
                    "name": file_name
                }
            })
    except Exception as e:
        return jsonify({"success": False, "error": f"删除文件失败: {str(e)}"}), 500

# API: 关键词模糊搜索md文件名
@md_app.route('/api/files/search', methods=['GET'])
def search_files():
    """
    搜索指定用户的md文件（按文件名模糊匹配）
    参数：user_id, q
    返回：文件列表
    """
    user_id = request.args.get('user_id')
    keyword = request.args.get('q', '')
    if not user_id:
        return jsonify({"success": False, "error": "缺少user_id"}), 400
    try:
        conn = sqlite3.connect('levelup.db')
        c = conn.cursor()
        c.execute("SELECT id, name, tags FROM files WHERE user_id=? AND name LIKE ?", (user_id, f'%{keyword}%'))
        files = [{"id": row[0], "name": row[1], "tags": row[2]} for row in c.fetchall()]
        conn.close()
        return jsonify({"success": True, "data": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# API: 获取roadmap进度
@md_app.route('/api/roadmap_progress', methods=['GET'])
def get_roadmap_progress_route():
    """
    获取指定目标的roadmap学习进度
    参数：user_id, target_id
    返回：progress（0~1）
    """
    user_id = request.args.get('user_id')
    target_id = request.args.get('target_id')
    if not user_id or not target_id:
        return jsonify({'success': False, 'error': '缺少user_id或target_id'}), 400
    try:
        progress = get_roadmap_progress(user_id, target_id)
        return jsonify({'success': True, 'progress': progress})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# 临时添加测试路由
@md_app.route('/test-db')
def test_db():
    """
    测试数据库连接和文件表内容
    """
    try:
        conn = sqlite3.connect('levelup.db')
        c = conn.cursor()
        c.execute("SELECT id, name, is_dir FROM files")
        files = c.fetchall()
        conn.close()
        return jsonify({"success": True, "data": files})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500