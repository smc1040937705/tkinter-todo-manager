"""
待办事项对话框组件
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from models.todo import TodoItem, Category, Priority
from views.theme import get_theme


class TodoDialog:
    """待办事项编辑对话框"""

    def __init__(self, parent, todo=None, title="添加待办"):
        self.parent = parent
        self.todo = todo
        self.title = title
        self.result = None
        self.theme = get_theme()
        self.dialog = None

    def show(self):
        """显示对话框"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(self.title)
        self.dialog.geometry("450x550")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.resizable(True, True)
        
        # 设置主题样式
        self._apply_theme()
        
        # 创建滚动区域
        self._create_scrollable_form()
        
        # 居中显示
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # 等待对话框关闭
        self.parent.wait_window(self.dialog)
        return self.result

    def _apply_theme(self):
        """应用主题样式"""
        colors = self.theme.colors
        self.dialog.configure(bg=colors["bg_primary"])

    def _create_scrollable_form(self):
        """创建可滚动的表单"""
        colors = self.theme.colors
        
        # 创建Canvas和滚动条
        canvas_frame = tk.Frame(self.dialog, bg=colors["bg_primary"])
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        canvas = tk.Canvas(canvas_frame, bg=colors["bg_primary"], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建主容器
        main_frame = tk.Frame(canvas, bg=colors["bg_primary"], padx=20, pady=20)
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor=tk.NW, width=410)
        
        # 创建表单内容
        self._create_form_content(main_frame)
        
        # 绑定滚动事件
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        main_frame.bind("<Configure>", on_frame_configure)
        
        def on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind("<Configure>", on_canvas_configure)
        
        # 鼠标滚轮绑定
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        # 保存引用以便清理
        self._canvas = canvas
        self._on_mousewheel = on_mousewheel

    def _create_form_content(self, main_frame):
        """创建表单内容"""
        colors = self.theme.colors
        
        # 标题输入
        tk.Label(main_frame, text="标题 *", font=self.theme.get_font("normal", "bold"),
                bg=colors["bg_primary"], fg=colors["fg_primary"]).pack(anchor=tk.W, pady=(0, 5))
        
        self.title_var = tk.StringVar(value=self.todo.title if self.todo else "")
        self.title_entry = tk.Entry(main_frame, textvariable=self.title_var,
                                   font=self.theme.get_font("normal"),
                                   bg=colors["bg_secondary"], fg=colors["fg_primary"],
                                   insertbackground=colors["fg_primary"],
                                   relief=tk.FLAT, highlightthickness=1,
                                   highlightbackground=colors["border"],
                                   highlightcolor=colors["border_focus"])
        self.title_entry.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # 分类选择
        tk.Label(main_frame, text="分类", font=self.theme.get_font("normal", "bold"),
                bg=colors["bg_primary"], fg=colors["fg_primary"]).pack(anchor=tk.W, pady=(0, 5))
        
        self.category_var = tk.StringVar(value=self.todo.category.value if self.todo else Category.WORK.value)
        category_frame = tk.Frame(main_frame, bg=colors["bg_primary"])
        category_frame.pack(fill=tk.X, pady=(0, 15))
        
        for cat in Category:
            rb = tk.Radiobutton(category_frame, text=cat.value, variable=self.category_var,
                              value=cat.value, font=self.theme.get_font("normal"),
                              bg=colors["bg_primary"], fg=colors["fg_primary"],
                              selectcolor=colors["bg_secondary"],
                              activebackground=colors["bg_primary"],
                              activeforeground=colors["fg_primary"])
            rb.pack(side=tk.LEFT, padx=(0, 15))
        
        # 优先级选择
        tk.Label(main_frame, text="优先级", font=self.theme.get_font("normal", "bold"),
                bg=colors["bg_primary"], fg=colors["fg_primary"]).pack(anchor=tk.W, pady=(0, 5))
        
        self.priority_var = tk.StringVar(value=self.todo.priority.value if self.todo else Priority.MEDIUM.value)
        priority_frame = tk.Frame(main_frame, bg=colors["bg_primary"])
        priority_frame.pack(fill=tk.X, pady=(0, 15))
        
        for pri in Priority:
            rb = tk.Radiobutton(priority_frame, text=pri.value, variable=self.priority_var,
                              value=pri.value, font=self.theme.get_font("normal"),
                              bg=colors["bg_primary"], fg=colors["fg_primary"],
                              selectcolor=colors["bg_secondary"],
                              activebackground=colors["bg_primary"],
                              activeforeground=colors["fg_primary"])
            rb.pack(side=tk.LEFT, padx=(0, 15))
        
        # 截止日期
        tk.Label(main_frame, text="截止日期 (YYYY-MM-DD)", font=self.theme.get_font("normal", "bold"),
                bg=colors["bg_primary"], fg=colors["fg_primary"]).pack(anchor=tk.W, pady=(0, 5))
        
        self.date_var = tk.StringVar(value=self.todo.due_date if self.todo and self.todo.due_date else "")
        self.date_entry = tk.Entry(main_frame, textvariable=self.date_var,
                                  font=self.theme.get_font("normal"),
                                  bg=colors["bg_secondary"], fg=colors["fg_primary"],
                                  insertbackground=colors["fg_primary"],
                                  relief=tk.FLAT, highlightthickness=1,
                                  highlightbackground=colors["border"],
                                  highlightcolor=colors["border_focus"])
        self.date_entry.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        # 描述
        tk.Label(main_frame, text="描述", font=self.theme.get_font("normal", "bold"),
                bg=colors["bg_primary"], fg=colors["fg_primary"]).pack(anchor=tk.W, pady=(0, 5))
        
        desc_frame = tk.Frame(main_frame, bg=colors["border"], highlightthickness=1,
                             highlightbackground=colors["border"])
        desc_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.desc_text = tk.Text(desc_frame, height=5, font=self.theme.get_font("normal"),
                                bg=colors["bg_secondary"], fg=colors["fg_primary"],
                                insertbackground=colors["fg_primary"],
                                relief=tk.FLAT, wrap=tk.WORD, padx=5, pady=5)
        self.desc_text.pack(fill=tk.X, expand=True)
        
        if self.todo and self.todo.description:
            self.desc_text.insert("1.0", self.todo.description)
        
        # 按钮区域
        btn_frame = tk.Frame(main_frame, bg=colors["bg_primary"])
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 取消按钮
        cancel_btn = tk.Button(btn_frame, text="取消", command=self._on_cancel,
                              font=self.theme.get_font("normal"),
                              bg=colors["bg_secondary"], fg=colors["fg_primary"],
                              activebackground=colors["bg_tertiary"],
                              activeforeground=colors["fg_primary"],
                              relief=tk.FLAT, cursor="hand2", padx=20, pady=5)
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 保存按钮
        save_btn = tk.Button(btn_frame, text="保存", command=self._on_save,
                            font=self.theme.get_font("normal", "bold"),
                            bg=colors["accent"], fg="white",
                            activebackground=colors["accent_hover"],
                            activeforeground="white",
                            relief=tk.FLAT, cursor="hand2", padx=20, pady=5)
        save_btn.pack(side=tk.RIGHT)
        
        # 绑定回车键
        self.dialog.bind("<Return>", lambda e: self._on_save())
        self.dialog.bind("<Escape>", lambda e: self._on_cancel())

    def _validate_date(self, date_str):
        """验证日期格式"""
        if not date_str:
            return True
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def _on_save(self):
        """保存按钮回调"""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("提示", "请输入待办标题", parent=self.dialog)
            return
        
        due_date = self.date_var.get().strip()
        if due_date and not self._validate_date(due_date):
            messagebox.showwarning("提示", "日期格式不正确，请使用 YYYY-MM-DD 格式", parent=self.dialog)
            return
        
        # 获取分类和优先级
        category_value = self.category_var.get()
        priority_value = self.priority_var.get()
        
        # 转换为枚举
        category = None
        for cat in Category:
            if cat.value == category_value:
                category = cat
                break
        
        priority = None
        for pri in Priority:
            if pri.value == priority_value:
                priority = pri
                break
        
        description = self.desc_text.get("1.0", tk.END).strip()
        
        self.result = {
            "title": title,
            "category": category,
            "priority": priority,
            "due_date": due_date if due_date else None,
            "description": description
        }
        
        self._cleanup()
        self.dialog.destroy()

    def _on_cancel(self):
        """取消按钮回调"""
        self.result = None
        self._cleanup()
        self.dialog.destroy()

    def _cleanup(self):
        """清理资源"""
        # 解绑鼠标滚轮事件
        if hasattr(self, '_canvas') and hasattr(self, '_on_mousewheel'):
            self._canvas.unbind_all("<MouseWheel>")
