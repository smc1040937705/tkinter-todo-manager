#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
待办管理器 - 基于 Python + Tkinter 的桌面待办管理应用
"""

import tkinter as tk
from views import MainWindow

def main():
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()