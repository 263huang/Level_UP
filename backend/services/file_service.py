"""
文件名：file_service.py
功能：提供文件（md笔记）相关的数据库操作，包括增删改查等
主要内容：
    - 文件表的初始化
    - 文件的增删改查
    - 文件内容的获取
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

def init_file_db(db_path=None):
    if db_path is None:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        db_path = os.getenv("DATABASE_URL", "levelup.db")
    conn = sqlite3.connect(db_path, timeout=10)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS files
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 content TEXT,
                 parent_id INTEGER,
                 is_dir INTEGER DEFAULT 0,
                 tags TEXT DEFAULT '',
                 user_id TEXT DEFAULT '',
                 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def get_files(user_id):
    """
    获取指定用户的所有文件列表
    参数：user_id - 用户ID
    返回：文件字典列表
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, name, parent_id, is_dir, tags FROM files WHERE user_id=? ORDER BY is_dir DESC, name", (user_id,))
    files = [{"id": row[0], "name": row[1], "parent_id": row[2], "is_dir": bool(row[3]), "tags": row[4]} for row in c.fetchall()]
    conn.close()
    return files

def add_file(name, content, tags, user_id):
    """
    新增文件
    参数：name-文件名, content-内容, tags-标签, user_id-用户ID
    返回：(文件数据, 错误信息)
    """
    if not name.endswith('.md'):
        name += '.md'
    conn = get_conn()
    c = conn.cursor()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # 检查重名
    c.execute("SELECT id FROM files WHERE name = ? AND user_id = ?", (name, user_id))
    existing_file = c.fetchone()
    if existing_file:
        conn.close()
        return None, "文件已存在"
    c.execute("""
        INSERT INTO files (name, content, tags, user_id, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, content, tags, user_id, current_time, current_time))
    file_id = c.lastrowid
    conn.commit()
    c.execute("SELECT * FROM files WHERE id = ?", (file_id,))
    file_data = c.fetchone()
    conn.close()
    return file_data, None

def get_file_content(file_id):
    """
    获取指定文件内容
    参数：file_id - 文件ID
    返回：文件元组
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, name, content, is_dir, parent_id, tags 
        FROM files 
        WHERE id = ?
    """, (file_id,))
    result = c.fetchone()
    conn.close()
    return result

def update_file(file_id, name, content, tags, user_id):
    """
    更新文件内容
    参数：file_id-文件ID, name-文件名, content-内容, tags-标签, user_id-用户ID
    返回：(文件数据, 错误信息)
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM files WHERE id = ? AND user_id = ?", (file_id, user_id))
    if not c.fetchone():
        conn.close()
        return None, "文件不存在或无权限"
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updates = []
    params = []
    if name:
        if not name.endswith('.md'):
            name += '.md'
        updates.append("name = ?")
        params.append(name)
    if content:
        updates.append("content = ?")
        params.append(content)
    if tags is not None:
        updates.append("tags = ?")
        params.append(tags)
    updates.append("updated_at = ?")
    params.append(current_time)
    sql = f"UPDATE files SET {', '.join(updates)} WHERE id = ? AND user_id = ?"
    params.append(file_id)
    params.append(user_id)
    c.execute(sql, params)
    conn.commit()
    c.execute("SELECT * FROM files WHERE id = ?", (file_id,))
    file_data = c.fetchone()
    conn.close()
    return file_data, None

def delete_file(file_id, user_id):
    """
    删除文件
    参数：file_id-文件ID, user_id-用户ID
    返回：(文件名, 错误信息)
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT name FROM files WHERE id = ? AND user_id = ?", (file_id, user_id))
    file_name = c.fetchone()
    file_name = file_name[0] if file_name else "未知文件"
    c.execute("DELETE FROM files WHERE id = ? AND user_id = ?", (file_id, user_id))
    conn.commit()
    conn.close()
    return file_name, None
