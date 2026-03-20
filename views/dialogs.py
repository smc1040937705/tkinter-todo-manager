import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
from typing import Optional

from .theme import Theme
from models.todo import Todo
from models.data_manager import DataManager


class AddEditDialog:
    def __init__(
        self,
        parent: tk.Tk,
        theme: Theme,
        data_manager: DataManager,
        todo: Optional[Todo] = None
    ):
        self.theme = theme
        self.data_manager = data_manager
        self.todo = todo
        self.result: Optional[Todo] = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("编辑待办" if todo else "添加待办")
        self.dialog.geometry("450x480")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._center_dialog(parent)
        self._setup_ui()
        self._apply_theme()
        
        if todo:
            self._populate_fields()
        
        self.dialog.wait_window()
    
    def _center_dialog(self, parent: tk.Tk):
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 450) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 480) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def _setup_ui(self):
        self.main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self.main_frame, text="标题 *").grid(
            row=0, column=0, sticky="w", pady=(0, 5)
        )
        self.title_var = tk.StringVar()
        self.title_entry = tk.Entry(
            self.main_frame,
            textvariable=self.title_var,
            width=40
        )
        self.title_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        tk.Label(self.main_frame, text="分类").grid(
            row=2, column=0, sticky="w", pady=(0, 5)
        )
        self.category_var = tk.StringVar(value=Todo.CATEGORY_WORK)
        self.category_combo = ttk.Combobox(
            self.main_frame,
            textvariable=self.category_var,
            values=Todo.CATEGORIES,
            state="readonly",
            width=37
        )
        self.category_combo.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        tk.Label(self.main_frame, text="优先级").grid(
            row=4, column=0, sticky="w", pady=(0, 5)
        )
        self.priority_var = tk.StringVar(value="中")
        self.priority_combo = ttk.Combobox(
            self.main_frame,
            textvariable=self.priority_var,
            values=["高", "中", "低"],
            state="readonly",
            width=37
        )
        self.priority_combo.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        tk.Label(self.main_frame, text="截止日期").grid(
            row=6, column=0, sticky="w", pady=(0, 5)
        )
        
        date_frame = tk.Frame(self.main_frame)
        date_frame.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(0, 15))
        
        self.date_var = tk.StringVar()
        self.date_entry = tk.Entry(date_frame, textvariable=self.date_var, width=12)
        self.date_entry.pack(side=tk.LEFT)
        
        tk.Label(date_frame, text=" 时间: ").pack(side=tk.LEFT)
        
        self.time_var = tk.StringVar()
        self.time_entry = tk.Entry(date_frame, textvariable=self.time_var, width=8)
        self.time_entry.pack(side=tk.LEFT)
        
        tk.Label(date_frame, text=" (格式: YYYY-MM-DD HH:MM)").pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Label(self.main_frame, text="描述").grid(
            row=8, column=0, sticky="w", pady=(0, 5)
        )
        
        desc_frame = tk.Frame(self.main_frame)
        desc_frame.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        
        self.description_text = tk.Text(
            desc_frame,
            width=40,
            height=4,
            wrap=tk.WORD
        )
        self.description_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        desc_scrollbar = tk.Scrollbar(desc_frame, command=self.description_text.yview)
        desc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.description_text.config(yscrollcommand=desc_scrollbar.set)
        
        button_frame = tk.Frame(self.main_frame)
        button_frame.grid(row=10, column=0, columnspan=2, sticky="ew")
        
        self.btn_cancel = tk.Button(
            button_frame,
            text="取消",
            command=self._on_cancel,
            width=12
        )
        self.btn_cancel.pack(side=tk.RIGHT, padx=(10, 0))
        
        self.btn_save = tk.Button(
            button_frame,
            text="保存",
            command=self._on_save,
            width=12
        )
        self.btn_save.pack(side=tk.RIGHT)
        
        self.main_frame.columnconfigure(0, weight=1)
    
    def _apply_theme(self):
        colors = self.theme.get_all_colors()
        fonts = self.theme.FONTS
        
        self.dialog.configure(bg=colors["bg"])
        self.main_frame.configure(bg=colors["bg"])
        
        label_style = {
            "bg": colors["bg"],
            "fg": colors["fg"],
            "font": fonts["normal"]
        }
        
        for widget in self.main_frame.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(**label_style)
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=colors["bg"])
        
        entry_style = {
            "bg": colors["input_bg"],
            "fg": colors["fg"],
            "font": fonts["normal"],
            "relief": "solid",
            "bd": 1,
            "insertbackground": colors["fg"]
        }
        
        self.title_entry.configure(**entry_style)
        self.date_entry.configure(**entry_style)
        self.time_entry.configure(**entry_style)
        
        text_style = {
            "bg": colors["input_bg"],
            "fg": colors["fg"],
            "font": fonts["normal"],
            "relief": "solid",
            "bd": 1,
            "insertbackground": colors["fg"]
        }
        self.description_text.configure(**text_style)
        
        btn_style = {
            "bg": colors["accent"],
            "fg": "white",
            "font": fonts["button"],
            "relief": "flat",
            "cursor": "hand2",
            "activebackground": colors["accent_hover"],
            "activeforeground": "white"
        }
        
        self.btn_save.configure(**btn_style)
        
        cancel_style = btn_style.copy()
        cancel_style["bg"] = colors["disabled"]
        self.btn_cancel.configure(**cancel_style)
    
    def _populate_fields(self):
        if not self.todo:
            return
        
        self.title_var.set(self.todo.title)
        self.category_var.set(self.todo.category)
        
        priority_map = {
            Todo.PRIORITY_HIGH: "高",
            Todo.PRIORITY_MEDIUM: "中",
            Todo.PRIORITY_LOW: "低"
        }
        self.priority_var.set(priority_map.get(self.todo.priority, "中"))
        
        if self.todo.due_date:
            self.date_var.set(self.todo.due_date.strftime("%Y-%m-%d"))
            self.time_var.set(self.todo.due_date.strftime("%H:%M"))
        
        self.description_text.insert("1.0", self.todo.description)
    
    def _on_save(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("验证错误", "请输入标题")
            return
        
        priority_map = {
            "高": Todo.PRIORITY_HIGH,
            "中": Todo.PRIORITY_MEDIUM,
            "低": Todo.PRIORITY_LOW
        }
        
        due_date = None
        date_str = self.date_var.get().strip()
        time_str = self.time_var.get().strip()
        
        if date_str:
            try:
                if time_str:
                    due_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                else:
                    due_date = datetime.strptime(date_str, "%Y-%m-%d")
                    due_date = due_date.replace(hour=23, minute=59)
            except ValueError:
                messagebox.showwarning("验证错误", "日期格式不正确，请使用 YYYY-MM-DD HH:MM 格式")
                return
        
        description = self.description_text.get("1.0", tk.END).strip()
        
        if self.todo:
            self.todo.title = title
            self.todo.category = self.category_var.get()
            self.todo.priority = priority_map.get(self.priority_var.get(), Todo.PRIORITY_MEDIUM)
            self.todo.due_date = due_date
            self.todo.description = description
            self.data_manager.update(self.todo)
            self.result = self.todo
        else:
            new_todo = Todo(
                title=title,
                category=self.category_var.get(),
                priority=priority_map.get(self.priority_var.get(), Todo.PRIORITY_MEDIUM),
                due_date=due_date,
                description=description
            )
            self.result = self.data_manager.add(new_todo)
        
        self.dialog.destroy()
    
    def _on_cancel(self):
        self.result = None
        self.dialog.destroy()
