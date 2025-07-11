"""
文件名：todo_service.py
功能：提供待办事项（Todo）相关的数据库操作，包括增删改查等
主要内容：
    - 待办事项表的初始化
    - 待办事项的增删改查
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

def init_todo_db(db_path=None):
    if db_path is None:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        db_path = os.getenv("DATABASE_URL", "levelup.db")
    conn = sqlite3.connect(db_path, timeout=10)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            text TEXT NOT NULL,
            completed INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_todos(user_id):
    """
    获取指定用户的所有待办事项
    参数：user_id - 用户ID
    返回：待办事项字典列表
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT id, text, completed, created_at FROM todos WHERE user_id=? ORDER BY id DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [
        {'id': row[0], 'text': row[1], 'completed': bool(row[2]), 'created_at': row[3]}
        for row in rows
    ]

def add_todo(user_id, text):
    """
    新增待办事项
    参数：user_id - 用户ID, text - 事项内容
    返回：True
    """
    conn = get_conn()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('INSERT INTO todos (user_id, text, completed, created_at) VALUES (?, ?, 0, ?)', (user_id, text, now))
    conn.commit()
    conn.close()
    return True

def update_todo(todo_id, completed, user_id):
    """
    更新待办事项的完成状态
    参数：todo_id - 待办ID, completed - 是否完成, user_id - 用户ID
    返回：True
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE todos SET completed=? WHERE id=? AND user_id=?', (int(completed), todo_id, user_id))
    conn.commit()
    conn.close()
    return True

def delete_todo(todo_id, user_id):
    """
    删除待办事项
    参数：todo_id - 待办ID, user_id - 用户ID
    返回：True
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute('DELETE FROM todos WHERE id=? AND user_id=?', (todo_id, user_id))
    conn.commit()
    conn.close()
    return True 