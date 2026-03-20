import tkinter as tk
from tkinter import ttk, messagebox
import datetime
from typing import Optional, Dict, Any
from .theme import Theme
from .widgets import StyledButton, StyledEntry, StyledCombobox, StyledText
from models.todo import Todo, CATEGORIES, PRIORITIES

class TodoDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, theme_name: str, todo: Optional[Todo] = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.theme_name = theme_name
        self.colors = Theme.get_colors(theme_name)
        self.todo = todo
        self.result: Optional[Dict[str, Any]] = None

        self.title('编辑待办' if todo else '添加待办')
        self.geometry('500x480')
        self.resizable(True, True)
        self.minsize(500, 480)
        self.configure(bg=self.colors['bg'])

        self.transient(parent)
        self.grab_set()

        self._setup_ui()

        if todo:
            self._load_todo_data()

        self.center_window()

    def center_window(self) -> None:
        self.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - self.winfo_width()) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f'+{x}+{y}')

    def _setup_ui(self) -> None:
        padding = {'padx': 20, 'pady': 10}

        main_frame = tk.Frame(self, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, **padding)

        tk.Label(
            main_frame,
            text='标题 *',
            font=Theme.get_font('normal', bold=True),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        ).grid(row=0, column=0, sticky='w', pady=(0, 5))

        self.title_entry = StyledEntry(main_frame, self.colors, width=40)
        self.title_entry.grid(row=1, column=0, sticky='ew', pady=(0, 15))

        tk.Label(
            main_frame,
            text='描述',
            font=Theme.get_font('normal', bold=True),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        ).grid(row=2, column=0, sticky='w', pady=(0, 5))

        self.desc_text = StyledText(main_frame, self.colors, width=40, height=5)
        self.desc_text.grid(row=3, column=0, sticky='ew', pady=(0, 15))

        row_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        row_frame.grid(row=4, column=0, sticky='ew', pady=(0, 15))

        tk.Label(
            row_frame,
            text='分类',
            font=Theme.get_font('normal', bold=True),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        ).grid(row=0, column=0, sticky='w', padx=(0, 10))

        self.category_var = tk.StringVar(value=CATEGORIES[2])
        self.category_combo = StyledCombobox(
            row_frame,
            self.colors,
            textvariable=self.category_var,
            values=CATEGORIES,
            width=10
        )
        self.category_combo.grid(row=1, column=0, padx=(0, 20))

        tk.Label(
            row_frame,
            text='优先级',
            font=Theme.get_font('normal', bold=True),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        ).grid(row=0, column=1, sticky='w', padx=(0, 10))

        self.priority_var = tk.StringVar(value=PRIORITIES[1])
        self.priority_combo = StyledCombobox(
            row_frame,
            self.colors,
            textvariable=self.priority_var,
            values=PRIORITIES,
            width=10
        )
        self.priority_combo.grid(row=1, column=1)

        tk.Label(
            main_frame,
            text='截止日期 (YYYY-MM-DD)',
            font=Theme.get_font('normal', bold=True),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        ).grid(row=5, column=0, sticky='w', pady=(0, 5))

        date_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        date_frame.grid(row=6, column=0, sticky='ew', pady=(0, 20))

        self.date_entry = StyledEntry(date_frame, self.colors, width=15)
        self.date_entry.grid(row=0, column=0, padx=(0, 10))

        StyledButton(
            date_frame,
            '今天',
            self.colors,
            style='default',
            command=self._set_today,
            padx=10
        ).grid(row=0, column=1, padx=2)

        StyledButton(
            date_frame,
            '明天',
            self.colors,
            style='default',
            command=self._set_tomorrow,
            padx=10
        ).grid(row=0, column=2, padx=2)

        StyledButton(
            date_frame,
            '清空',
            self.colors,
            style='default',
            command=self._clear_date,
            padx=10
        ).grid(row=0, column=3, padx=2)

        btn_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        btn_frame.grid(row=7, column=0, sticky='e')

        StyledButton(
            btn_frame,
            '取消',
            self.colors,
            style='default',
            command=self.destroy
        ).grid(row=0, column=0, padx=(0, 10))

        StyledButton(
            btn_frame,
            '保存',
            self.colors,
            style='primary',
            command=self._on_save
        ).grid(row=0, column=1)

        main_frame.grid_columnconfigure(0, weight=1)

    def _load_todo_data(self) -> None:
        if not self.todo:
            return

        self.title_entry.insert(0, self.todo.title)

        if self.todo.description:
            self.desc_text.insert('1.0', self.todo.description)

        self.category_var.set(self.todo.category)
        self.priority_var.set(self.todo.priority)

        if self.todo.due_date:
            self.date_entry.insert(0, Todo.format_date(self.todo.due_date))

    def _set_today(self) -> None:
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, today)

    def _set_tomorrow(self) -> None:
        tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, tomorrow)

    def _clear_date(self) -> None:
        self.date_entry.delete(0, tk.END)

    def _on_save(self) -> None:
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror('错误', '请输入待办标题！', parent=self)
            self.title_entry.focus_set()
            return

        description = self.desc_text.get('1.0', tk.END).strip()
        category = self.category_var.get()
        priority = self.priority_var.get()

        due_date_str = self.date_entry.get().strip()
        due_date = None
        if due_date_str:
            try:
                parsed_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d')
                due_date = parsed_date.isoformat()
            except ValueError:
                messagebox.showerror('错误', '日期格式无效，请使用 YYYY-MM-DD 格式！', parent=self)
                self.date_entry.focus_set()
                return

        self.result = {
            'title': title,
            'description': description,
            'category': category,
            'priority': priority,
            'due_date': due_date
        }

        self.destroy()

    def show(self) -> Optional[Dict[str, Any]]:
        self.wait_window()
        return self.result

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent: tk.Widget, theme_name: str, topmost: bool, *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.theme_name = theme_name
        self.topmost = topmost
        self.colors = Theme.get_colors(theme_name)
        self.result: Optional[Dict[str, Any]] = None

        self.title('设置')
        self.geometry('400x250')
        self.resizable(False, False)
        self.configure(bg=self.colors['bg'])

        self.transient(parent)
        self.grab_set()

        self._setup_ui()
        self.center_window()

    def center_window(self) -> None:
        self.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - self.winfo_width()) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f'+{x}+{y}')

    def _setup_ui(self) -> None:
        padding = {'padx': 30, 'pady': 20}

        main_frame = tk.Frame(self, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, **padding)

        tk.Label(
            main_frame,
            text='主题',
            font=Theme.get_font('normal', bold=True),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        ).grid(row=0, column=0, sticky='w', pady=(0, 10))

        self.theme_var = tk.StringVar(value=self.theme_name)
        theme_combo = StyledCombobox(
            main_frame,
            self.colors,
            textvariable=self.theme_var,
            values=['light', 'dark'],
            width=15
        )
        theme_combo.grid(row=1, column=0, sticky='w', pady=(0, 20))

        self.topmost_var = tk.BooleanVar(value=self.topmost)
        topmost_check = tk.Checkbutton(
            main_frame,
            text='窗口置顶',
            variable=self.topmost_var,
            font=Theme.get_font('normal'),
            fg=self.colors['fg'],
            bg=self.colors['bg'],
            activebackground=self.colors['bg'],
            activeforeground=self.colors['fg'],
            selectcolor=self.colors['input_bg']
        )
        topmost_check.grid(row=2, column=0, sticky='w', pady=(0, 30))

        btn_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        btn_frame.grid(row=3, column=0, sticky='e')

        StyledButton(
            btn_frame,
            '取消',
            self.colors,
            style='default',
            command=self.destroy
        ).grid(row=0, column=0, padx=(0, 10))

        StyledButton(
            btn_frame,
            '保存',
            self.colors,
            style='primary',
            command=self._on_save
        ).grid(row=0, column=1)

        main_frame.grid_columnconfigure(0, weight=1)

    def _on_save(self) -> None:
        self.result = {
            'theme': self.theme_var.get(),
            'topmost': self.topmost_var.get()
        }
        self.destroy()

    def show(self) -> Optional[Dict[str, Any]]:
        self.wait_window()
        return self.result