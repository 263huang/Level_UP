"""
文件名：roadmap_service.py
功能：提供学习路径（Roadmap）相关的数据库操作，包括主节点、分支节点的增删改查、进度统计、搜索等
主要内容：
    - Roadmap主节点/分支节点表的初始化
    - 主节点/分支节点的增删改查
    - Roadmap进度统计
    - Roadmap节点搜索
"""
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
db_path = os.getenv("DATABASE_URL", "levelup.db")

def get_conn():
    """
    获取数据库连接
    返回：sqlite3.Connection 对象
    """
    return sqlite3.connect(db_path, timeout=10)

def init_roadmap_db():
    """
    初始化Roadmap主节点和分支节点表
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS roadmap_main_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT '',
            remark TEXT DEFAULT '',
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS roadmap_branch_nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            main_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            target_id TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT DEFAULT '',
            remark TEXT DEFAULT '',
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_roadmap(user_id, target_id):
    """
    获取指定用户、指定目标的Roadmap结构（主节点及其分支节点）
    参数：user_id - 用户ID, target_id - 目标ID
    返回：主节点及其分支节点的嵌套列表
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM roadmap_main_nodes WHERE user_id=? AND target_id=? ORDER BY node_order ASC', (user_id, target_id))
    mains = c.fetchall()
    # 如果没有主节点，自动插入一个
    if not mains:
        now = datetime.now().isoformat()
        c.execute('''
            INSERT INTO roadmap_main_nodes (user_id, target_id, title, status, remark, created_at, updated_at)
            VALUES (?, ?, ?, 'todo', '', ?, ?)
        ''', (user_id, target_id, '第一个技能点', now, now))
        conn.commit()
        c.execute('SELECT * FROM roadmap_main_nodes WHERE user_id=? AND target_id=?', (user_id, target_id))
        mains = c.fetchall()
    result = []
    for main in mains:
        main_id = main[0]
        c.execute('SELECT * FROM roadmap_branch_nodes WHERE main_id=? AND target_id=?', (main_id, target_id))
        branches = c.fetchall()
        result.append({
            'id': main[0],
            'title': main[3],
            'status': main[4],
            'remark': main[5],
            'children': [
                {
                    'id': b[0],
                    'title': b[4],
                    'status': b[5],
                    'remark': b[6]
                } for b in branches
            ]
        })
    conn.close()
    return result

