"""
主窗口组件
"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta

from models.todo import TodoItem, TodoManager, Category, Priority
from models.storage import Storage
from views.theme import get_theme, toggle_theme
from views.todo_dialog import TodoDialog
from views.todo_list_item import TodoListItem


class MainWindow:
    """主窗口类"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("待办管理器")
        self.root.geometry("900x700")
        self.root.minsize(700, 500)
        
        # 窗口置顶设置
        self.topmost = False
        self.root.attributes("-topmost", self.topmost)
        
        # 主题
        self.theme = get_theme()
        
        # 数据
        self.storage = Storage()
        self.todo_manager = TodoManager()
        self.load_data()
        
        # 筛选状态
        self.current_filter = "all"  # all, work, study, life, completed, incomplete
        self.search_keyword = ""
        
        # 列表项组件缓存
        self.todo_items = {}
        
        # 创建UI
        self._create_menu()
        self._create_toolbar()
        self._create_filter_bar()
        self._create_list_area()
        self._create_status_bar()
        
        # 应用主题
        self._apply_theme()
        
        # 检查到期提醒
        self.root.after(1000, self._check_due_reminders)
        
        # 绑定窗口关闭
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 刷新列表
        self.refresh_list()

    def _create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建待办", command=self._add_todo, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="保存", command=self.save_data, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_close)
        
        # 视图菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_checkbutton(label="窗口置顶", command=self._toggle_topmost)
        view_menu.add_separator()
        view_menu.add_command(label="切换主题", command=self._toggle_theme)
        
        # 筛选菜单
        filter_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="筛选", menu=filter_menu)
        filter_menu.add_command(label="全部", command=lambda: self._set_filter("all"))
        filter_menu.add_separator()
        filter_menu.add_command(label="工作", command=lambda: self._set_filter("work"))
        filter_menu.add_command(label="学习", command=lambda: self._set_filter("study"))
        filter_menu.add_command(label="生活", command=lambda: self._set_filter("life"))
        filter_menu.add_separator()
        filter_menu.add_command(label="未完成", command=lambda: self._set_filter("incomplete"))
        filter_menu.add_command(label="已完成", command=lambda: self._set_filter("completed"))
        filter_menu.add_separator()
        filter_menu.add_command(label="已逾期", command=lambda: self._set_filter("overdue"))
        filter_menu.add_command(label="今天到期", command=lambda: self._set_filter("today"))
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)
        
        # 绑定快捷键
        self.root.bind("<Control-n>", lambda e: self._add_todo())
        self.root.bind("<Control-s>", lambda e: self.save_data())

    def _create_toolbar(self):
        """创建工具栏"""
        colors = self.theme.colors
        
        self.toolbar = tk.Frame(self.root, bg=colors["bg_secondary"], height=50)
        self.toolbar.pack(fill=tk.X)
        self.toolbar.pack_propagate(False)
        
        # 添加按钮
        add_btn = tk.Button(self.toolbar, text="+ 新建待办", command=self._add_todo,
                           font=self.theme.get_font("normal", "bold"),
                           bg=colors["accent"], fg="white",
                           activebackground=colors["accent_hover"],
                           relief=tk.FLAT, cursor="hand2", padx=15)
        add_btn.pack(side=tk.LEFT, padx=15, pady=8)
        
        # 搜索框
        search_frame = tk.Frame(self.toolbar, bg=colors["bg_secondary"])
        search_frame.pack(side=tk.RIGHT, padx=15, pady=8)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search)
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=self.theme.get_font("normal"),
                               bg=colors["bg_primary"], fg=colors["fg_primary"],
                               insertbackground=colors["fg_primary"],
                               relief=tk.FLAT, highlightthickness=1,
                               highlightbackground=colors["border"],
                               highlightcolor=colors["border_focus"],
                               width=25)
        search_entry.pack(side=tk.LEFT, ipady=4)
        
        search_label = tk.Label(search_frame, text="搜索: ",
                               font=self.theme.get_font("normal"),
                               bg=colors["bg_secondary"], fg=colors["fg_primary"])
        search_label.pack(side=tk.LEFT, padx=(0, 5))

    def _create_filter_bar(self):
        """创建筛选栏"""
        colors = self.theme.colors
        
        self.filter_bar = tk.Frame(self.root, bg=colors["bg_primary"], height=40)
        self.filter_bar.pack(fill=tk.X)
        self.filter_bar.pack_propagate(False)
        
        # 筛选按钮
        filters = [
            ("全部", "all"),
            ("工作", "work"),
            ("学习", "study"),
            ("生活", "life"),
            ("未完成", "incomplete"),
            ("已完成", "completed"),
        ]
        
        self.filter_buttons = {}
        for label, filter_key in filters:
            btn = tk.Button(self.filter_bar, text=label,
                           command=lambda k=filter_key: self._set_filter(k),
                           font=self.theme.get_font("small"),
                           bg=colors["bg_tertiary"], fg=colors["fg_primary"],
                           activebackground=colors["accent"],
                           activeforeground="white",
                           relief=tk.FLAT, cursor="hand2", padx=12, pady=2)
            btn.pack(side=tk.LEFT, padx=(15 if filter_key == "all" else 5, 0), pady=8)
            self.filter_buttons[filter_key] = btn
        
        # 主题切换按钮
        theme_btn = tk.Button(self.filter_bar, text="切换主题", command=self._toggle_theme,
                             font=self.theme.get_font("small"),
                             bg=colors["bg_tertiary"], fg=colors["fg_primary"],
                             activebackground=colors["accent"],
                             activeforeground="white",
                             relief=tk.FLAT, cursor="hand2", padx=12, pady=2)
        theme_btn.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # 置顶按钮
        self.topmost_btn = tk.Button(self.filter_bar, text="置顶", command=self._toggle_topmost,
                                    font=self.theme.get_font("small"),
                                    bg=colors["bg_tertiary"], fg=colors["fg_primary"],
                                    activebackground=colors["accent"],
                                    activeforeground="white",
                                    relief=tk.FLAT, cursor="hand2", padx=12, pady=2)
        self.topmost_btn.pack(side=tk.RIGHT, padx=5, pady=8)
        
        self._update_filter_buttons()

    def _create_list_area(self):
        """创建列表区域"""
        colors = self.theme.colors
        
        # 创建Canvas和滚动条
        self.canvas_frame = tk.Frame(self.root, bg=colors["bg_primary"])
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.canvas = tk.Canvas(self.canvas_frame, bg=colors["bg_primary"],
                               highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.canvas_frame, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.config(yscrollcommand=scrollbar.set)
        
        # 创建内容框架
        self.list_frame = tk.Frame(self.canvas, bg=colors["bg_primary"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.list_frame,
                                                      anchor=tk.NW, width=self.canvas.winfo_width())
        
        # 绑定事件
        self.list_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _create_status_bar(self):
        """创建状态栏"""
        colors = self.theme.colors
        
        self.status_bar = tk.Frame(self.root, bg=colors["bg_secondary"], height=25)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="就绪",
                                    font=self.theme.get_font("small"),
                                    bg=colors["bg_secondary"], fg=colors["fg_secondary"])
        self.status_label.pack(side=tk.LEFT, padx=15)
        
        self.count_label = tk.Label(self.status_bar, text="",
                                   font=self.theme.get_font("small"),
                                   bg=colors["bg_secondary"], fg=colors["fg_secondary"])
        self.count_label.pack(side=tk.RIGHT, padx=15)

    def _apply_theme(self):
        """应用主题到所有组件"""
        colors = self.theme.colors
        self.root.configure(bg=colors["bg_primary"])
        
        # 更新工具栏
        self.toolbar.config(bg=colors["bg_secondary"])
        for widget in self.toolbar.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.config(bg=colors["bg_secondary"])
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.config(bg=colors["bg_secondary"], fg=colors["fg_primary"])
                    elif isinstance(child, tk.Entry):
                        child.config(bg=colors["bg_primary"], fg=colors["fg_primary"],
                                    insertbackground=colors["fg_primary"],
                                    highlightbackground=colors["border"],
                                    highlightcolor=colors["border_focus"])
            elif isinstance(widget, tk.Button):
                widget.config(bg=colors["accent"], fg="white",
                             activebackground=colors["accent_hover"])
        
        # 更新筛选栏
        self.filter_bar.config(bg=colors["bg_primary"])
        for widget in self.filter_bar.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(bg=colors["bg_tertiary"], fg=colors["fg_primary"],
                             activebackground=colors["accent"], activeforeground="white")
        
        # 更新列表区域
        self.canvas_frame.config(bg=colors["bg_primary"])
        self.canvas.config(bg=colors["bg_primary"])
        self.list_frame.config(bg=colors["bg_primary"])
        
        # 更新状态栏
        self.status_bar.config(bg=colors["bg_secondary"])
        self.status_label.config(bg=colors["bg_secondary"], fg=colors["fg_secondary"])
        self.count_label.config(bg=colors["bg_secondary"], fg=colors["fg_secondary"])

    def _update_filter_buttons(self):
        """更新筛选按钮状态"""
        colors = self.theme.colors
        for key, btn in self.filter_buttons.items():
            if key == self.current_filter:
                btn.config(bg=colors["accent"], fg="white")
            else:
                btn.config(bg=colors["bg_tertiary"], fg=colors["fg_primary"])

    def _set_filter(self, filter_key):
        """设置筛选条件"""
        self.current_filter = filter_key
        self._update_filter_buttons()
        self.refresh_list()

    def _on_search(self, *args):
        """搜索回调"""
        self.search_keyword = self.search_var.get().strip()
        self.refresh_list()

    def _get_filtered_todos(self):
        """获取筛选后的待办列表"""
        todos = self.todo_manager.get_all()
        
        # 应用分类筛选
        if self.current_filter == "work":
            todos = [t for t in todos if t.category == Category.WORK]
        elif self.current_filter == "study":
            todos = [t for t in todos if t.category == Category.STUDY]
        elif self.current_filter == "life":
            todos = [t for t in todos if t.category == Category.LIFE]
        elif self.current_filter == "completed":
            todos = [t for t in todos if t.completed]
        elif self.current_filter == "incomplete":
            todos = [t for t in todos if not t.completed]
        elif self.current_filter == "overdue":
            todos = [t for t in todos if t.is_overdue()]
        elif self.current_filter == "today":
            todos = [t for t in todos if t.is_due_today()]
        
        # 应用搜索
        if self.search_keyword:
            keyword = self.search_keyword.lower()
            todos = [t for t in todos if (
                keyword in t.title.lower() or
                keyword in t.description.lower() or
                keyword in t.category.value.lower()
            )]
        
        # 按优先级和日期排序
        todos.sort(key=lambda t: (
            t.completed,  # 未完成的在前
            -({Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}.get(t.priority, 0)),  # 高优先级在前
            t.due_date or "9999-99-99"  # 有日期的在前
        ))
        
        return todos

    def refresh_list(self):
        """刷新待办列表"""
        # 清除现有组件
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        self.todo_items.clear()
        
        # 获取筛选后的待办
        todos = self._get_filtered_todos()
        
        if not todos:
            # 显示空状态
            empty_label = tk.Label(self.list_frame, text="暂无待办事项",
                                  font=self.theme.get_font("large"),
                                  bg=self.theme.colors["bg_primary"],
                                  fg=self.theme.colors["fg_secondary"])
            empty_label.pack(pady=50)
            
            if self.search_keyword:
                empty_label.config(text=f"未找到包含 \"{self.search_keyword}\" 的待办")
            elif self.current_filter != "all":
                filter_names = {
                    "work": "工作", "study": "学习", "life": "生活",
                    "completed": "已完成", "incomplete": "未完成",
                    "overdue": "已逾期", "today": "今天到期"
                }
                empty_label.config(text=f"暂无 {filter_names.get(self.current_filter, '')} 待办")
        else:
            # 创建列表项
            for todo in todos:
                item = TodoListItem(self.list_frame, todo,
                                   on_toggle=self._toggle_todo,
                                   on_edit=self._edit_todo,
                                   on_delete=self._delete_todo)
                item.pack(fill=tk.X, pady=(0, 8))
                self.todo_items[todo.id] = item
        
        # 更新状态栏
        total = len(self.todo_manager.get_all())
        completed = len(self.todo_manager.get_completed())
        incomplete = total - completed
        self.count_label.config(text=f"总计: {total} | 未完成: {incomplete} | 已完成: {completed}")
        
        # 更新Canvas滚动区域
        self.list_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _add_todo(self):
        """添加待办"""
        dialog = TodoDialog(self.root, title="添加待办")
        result = dialog.show()
        
        if result:
            todo = TodoItem(
                title=result["title"],
                category=result["category"],
                priority=result["priority"],
                due_date=result["due_date"],
                description=result["description"]
            )
            self.todo_manager.add(todo)
            self.save_data()
            self.refresh_list()
            self.status_label.config(text=f"已添加: {todo.title}")

    def _edit_todo(self, todo_id):
        """编辑待办"""
        todo = self.todo_manager.get(todo_id)
        if not todo:
            return
        
        dialog = TodoDialog(self.root, todo=todo, title="编辑待办")
        result = dialog.show()
        
        if result:
            self.todo_manager.update(todo_id, **result)
            self.save_data()
            self.refresh_list()
            self.status_label.config(text=f"已更新: {result['title']}")

    def _delete_todo(self, todo_id):
        """删除待办"""
        todo = self.todo_manager.get(todo_id)
        if not todo:
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除待办 \"{todo.title}\" 吗？"):
            self.todo_manager.delete(todo_id)
            self.save_data()
            self.refresh_list()
            self.status_label.config(text=f"已删除: {todo.title}")

    def _toggle_todo(self, todo_id):
        """切换完成状态"""
        todo = self.todo_manager.get(todo_id)
        if todo:
            if todo.completed:
                todo.mark_incomplete()
                self.status_label.config(text=f"标记为未完成: {todo.title}")
            else:
                todo.mark_complete()
                self.status_label.config(text=f"标记为完成: {todo.title}")
            self.save_data()
            self.refresh_list()

    def _toggle_topmost(self):
        """切换窗口置顶"""
        self.topmost = not self.topmost
        self.root.attributes("-topmost", self.topmost)
        self.topmost_btn.config(text="取消置顶" if self.topmost else "置顶")

    def _toggle_theme(self):
        """切换主题"""
        toggle_theme()
        self.theme = get_theme()
        self._apply_theme()
        self._update_filter_buttons()
        self.refresh_list()
        self.status_label.config(text=f"已切换到{'深色' if self.theme.is_dark() else '浅色'}主题")

    def _check_due_reminders(self):
        """检查到期提醒"""
        try:
            overdue = self.todo_manager.get_overdue()
            due_today = self.todo_manager.get_due_today()
            
            # 只提醒未完成的
            overdue_incomplete = [t for t in overdue if not t.completed]
            due_today_incomplete = [t for t in due_today if not t.completed]
            
            if overdue_incomplete:
                titles = ", ".join([t.title for t in overdue_incomplete[:3]])
                if len(overdue_incomplete) > 3:
                    titles += f" 等 {len(overdue_incomplete)} 项"
                messagebox.showwarning("逾期提醒", f"以下待办已逾期:\n{titles}", parent=self.root)
            
            if due_today_incomplete:
                titles = ", ".join([t.title for t in due_today_incomplete[:3]])
                if len(due_today_incomplete) > 3:
                    titles += f" 等 {len(due_today_incomplete)} 项"
                messagebox.showinfo("到期提醒", f"以下待办今天到期:\n{titles}", parent=self.root)
        except Exception as e:
            print(f"提醒检查出错: {e}")
        
        # 每小时检查一次
        self.root.after(3600000, self._check_due_reminders)

    def _on_frame_configure(self, event=None):
        """框架配置改变"""
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Canvas配置改变"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """鼠标滚轮滚动"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _show_about(self):
        """显示关于对话框"""
        messagebox.showinfo("关于", "待办管理器 v1.0\n\n基于 Python + Tkinter 开发")

    def load_data(self):
        """加载数据"""
        data = self.storage.load()
        self.todo_manager = TodoManager.from_list(data)

    def save_data(self):
        """保存数据"""
        data = self.todo_manager.to_list()
        self.storage.save(data)

    def _on_close(self):
        """关闭窗口"""
        self.save_data()
        self.root.destroy()

    def run(self):
        """运行应用"""
        self.root.mainloop()
