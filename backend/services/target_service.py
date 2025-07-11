"""
文件名：target_service.py
功能：提供学习目标相关的数据库操作，包括目标的增删改查、搜索等
主要内容：
    - 学习目标表的初始化
    - 学习目标的增删改查
    - 学习目标的搜索
"""
import sqlite3
from datetime import datetime

def init_target_db():
    """
    初始化学习目标数据库表
    """
    conn = sqlite3.connect('levelup.db')
    c = conn.cursor()
    # 创建学习目标表
    c.execute('''
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            progress REAL DEFAULT 0,
            tags TEXT,
            update_time TEXT,
            user_id TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_target(title, progress, tags, user_id):
    """
    添加新的学习目标，并自动创建初始roadmap主节点
    参数：title-目标名, progress-进度, tags-标签列表, user_id-用户ID
    返回：(True/False, 信息)
    """
    try:
        conn = sqlite3.connect('levelup.db')
        c = conn.cursor()
        tags_str = ','.join(tags)
        update_time = datetime.now().strftime('%Y-%m-%d')
        c.execute('''
            INSERT INTO targets (title, progress, tags, update_time, user_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, progress, tags_str, update_time, user_id))
        target_id = c.lastrowid
        # 自动为新目标创建roadmap主节点
        now = datetime.now().isoformat()
        c.execute('''
            INSERT INTO roadmap_main_nodes (user_id, target_id, title, status, remark, created_at, updated_at)
            VALUES (?, ?, ?, 'todo', '', ?, ?)
        ''', (user_id, target_id, '第一个技能点', now, now))
        conn.commit()
        conn.close()
        return True, "添加成功"
    except Exception as e:
        return False, f"添加失败: {str(e)}"

def get_targets(user_id):
    """
    获取指定用户的所有学习目标
    参数：user_id-用户ID
    返回：目标字典列表
    """
    try:
        conn = sqlite3.connect('levelup.db')
        c = conn.cursor()
        c.execute('SELECT * FROM targets WHERE user_id = ?', (user_id,))
        targets = c.fetchall()
        # 将数据库结果转换为字典列表
        result = []
        for target in targets:
            result.append({
                'id': target[0],
                'title': target[1],
                'progress': target[2],
                'tags': target[3].split(',') if target[3] else [],
                'update': target[4],
                'user_id': target[5]
            })
        conn.close()
        return result
    except Exception as e:
        print(f"获取学习目标失败: {str(e)}")
        return []

def update_target(target_id, title, progress, tags, user_id):
    """
    更新学习目标
    参数：target_id-目标ID, title-目标名, progress-进度, tags-标签列表, user_id-用户ID
    返回：(True/False, 信息)
    """
    try:
        conn = sqlite3.connect('levelup.db')
        c = conn.cursor()
        # 确保只能更新自己的学习目标
        c.execute('SELECT user_id FROM targets WHERE id = ?', (target_id,))
        result = c.fetchone()
        if not result or result[0] != user_id:
            return False, "无权更新此学习目标"
        tags_str = ','.join(tags)
        update_time = datetime.now().strftime('%Y-%m-%d')
        c.execute('''
            UPDATE targets 
            SET title = ?, progress = ?, tags = ?, update_time = ?
            WHERE id = ? AND user_id = ?
        ''', (title, progress, tags_str, update_time, target_id, user_id))
        conn.commit()
        conn.close()
        return True, "更新成功"
    except Exception as e:
        return False, f"更新失败: {str(e)}"

def delete_target(target_id, user_id):
    """
    删除学习目标
    参数：target_id-目标ID, user_id-用户ID
    返回：(True/False, 信息)
    """
    try:
        conn = sqlite3.connect('levelup.db')
        c = conn.cursor()
        # 确保只能删除自己的学习目标
        c.execute('SELECT user_id FROM targets WHERE id = ?', (target_id,))
        result = c.fetchone()
        if not result or result[0] != user_id:
            return False, "无权删除此学习目标"
        c.execute('DELETE FROM targets WHERE id = ? AND user_id = ?', (target_id, user_id))
        conn.commit()
        conn.close()
        return True, "删除成功"
    except Exception as e:
        return False, f"删除失败: {str(e)}"

def search_targets(query, user_id):
    """
    搜索学习目标（标题或标签模糊匹配）
    参数：query-搜索关键词, user_id-用户ID
    返回：目标字典列表
    """
    try:
        conn = sqlite3.connect('levelup.db')
        c = conn.cursor()
        # 在标题和标签中搜索
        search_pattern = f'%{query}%'
        c.execute('''
            SELECT * FROM targets 
            WHERE user_id = ? AND (title LIKE ? OR tags LIKE ?)
        ''', (user_id, search_pattern, search_pattern))
        targets = c.fetchall()
        # 将数据库结果转换为字典列表
        result = []
        for target in targets:
            result.append({
                'id': target[0],
                'title': target[1],
                'progress': target[2],
                'tags': target[3].split(',') if target[3] else [],
                'update': target[4],
                'user_id': target[5]
            })
        conn.close()
        return result
    except Exception as e:
        print(f"搜索学习目标失败: {str(e)}")
        return [] 