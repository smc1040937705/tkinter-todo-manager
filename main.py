"""
待办管理器 - 主程序入口
"""
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from views.main_window import MainWindow


def main():
    """主函数"""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