def get_roadmap_progress(user_id, target_id):
    """
    获取指定目标的Roadmap分支节点学习进度（已完成/总数）
    参数：user_id - 用户ID, target_id - 目标ID
    返回：分支节点学习率（0~1浮点数）
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM roadmap_branch_nodes WHERE user_id=? AND target_id=?', (user_id, target_id))
    total = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM roadmap_branch_nodes WHERE user_id=? AND target_id=? AND status='done'", (user_id, target_id))
    done = c.fetchone()[0]
    conn.close()
    if total == 0:
        return 0
    return round(done / total, 4)

def add_main_node(user_id, target_id, title):
    """
    新增主节点（追加到末尾）
    参数：user_id - 用户ID, target_id - 目标ID, title - 节点标题
    返回：True
    """
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        INSERT INTO roadmap_main_nodes (user_id, target_id, title, status, remark, created_at, updated_at)
        VALUES (?, ?, ?, 'todo', '', ?, ?)
    ''', (user_id, target_id, title, now, now))
    conn.commit()
    conn.close()
    return True

def add_main_node_at(user_id, target_id, title, insert_after_id=None):
    """
    在指定主节点后插入新主节点（带顺序）
    参数：user_id - 用户ID, target_id - 目标ID, title - 节点标题, insert_after_id - 插入位置的主节点ID
    返回：True
    """
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    # 兼容前端传递字符串 'null' 的情况
    if insert_after_id in (None, 'null', ''):
        c.execute('SELECT MAX(node_order) FROM roadmap_main_nodes WHERE user_id=? AND target_id=?', (user_id, target_id))
        row = c.fetchone()
        insert_order = (row[0] or 0) + 1
        print(f"[DEBUG] 追加主节点: title={title}, insert_after_id={insert_after_id}, insert_order={insert_order}")
    else:
        c.execute('SELECT node_order FROM roadmap_main_nodes WHERE id=?', (insert_after_id,))
        row = c.fetchone()
        if row:
            insert_order = row[0] + 1
        else:
            insert_order = 0
        print(f"[DEBUG] 插入主节点: title={title}, insert_after_id={insert_after_id}, insert_order={insert_order}")
    # 所有 >= insert_order 的 node_order +1
    c.execute('UPDATE roadmap_main_nodes SET node_order = node_order + 1 WHERE user_id=? AND target_id=? AND node_order >= ?', (user_id, target_id, insert_order))
    # 插入新节点
    c.execute('''
        INSERT INTO roadmap_main_nodes (user_id, target_id, title, status, remark, created_at, updated_at, node_order)
        VALUES (?, ?, ?, 'todo', '', ?, ?, ?)
    ''', (user_id, target_id, title, now, now, insert_order))
    conn.commit()
    conn.close()
    return True

def add_branch_node(main_id, target_id, title, user_id):
    """
    新增分支节点
    参数：main_id - 主节点ID, target_id - 目标ID, title - 节点标题, user_id - 用户ID
    返回：True
    """
    print(f"[DEBUG] add_branch_node 插入: main_id={main_id}, user_id={user_id}, target_id={target_id}, title={title}")
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        INSERT INTO roadmap_branch_nodes (main_id, user_id, target_id, title, status, remark, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'todo', '', ?, ?)
    ''', (main_id, user_id, target_id, title, now, now))
    conn.commit()
    conn.close()
    return True

def update_main_node(node_id, title, status, remark, target_id):
    """
    更新主节点信息
    参数：node_id - 主节点ID, title - 标题, status - 状态, remark - 备注, target_id - 目标ID
    返回：True
    """
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        UPDATE roadmap_main_nodes SET title=?, status=?, remark=?, updated_at=? WHERE id=? AND target_id=?
    ''', (title, status, remark, now, node_id, target_id))
    conn.commit()
    conn.close()
    return True

def update_branch_node(node_id, title, status, remark, target_id):
    """
    更新分支节点信息
    参数：node_id - 分支节点ID, title - 标题, status - 状态, remark - 备注, target_id - 目标ID
    返回：True
    """
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('''
        UPDATE roadmap_branch_nodes SET title=?, status=?, remark=?, updated_at=? WHERE id=? AND target_id=?
    ''', (title, status, remark, now, node_id, target_id))
    conn.commit()
    conn.close()
    return True

def delete_main_node(node_id, target_id):
    """
    删除主节点及其所有分支节点，并删除相关md文件
    参数：node_id - 主节点ID, target_id - 目标ID
    返回：True
    """
    conn = get_conn()
    c = conn.cursor()
    # 查找所有分支节点id
    c.execute('SELECT id FROM roadmap_branch_nodes WHERE main_id=? AND target_id=?', (node_id, target_id))
    branch_ids = [row[0] for row in c.fetchall()]
    # 删除分支节点
    c.execute('DELETE FROM roadmap_branch_nodes WHERE main_id=? AND target_id=?', (node_id, target_id))
    # 删除主节点
    c.execute('DELETE FROM roadmap_main_nodes WHERE id=? AND target_id=?', (node_id, target_id))
    # 删除 files 表中 mainId=该主节点id 的文件
    import json
    c.execute('SELECT id, tags FROM files')
    files = c.fetchall()
    files_to_delete = []
    for file_id, tags in files:
        try:
            t = json.loads(tags) if tags else {}
            if str(t.get('mainId')) == str(node_id):
                files_to_delete.append(file_id)
            elif 'branchId' in t and str(t['branchId']) in [str(bid) for bid in branch_ids]:
                files_to_delete.append(file_id)
        except Exception:
            continue
    for file_id in files_to_delete:
        c.execute('DELETE FROM files WHERE id=?', (file_id,))
    conn.commit()
    # 打印表内容（调试用）
    print("==== roadmap_main_nodes ====")
    for row in c.execute('SELECT * FROM roadmap_main_nodes'):
        print(row)
    print("==== roadmap_branch_nodes ====")
    for row in c.execute('SELECT * FROM roadmap_branch_nodes'):
        print(row)
    print("==== files ====")
    for row in c.execute('SELECT id, name, tags FROM files'):
        print(row)
    conn.close()
    return True

def delete_branch_node(node_id, target_id):
    """
    删除分支节点，并删除相关md文件
    参数：node_id - 分支节点ID, target_id - 目标ID
    返回：True
    """
    conn = get_conn()
    c = conn.cursor()
    # 删除分支节点
    c.execute('DELETE FROM roadmap_branch_nodes WHERE id=? AND target_id=?', (node_id, target_id))
    # 删除 files 表中 branchId=该分支节点id 的文件
    import json
    c.execute('SELECT id, tags FROM files')
    files = c.fetchall()
    files_to_delete = []
    for file_id, tags in files:
        try:
            t = json.loads(tags) if tags else {}
            if str(t.get('branchId')) == str(node_id):
                files_to_delete.append(file_id)
        except Exception:
            continue
    for file_id in files_to_delete:
        c.execute('DELETE FROM files WHERE id=?', (file_id,))
    conn.commit()
    # 打印表内容（调试用）
    print("==== roadmap_main_nodes ====")
    for row in c.execute('SELECT * FROM roadmap_main_nodes'):
        print(row)
    print("==== roadmap_branch_nodes ====")
    for row in c.execute('SELECT * FROM roadmap_branch_nodes'):
        print(row)
    print("==== files ====")
    for row in c.execute('SELECT id, name, tags FROM files'):
        print(row)
    conn.close()
    return True

def search_roadmap_nodes(keyword, user_id):
    """
    搜索Roadmap主节点和分支节点（标题模糊匹配）
    参数：keyword - 关键词, user_id - 用户ID
    返回：节点字典列表（含主/分类型）
    """
    conn = get_conn()
    c = conn.cursor()
    # 搜索主节点
    c.execute("SELECT id, title, target_id FROM roadmap_main_nodes WHERE user_id=? AND title LIKE ?", (user_id, f'%{keyword}%'))
    main_nodes = [
        {"id": row[0], "title": row[1], "target_id": row[2], "node_type": "main"}
        for row in c.fetchall()
    ]
    # 搜索分支节点
    c.execute("SELECT id, title, target_id FROM roadmap_branch_nodes WHERE user_id=? AND title LIKE ?", (user_id, f'%{keyword}%'))
    branch_nodes = [
        {"id": row[0], "title": row[1], "target_id": row[2], "node_type": "branch"}
        for row in c.fetchall()
    ]
    conn.close()
    return main_nodes + branch_nodes
