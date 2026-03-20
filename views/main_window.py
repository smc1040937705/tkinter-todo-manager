import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional, Callable, List

from .theme import Theme
from .todo_list import TodoListView
from .dialogs import AddEditDialog
from models.todo import Todo
from models.data_manager import DataManager


class MainWindow:
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.theme = Theme(Theme.LIGHT)
        
        self.root = tk.Tk()
        self.root.title("待办管理器")
        self.root.geometry("900x650")
        self.root.minsize(700, 500)
        self.root.resizable(True, True)
        self.root.topmost = False
        
        self._current_filter = {
            "category": None,
            "priority": None,
            "completed": None,
            "overdue_only": False
        }
        self._sort_by = "due_date"
        self._sort_reverse = False
        
        self._setup_ui()
        self._apply_theme()
        self._bind_events()
        self._start_reminder_check()
        self.refresh_list()
    
    def _setup_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self._setup_toolbar()
        self._setup_filter_bar()
        self._setup_content_area()
        self._setup_status_bar()
    
    def _setup_toolbar(self):
        self.toolbar = tk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, pady=(0, 10))
        
        self.btn_add = tk.Button(
            self.toolbar,
            text="➕ 添加待办",
            command=self._on_add_click,
            width=12
        )
        self.btn_add.pack(side=tk.LEFT, padx=5)
        
        self.btn_edit = tk.Button(
            self.toolbar,
            text="✏️ 编辑",
            command=self._on_edit_click,
            width=10
        )
        self.btn_edit.pack(side=tk.LEFT, padx=5)
        
        self.btn_delete = tk.Button(
            self.toolbar,
            text="🗑️ 删除",
            command=self._on_delete_click,
            width=10
        )
        self.btn_delete.pack(side=tk.LEFT, padx=5)
        
        self.btn_toggle = tk.Button(
            self.toolbar,
            text="✓ 标记完成",
            command=self._on_toggle_complete,
            width=12
        )
        self.btn_toggle.pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self._on_search_change)
        self.search_entry = tk.Entry(
            self.toolbar,
            textvariable=self.search_var,
            width=25
        )
        self.search_entry.pack(side=tk.RIGHT, padx=5)
        
        tk.Label(self.toolbar, text="🔍 搜索:").pack(side=tk.RIGHT, padx=5)
        
        self.btn_theme = tk.Button(
            self.toolbar,
            text="🌙 深色",
            command=self._toggle_theme,
            width=10
        )
        self.btn_theme.pack(side=tk.RIGHT, padx=5)
        
        self.btn_topmost = tk.Button(
            self.toolbar,
            text="📌 置顶",
            command=self._toggle_topmost,
            width=10
        )
        self.btn_topmost.pack(side=tk.RIGHT, padx=5)
    
    def _setup_filter_bar(self):
        self.filter_frame = tk.Frame(self.main_frame)
        self.filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(self.filter_frame, text="分类:").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar(value="全部")
        self.category_combo = ttk.Combobox(
            self.filter_frame,
            textvariable=self.category_var,
            values=["全部"] + Todo.CATEGORIES,
            state="readonly",
            width=10
        )
        self.category_combo.pack(side=tk.LEFT, padx=5)
        self.category_combo.bind("<<ComboboxSelected>>", self._on_filter_change)
        
        tk.Label(self.filter_frame, text="优先级:").pack(side=tk.LEFT, padx=(20, 5))
        self.priority_var = tk.StringVar(value="全部")
        self.priority_combo = ttk.Combobox(
            self.filter_frame,
            textvariable=self.priority_var,
            values=["全部", "高", "中", "低"],
            state="readonly",
            width=8
        )
        self.priority_combo.pack(side=tk.LEFT, padx=5)
        self.priority_combo.bind("<<ComboboxSelected>>", self._on_filter_change)
        
        tk.Label(self.filter_frame, text="状态:").pack(side=tk.LEFT, padx=(20, 5))
        self.status_var = tk.StringVar(value="全部")
        self.status_combo = ttk.Combobox(
            self.filter_frame,
            textvariable=self.status_var,
            values=["全部", "未完成", "已完成", "已过期"],
            state="readonly",
            width=10
        )
        self.status_combo.pack(side=tk.LEFT, padx=5)
        self.status_combo.bind("<<ComboboxSelected>>", self._on_filter_change)
        
        tk.Label(self.filter_frame, text="排序:").pack(side=tk.LEFT, padx=(20, 5))
        self.sort_var = tk.StringVar(value="截止日期")
        self.sort_combo = ttk.Combobox(
            self.filter_frame,
            textvariable=self.sort_var,
            values=["截止日期", "优先级", "创建时间", "标题"],
            state="readonly",
            width=10
        )
        self.sort_combo.pack(side=tk.LEFT, padx=5)
        self.sort_combo.bind("<<ComboboxSelected>>", self._on_sort_change)
    
    def _setup_content_area(self):
        self.content_frame = tk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.todo_list = TodoListView(
            self.content_frame,
            self.theme,
            on_select=self._on_todo_select,
            on_double_click=self._on_todo_double_click
        )
        self.todo_list.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.content_frame, command=self.todo_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.todo_list.config(yscrollcommand=scrollbar.set)
    
    def _setup_status_bar(self):
        self.status_bar = tk.Frame(self.main_frame)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = tk.Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT)
        
        self.stats_label = tk.Label(self.status_bar, text="")
        self.stats_label.pack(side=tk.RIGHT)
    
    def _apply_theme(self):
        colors = self.theme.get_all_colors()
        fonts = self.theme.FONTS
        
        self.root.configure(bg=colors["bg"])
        self.main_frame.configure(bg=colors["bg"])
        self.toolbar.configure(bg=colors["bg"])
        self.filter_frame.configure(bg=colors["bg"])
        self.content_frame.configure(bg=colors["bg"])
        self.status_bar.configure(bg=colors["bg"])
        
        btn_style = {
            "bg": colors["accent"],
            "fg": "white",
            "font": fonts["button"],
            "relief": "flat",
            "cursor": "hand2",
            "activebackground": colors["accent_hover"],
            "activeforeground": "white"
        }
        
        for btn in [self.btn_add, self.btn_edit, self.btn_delete, 
                    self.btn_toggle, self.btn_theme, self.btn_topmost]:
            btn.configure(**btn_style)
        
        label_style = {
            "bg": colors["bg"],
            "fg": colors["fg"],
            "font": fonts["normal"]
        }
        
        for widget in self.toolbar.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(**label_style)
        
        for widget in self.filter_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(**label_style)
        
        entry_style = {
            "bg": colors["input_bg"],
            "fg": colors["fg"],
            "font": fonts["normal"],
            "relief": "solid",
            "bd": 1,
            "insertbackground": colors["fg"]
        }
        self.search_entry.configure(**entry_style)
        
        self.status_label.configure(**label_style)
        self.stats_label.configure(**label_style)
        
        self.todo_list.apply_theme()
        
        theme_text = "☀️ 浅色" if self.theme.mode == Theme.DARK else "🌙 深色"
        self.btn_theme.configure(text=theme_text)
    
    def _bind_events(self):
        self.root.bind("<Delete>", lambda e: self._on_delete_click())
        self.root.bind("<Control-n>", lambda e: self._on_add_click())
        self.root.bind("<Control-e>", lambda e: self._on_edit_click())
        self.root.bind("<Control-f>", lambda e: self.search_entry.focus())
        self.root.bind("<Escape>", lambda e: self._clear_search())
    
    def _start_reminder_check(self):
        self._check_reminders()
        self.root.after(60000, self._start_reminder_check)
    
    def _check_reminders(self):
        overdue_todos = self.data_manager.get_overdue()
        due_today = self.data_manager.get_due_today()
        
        pending_due_today = [t for t in due_today if not t.completed]
        
        if overdue_todos:
            titles = "\n".join([f"• {t.title}" for t in overdue_todos[:5]])
            if len(overdue_todos) > 5:
                titles += f"\n... 还有 {len(overdue_todos) - 5} 项"
            messagebox.showwarning(
                "过期提醒",
                f"以下待办已过期:\n{titles}"
            )
        
        if pending_due_today:
            titles = "\n".join([f"• {t.title}" for t in pending_due_today[:5]])
            if len(pending_due_today) > 5:
                titles += f"\n... 还有 {len(pending_due_today) - 5} 项"
            messagebox.showinfo(
                "今日待办",
                f"今天有以下待办:\n{titles}"
            )
    
    def refresh_list(self):
        self._apply_filters()
        self._update_stats()
    
    def _apply_filters(self):
        category = self.category_var.get()
        priority = self.priority_var.get()
        status = self.status_var.get()
        
        filter_category = None if category == "全部" else category
        
        filter_priority = None
        if priority == "高":
            filter_priority = Todo.PRIORITY_HIGH
        elif priority == "中":
            filter_priority = Todo.PRIORITY_MEDIUM
        elif priority == "低":
            filter_priority = Todo.PRIORITY_LOW
        
        filter_completed = None
        overdue_only = False
        if status == "已完成":
            filter_completed = True
        elif status == "未完成":
            filter_completed = False
        elif status == "已过期":
            overdue_only = True
        
        todos = self.data_manager.filter_todos(
            category=filter_category,
            priority=filter_priority,
            completed=filter_completed,
            overdue_only=overdue_only
        )
        
        sort_map = {
            "截止日期": "due_date",
            "优先级": "priority",
            "创建时间": "created_at",
            "标题": "title"
        }
        sort_by = sort_map.get(self.sort_var.get(), "due_date")
        
        todos = self.data_manager.sort_todos(todos, by=sort_by)
        
        self.todo_list.update_todos(todos)
    
    def _update_stats(self):
        stats = self.data_manager.get_statistics()
        self.stats_label.configure(
            text=f"总计: {stats['total']} | 已完成: {stats['completed']} | "
                 f"待办: {stats['pending']} | 过期: {stats['overdue']}"
        )
    
    def _on_add_click(self):
        dialog = AddEditDialog(self.root, self.theme, self.data_manager)
        if dialog.result:
            self.refresh_list()
            self.status_label.configure(text=f"已添加: {dialog.result.title}")
    
    def _on_edit_click(self):
        selected = self.todo_list.get_selected()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个待办事项")
            return
        
        dialog = AddEditDialog(
            self.root, self.theme, self.data_manager, todo=selected
        )
        if dialog.result:
            self.refresh_list()
            self.status_label.configure(text=f"已更新: {dialog.result.title}")
    
    def _on_delete_click(self):
        selected = self.todo_list.get_selected()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个待办事项")
            return
        
        if messagebox.askyesno("确认删除", f"确定要删除 '{selected.title}' 吗?"):
            self.data_manager.delete(selected.id)
            self.refresh_list()
            self.status_label.configure(text=f"已删除: {selected.title}")
    
    def _on_toggle_complete(self):
        selected = self.todo_list.get_selected()
        if not selected:
            messagebox.showinfo("提示", "请先选择一个待办事项")
            return
        
        self.data_manager.toggle_complete(selected.id)
        self.refresh_list()
        status = "已完成" if not selected.completed else "未完成"
        self.status_label.configure(text=f"'{selected.title}' 已标记为{status}")
    
    def _on_search_change(self, *args):
        keyword = self.search_var.get().strip()
        if keyword:
            todos = self.data_manager.search(keyword)
            self.todo_list.update_todos(todos)
            self.status_label.configure(text=f"搜索结果: {len(todos)} 项")
        else:
            self.refresh_list()
    
    def _on_filter_change(self, event=None):
        self.refresh_list()
    
    def _on_sort_change(self, event=None):
        self.refresh_list()
    
    def _on_todo_select(self, todo: Optional[Todo]):
        if todo:
            self.status_label.configure(
                text=f"选中: {todo.title} | 分类: {todo.category} | "
                     f"优先级: {Todo.PRIORITIES.get(todo.priority, '中')}"
            )
    
    def _on_todo_double_click(self, todo: Todo):
        self._on_edit_click()
    
    def _toggle_theme(self):
        self.theme.toggle()
        self._apply_theme()
        self.status_label.configure(text=f"已切换到{'深色' if self.theme.mode == Theme.DARK else '浅色'}主题")
    
    def _toggle_topmost(self):
        current_topmost = self.root.attributes('-topmost')
        self.root.attributes('-topmost', not current_topmost)
        new_topmost = self.root.attributes('-topmost')
        text = "取消置顶" if new_topmost else "📌 置顶"
        self.btn_topmost.configure(text=text)
        self.status_label.configure(text=f"窗口{'已置顶' if new_topmost else '取消置顶'}")
    
    def _clear_search(self):
        self.search_var.set("")
        self.refresh_list()
    
    def run(self):
        self.root.mainloop()
