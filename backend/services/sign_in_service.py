"""
文件名：sign_in_service.py
功能：提供用户注册、登录相关的数据库操作
主要内容：
    - 用户表的初始化
    - 用户注册
    - 用户登录验证
"""
import sqlite3

def init_user_db():
    """
    初始化用户表
    """
    conn = sqlite3.connect('levelup.db')
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
    conn = sqlite3.connect('levelup.db')
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
    conn = sqlite3.connect('levelup.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    if c.fetchone():
        conn.close()
        return True, "登录成功"
    else:
        conn.close()
        return False, "用户名或密码错误"