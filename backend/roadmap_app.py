"""
文件名：roadmap_app.py
功能：提供Roadmap相关的Flask路由接口，包括主/分节点的增删改查、搜索、节点列表等
主要内容：
    - Roadmap主节点/分支节点的RESTful接口
    - Roadmap节点搜索接口
    - Roadmap节点列表接口
"""
from flask import Blueprint, request, jsonify
import sqlite3
from backend.services.roadmap_service import (
    get_roadmap, add_branch_node,
    update_main_node, update_branch_node, delete_main_node, delete_branch_node,
    search_roadmap_nodes  # 新增
)

roadmap_app = Blueprint('roadmap_app', __name__)

@roadmap_app.route('/roadmap', methods=['GET'])
def api_get_roadmap():
    """
    获取指定用户、目标的Roadmap结构
    参数：user_id, target_id
    返回：主节点及分支节点嵌套结构
    """
    user_id = request.args.get('user_id')
    target_id = request.args.get('target_id', 'testtarget')
    return jsonify(get_roadmap(user_id, target_id))

@roadmap_app.route('/roadmap/main', methods=['POST'])
def api_add_main_node():
    """
    新增主节点（支持插入到指定节点后）
    参数：user_id, title, target_id, insert_after_id
    返回：操作结果
    """
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    target_id = data.get('target_id', 'testtarget')
    insert_after_id = data.get('insert_after_id')  # 新增
    if not user_id or not title or not target_id:
        return jsonify({'success': False, 'error': 'user_id、技能点标题和目标ID不能为空'})
    from backend.services.roadmap_service import add_main_node_at
    add_main_node_at(user_id, target_id, title, insert_after_id)
    return jsonify({'success': True})

@roadmap_app.route('/roadmap/branch', methods=['POST'])
def api_add_branch_node():
    """
    新增分支节点
    参数：user_id, main_id, title, target_id
    返回：操作结果
    """
    data = request.get_json()
    user_id = data.get('user_id')
    main_id = data.get('main_id')
    title = data.get('title')
    target_id = data.get('target_id', 'testtarget')
    print(f"[DEBUG] /roadmap/branch 参数: main_id={main_id}, target_id={target_id}, title={title}, user_id={user_id}")
    if not user_id or not main_id or not title or not target_id:
        return jsonify({'success': False, 'error': 'user_id、分技能点参数不完整'})
    add_branch_node(main_id, target_id, title, user_id)
    return jsonify({'success': True})

@roadmap_app.route('/roadmap/main/<int:node_id>', methods=['PUT'])
def api_update_main_node(node_id):
    """
    更新主节点信息
    参数：node_id, user_id, title, status, remark, target_id
    返回：操作结果
    """
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    status = data.get('status')
    remark = data.get('remark', '')
    target_id = data.get('target_id', 'testtarget')
    if not user_id or not title or not status or not target_id:
        return jsonify({'success': False, 'error': 'user_id、参数不完整'})
    update_main_node(node_id, title, status, remark, target_id)
    return jsonify({'success': True})

@roadmap_app.route('/roadmap/branch/<int:node_id>', methods=['PUT'])
def api_update_branch_node(node_id):
    """
    更新分支节点信息
    参数：node_id, user_id, title, status, remark, target_id
    返回：操作结果
    """
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    status = data.get('status')
    remark = data.get('remark', '')
    target_id = data.get('target_id', 'testtarget')
    if not user_id or not title or not status or not target_id:
        return jsonify({'success': False, 'error': 'user_id、参数不完整'})
    update_branch_node(node_id, title, status, remark, target_id)
    return jsonify({'success': True})

@roadmap_app.route('/roadmap/main/<int:node_id>', methods=['DELETE'])
def api_delete_main_node(node_id):
    """
    删除主节点
    参数：node_id, user_id, target_id
    返回：操作结果
    """
    user_id = request.args.get('user_id')
    target_id = request.args.get('target_id', 'testtarget')
    delete_main_node(node_id, target_id)
    return jsonify({'success': True})

@roadmap_app.route('/roadmap/branch/<int:node_id>', methods=['DELETE'])
def api_delete_branch_node(node_id):
    """
    删除分支节点
    参数：node_id, user_id, target_id
    返回：操作结果
    """
    user_id = request.args.get('user_id')
    target_id = request.args.get('target_id', 'testtarget')
    delete_branch_node(node_id, target_id)
    return jsonify({'success': True})

@roadmap_app.route('/roadmap/search', methods=['GET'])
def api_search_roadmap_nodes():
    """
    搜索Roadmap节点（主/分）
    参数：user_id, q
    返回：节点列表
    """
    user_id = request.args.get('user_id')
    keyword = request.args.get('q', '')
    if not user_id:
        return jsonify({'success': False, 'error': '缺少user_id'}), 400
    results = search_roadmap_nodes(keyword, user_id)
    return jsonify({'success': True, 'data': results})

@roadmap_app.route('/roadmap/get_main_nodes')
def get_main_nodes():
    """
    获取指定目标下的所有主节点列表
    参数：target_id
    返回：主节点列表
    """
    target_id = request.args.get('target_id')
    if not target_id:
        return jsonify({'success': False, 'error': '缺少target_id'})
    conn = sqlite3.connect('levelup.db')
    c = conn.cursor()
    c.execute('SELECT id, title FROM roadmap_main_nodes WHERE target_id=?', (target_id,))
    nodes = [{'id': row[0], 'title': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'data': nodes})

@roadmap_app.route('/roadmap/get_branch_nodes')
def get_branch_nodes():
    """
    获取指定主节点下的所有分支节点列表
    参数：main_id
    返回：分支节点列表
    """
    main_id = request.args.get('main_id')
    if not main_id:
        return jsonify({'success': False, 'error': '缺少main_id'})
    conn = sqlite3.connect('levelup.db')
    c = conn.cursor()
    c.execute('SELECT id, title FROM roadmap_branch_nodes WHERE main_id=?', (main_id,))
    nodes = [{'id': row[0], 'title': row[1]} for row in c.fetchall()]
    conn.close()
    return jsonify({'success': True, 'data': nodes}) 