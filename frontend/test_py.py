# 检查Python环境是否正常工作的简单代码

def check_python():
    print("Python 环境正常运行！")
    print(f"当前Python版本: {__import__('sys').version}")

if __name__ == "__main__":
    check_python()