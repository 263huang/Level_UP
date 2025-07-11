"""
文件名：app.py
功能：Flask应用入口示例，提供根路由测试
主要内容：
    - Flask应用初始化
    - 根路由/hello world测试
"""
from flask import Flask
from dotenv import load_dotenv
import os

app = Flask(__name__)

load_dotenv()
debug_mode = os.getenv("FLASK_DEBUG", "False") == "True"

@app.route('/')
def hello():
    """
    根路由，返回Hello, Flask!字符串
    返回：字符串
    """
    return 'Hello, Flask!'

if __name__ == '__main__':
    # 启动Flask开发服务器
    app.run(debug=debug_mode)