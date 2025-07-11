"""
文件名：sign_in_service.py
功能：提供用户注册、登录相关的数据库操作
主要内容：
    - 用户表的初始化
    - 用户注册
    - 用户登录验证
"""
import sqlite3
from dotenv import load_dotenv
import os

load_dotenv()
db_path = os.getenv("DATABASE_URL", "levelup.db")

def init_user_db():
    """
    初始化用户表
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password):
    """
    新增用户（注册）
    参数：username - 用户名, password - 密码
    返回：(True/False, 信息)
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return False, "用户名已存在"
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True, "注册成功"

def verify_user(username, password):
    """
    验证用户登录
    参数：username - 用户名, password - 密码
    返回：(True/False, 信息)
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    if c.fetchone():
        conn.close()
        return True, "登录成功"
    else:
        conn.close()
        return False, "用户名或密码错误"

def update_username(old_username, new_username):
    """
    修改用户名，并同步更新所有相关表的 user_id 字段
    参数：old_username - 原用户名, new_username - 新用户名
    返回：(True/False, 信息)
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # 检查新用户名是否已存在
    c.execute("SELECT id FROM users WHERE username=?", (new_username,))
    if c.fetchone():
        conn.close()
        return False, "新用户名已存在"
    # 更新 users 表
    c.execute("UPDATE users SET username=? WHERE username=?", (new_username, old_username))
    # 同步更新所有业务表的 user_id 字段
    c.execute("UPDATE targets SET user_id=? WHERE user_id=?", (new_username, old_username))
    c.execute("UPDATE roadmap_main_nodes SET user_id=? WHERE user_id=?", (new_username, old_username))
    c.execute("UPDATE roadmap_branch_nodes SET user_id=? WHERE user_id=?", (new_username, old_username))
    c.execute("UPDATE files SET user_id=? WHERE user_id=?", (new_username, old_username))
    c.execute("UPDATE todos SET user_id=? WHERE user_id=?", (new_username, old_username))
    # 新增：同步更新files表tags字段内的userId
    import json
    c.execute("SELECT id, tags FROM files WHERE user_id=?", (new_username,))
    files = c.fetchall()
    for file_id, tags in files:
        if not tags:
            continue
        try:
            t = json.loads(tags)
            if t.get('userId') == old_username:
                t['userId'] = new_username
                c.execute("UPDATE files SET tags=? WHERE id=?", (json.dumps(t, ensure_ascii=False), file_id))
        except Exception:
            continue
    conn.commit()
    conn.close()
    return True, "用户名修改成功"

def update_password(username, old_password, new_password):
    """
    修改密码
    参数：username - 用户名, old_password - 旧密码, new_password - 新密码
    返回：(True/False, 信息)
    """
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    # 校验旧密码
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, old_password))
    if not c.fetchone():
        conn.close()
        return False, "原密码错误"
    # 更新密码
    c.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
    conn.commit()
    conn.close()
    return True, "密码修改成功"