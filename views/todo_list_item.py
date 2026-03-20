"""
待办事项列表项组件
"""
import tkinter as tk
from views.theme import get_theme
from models.todo import Priority, Category


class TodoListItem(tk.Frame):
    """待办事项列表项"""

    def __init__(self, parent, todo, on_toggle=None, on_edit=None, on_delete=None, **kwargs):
        self.todo = todo
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.theme = get_theme()
        
        colors = self.theme.colors
        super().__init__(parent, bg=colors["bg_secondary"], padx=10, pady=8, **kwargs)
        
        self._create_widgets()
        self._update_appearance()

    def _create_widgets(self):
        """创建子组件"""
        colors = self.theme.colors
        
        # 左侧：完成复选框
        self.complete_var = tk.BooleanVar(value=self.todo.completed)
        self.checkbox = tk.Checkbutton(self, variable=self.complete_var,
                                      command=self._on_toggle,
                                      bg=colors["bg_secondary"],
                                      activebackground=colors["bg_secondary"],
                                      selectcolor=colors["bg_primary"],
                                      cursor="hand2")
        self.checkbox.pack(side=tk.LEFT, padx=(0, 10))
        
        # 中间：内容区域
        content_frame = tk.Frame(self, bg=colors["bg_secondary"])
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 标题行
        title_frame = tk.Frame(content_frame, bg=colors["bg_secondary"])
        title_frame.pack(fill=tk.X)
        
        # 标题
        self.title_label = tk.Label(title_frame, text=self.todo.title,
                                   font=self.theme.get_font("medium", "bold" if not self.todo.completed else "normal"),
                                   bg=colors["bg_secondary"],
                                   fg=colors["fg_disabled"] if self.todo.completed else colors["fg_primary"])
        self.title_label.pack(side=tk.LEFT)
        
        # 优先级标签
        priority_color = self._get_priority_color()
        self.priority_label = tk.Label(title_frame, text=self.todo.priority.value,
                                      font=self.theme.get_font("small"),
                                      bg=priority_color, fg="white",
                                      padx=6, pady=1)
        self.priority_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 分类标签
        category_color = self._get_category_color()
        self.category_label = tk.Label(title_frame, text=self.todo.category.value,
                                      font=self.theme.get_font("small"),
                                      bg=category_color, fg="white",
                                      padx=6, pady=1)
        self.category_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 逾期标签
        if self.todo.is_overdue():
            self.overdue_label = tk.Label(title_frame, text="已逾期",
                                         font=self.theme.get_font("small"),
                                         bg=colors["error"], fg="white",
                                         padx=6, pady=1)
            self.overdue_label.pack(side=tk.LEFT, padx=(5, 0))
        elif self.todo.is_due_today():
            self.today_label = tk.Label(title_frame, text="今天",
                                       font=self.theme.get_font("small"),
                                       bg=colors["warning"], fg="white",
                                       padx=6, pady=1)
            self.today_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # 描述（如果有）
        if self.todo.description:
            self.desc_label = tk.Label(content_frame, text=self.todo.description,
                                      font=self.theme.get_font("small"),
                                      bg=colors["bg_secondary"],
                                      fg=colors["fg_secondary"],
                                      wraplength=400, justify=tk.LEFT)
            self.desc_label.pack(fill=tk.X, pady=(5, 0), anchor=tk.W)
        
        # 日期
        if self.todo.due_date:
            date_text = f"截止: {self.todo.due_date}"
            date_color = colors["error"] if self.todo.is_overdue() else colors["fg_secondary"]
            self.date_label = tk.Label(content_frame, text=date_text,
                                      font=self.theme.get_font("small"),
                                      bg=colors["bg_secondary"],
                                      fg=date_color)
            self.date_label.pack(fill=tk.X, pady=(3, 0), anchor=tk.W)
        
        # 右侧：操作按钮
        btn_frame = tk.Frame(self, bg=colors["bg_secondary"])
        btn_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 编辑按钮
        self.edit_btn = tk.Button(btn_frame, text="编辑", command=self._on_edit,
                                 font=self.theme.get_font("small"),
                                 bg=colors["bg_tertiary"], fg=colors["fg_primary"],
                                 activebackground=colors["accent"],
                                 activeforeground="white",
                                 relief=tk.FLAT, cursor="hand2", padx=10)
        self.edit_btn.pack(side=tk.TOP, pady=(0, 5))
        
        # 删除按钮
        self.delete_btn = tk.Button(btn_frame, text="删除", command=self._on_delete,
                                   font=self.theme.get_font("small"),
                                   bg=colors["error"], fg="white",
                                   activebackground="#d32f2f",
                                   activeforeground="white",
                                   relief=tk.FLAT, cursor="hand2", padx=10)
        self.delete_btn.pack(side=tk.TOP)

    def _update_appearance(self):
        """更新外观（完成状态）"""
        if self.todo.completed:
            self.title_label.config(fg=self.theme.colors["fg_disabled"])

    def _get_priority_color(self):
        """获取优先级对应的颜色"""
        colors = self.theme.colors
        if self.todo.priority == Priority.HIGH:
            return colors["priority_high"]
        elif self.todo.priority == Priority.MEDIUM:
            return colors["priority_medium"]
        else:
            return colors["priority_low"]

    def _get_category_color(self):
        """获取分类对应的颜色"""
        colors = self.theme.colors
        if self.todo.category == Category.WORK:
            return colors["category_work"]
        elif self.todo.category == Category.STUDY:
            return colors["category_study"]
        else:
            return colors["category_life"]

    def _on_toggle(self):
        """切换完成状态"""
        if self.on_toggle:
            self.on_toggle(self.todo.id)

    def _on_edit(self):
        """编辑回调"""
        if self.on_edit:
            self.on_edit(self.todo.id)

    def _on_delete(self):
        """删除回调"""
        if self.on_delete:
            self.on_delete(self.todo.id)

    def update_todo(self, todo):
        """更新待办数据"""
        self.todo = todo
        self.complete_var.set(todo.completed)
        self._update_appearance()
