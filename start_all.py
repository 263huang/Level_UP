"""
文件名：start_all.py
功能：一键启动LevelUP系统的后端Flask服务和前端静态服务器，并自动打开浏览器
主要内容：
    - 启动后端服务
    - 启动前端服务
    - 自动打开前端页面
    - 支持Ctrl+C关闭所有服务
"""
import subprocess
import webbrowser
import time
import sys
import os

# 启动后端 Flask 服务
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
backend_cmd = [sys.executable, 'main_app.py']
backend_proc = subprocess.Popen(backend_cmd, cwd=backend_dir)

# 启动前端静态服务器
frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
frontend_cmd = [sys.executable, 'start_frontend_server.py']
frontend_proc = subprocess.Popen(frontend_cmd, cwd=frontend_dir)

# 等待服务器启动，确保端口已监听
time.sleep(2)

# 自动打开前端登录页面
webbrowser.open('http://localhost:8080/signin_page.html')

print("所有服务已启动，浏览器已打开。")
print("按 Ctrl+C 可关闭所有服务。")

try:
    # 等待子进程结束（一般不会自动结束）
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    print("\n正在关闭服务...")
    backend_proc.terminate()
    frontend_proc.terminate()
    print("已全部关闭。") 