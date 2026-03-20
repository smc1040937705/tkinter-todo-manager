import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import datetime
from .theme import Theme
from .widgets import ScrollableFrame, TodoCard, StyledButton, StyledEntry, StyledCombobox
from .dialogs import TodoDialog, SettingsDialog
from models.todo import Todo, TodoManager, CATEGORIES, PRIORITIES

class MainWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.todo_manager = TodoManager()
        self.theme_name = 'light'
        self.topmost = False
        self.colors = Theme.get_colors(self.theme_name)

        self._setup_window()
        self._create_menu()
        self._setup_ui()
        self._load_todos()
        self._check_reminders()
        self._start_reminder_check()

    def _setup_window(self) -> None:
        self.root.title('待办管理器')
        self.root.geometry('800x600')
        self.root.minsize(600, 500)
        self.root.configure(bg=self.colors['bg'])

        try:
            self.root.iconbitmap(default='')
        except:
            pass

    def _create_menu(self) -> None:
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='文件', menu=file_menu)
        file_menu.add_command(label='新建待办', command=self._on_add_todo)
        file_menu.add_separator()
        file_menu.add_command(label='退出', command=self.root.quit)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='视图', menu=view_menu)
        view_menu.add_command(label='切换主题', command=self._toggle_theme)
        view_menu.add_command(label='窗口置顶', command=self._toggle_topmost)

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='帮助', menu=help_menu)
        help_menu.add_command(label='关于', command=self._show_about)

    def _setup_ui(self) -> None:
        self._setup_toolbar()
        self._setup_filter_bar()
        self._setup_todo_list()
        self._setup_status_bar()

    def _setup_toolbar(self) -> None:
        toolbar = tk.Frame(self.root, bg=self.colors['card_bg'], relief='raised', bd=1)
        toolbar.pack(fill='x', padx=10, pady=(10, 0))

        self.add_btn = StyledButton(
            toolbar,
            '添加待办',
            self.colors,
            style='primary',
            command=self._on_add_todo
        )
        self.add_btn.pack(side='left', padx=10, pady=8)

        self.settings_btn = StyledButton(
            toolbar,
            '设置',
            self.colors,
            style='default',
            command=self._on_settings
        )
        self.settings_btn.pack(side='right', padx=10, pady=8)

        self.refresh_btn = StyledButton(
            toolbar,
            '刷新',
            self.colors,
            style='default',
            command=self._load_todos
        )
        self.refresh_btn.pack(side='right', padx=(0, 10), pady=8)

    def _setup_filter_bar(self) -> None:
        filter_bar = tk.Frame(self.root, bg=self.colors['bg'])
        filter_bar.pack(fill='x', padx=10, pady=10)

        tk.Label(
            filter_bar,
            text='搜索:',
            font=Theme.get_font('normal'),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        ).pack(side='left', padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._on_filter_change())
        self.search_entry = StyledEntry(
            filter_bar,
            self.colors,
            textvariable=self.search_var,
            width=20
        )
        self.search_entry.pack(side='left', padx=(0, 20))

        tk.Label(
            filter_bar,
            text='分类:',
            font=Theme.get_font('normal'),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        ).pack(side='left', padx=(0, 5))

        self.category_var = tk.StringVar(value='全部')
        self.category_combo = StyledCombobox(
            filter_bar,
            self.colors,
            textvariable=self.category_var,
            values=['全部'] + CATEGORIES,
            width=10
        )
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self._on_filter_change())
        self.category_combo.pack(side='left', padx=(0, 20))

        tk.Label(
            filter_bar,
            text='优先级:',
            font=Theme.get_font('normal'),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        ).pack(side='left', padx=(0, 5))

        self.priority_var = tk.StringVar(value='全部')
        self.priority_combo = StyledCombobox(
            filter_bar,
            self.colors,
            textvariable=self.priority_var,
            values=['全部'] + PRIORITIES,
            width=10
        )
        self.priority_combo.bind('<<ComboboxSelected>>', lambda e: self._on_filter_change())
        self.priority_combo.pack(side='left', padx=(0, 20))

        tk.Label(
            filter_bar,
            text='状态:',
            font=Theme.get_font('normal'),
            fg=self.colors['fg'],
            bg=self.colors['bg']
        ).pack(side='left', padx=(0, 5))

        self.status_var = tk.StringVar(value='全部')
        self.status_combo = StyledCombobox(
            filter_bar,
            self.colors,
            textvariable=self.status_var,
            values=['全部', '未完成', '已完成'],
            width=10
        )
        self.status_combo.bind('<<ComboboxSelected>>', lambda e: self._on_filter_change())
        self.status_combo.pack(side='left')

    def _setup_todo_list(self) -> None:
        list_container = tk.Frame(self.root, bg=self.colors['bg'])
        list_container.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.scroll_frame = ScrollableFrame(list_container, bg=self.colors['bg'])
        self.scroll_frame.pack(fill='both', expand=True)

    def _setup_status_bar(self) -> None:
        self.status_bar = tk.Frame(self.root, bg=self.colors['card_bg'], relief='sunken', bd=1)
        self.status_bar.pack(fill='x', side='bottom')

        self.total_label = tk.Label(
            self.status_bar,
            text='总计: 0',
            font=Theme.get_font('small'),
            fg=self.colors['fg'],
            bg=self.colors['card_bg'],
            padx=10
        )
        self.total_label.pack(side='left')

        self.completed_label = tk.Label(
            self.status_bar,
            text='已完成: 0',
            font=Theme.get_font('small'),
            fg=self.colors['fg'],
            bg=self.colors['card_bg'],
            padx=10
        )
        self.completed_label.pack(side='left')

        self.overdue_label = tk.Label(
            self.status_bar,
            text='已过期: 0',
            font=Theme.get_font('small'),
            fg=self.colors['overdue'],
            bg=self.colors['card_bg'],
            padx=10
        )
        self.overdue_label.pack(side='left')

    def _load_todos(self) -> None:
        self.scroll_frame.clear()

        category = self.category_var.get()
        priority = self.priority_var.get()
        status = self.status_var.get()
        keyword = self.search_var.get()

        completed_map = {
            '全部': None,
            '已完成': True,
            '未完成': False
        }
        completed_filter = completed_map.get(status)

        todos = self.todo_manager.filter_todos(
            category=category,
            priority=priority,
            completed=completed_filter,
            keyword=keyword
        )

        todos = self.todo_manager.sort_todos(todos, sort_by='due_date')

        if not todos:
            empty_label = tk.Label(
                self.scroll_frame.scrollable_frame,
                text='暂无待办事项',
                font=Theme.get_font('large'),
                fg=self.colors['completed'],
                bg=self.colors['bg']
            )
            empty_label.pack(pady=50)
        else:
            for todo in todos:
                card = TodoCard(
                    self.scroll_frame.scrollable_frame,
                    todo,
                    self.theme_name,
                    on_toggle=self._on_toggle_todo,
                    on_edit=self._on_edit_todo,
                    on_delete=self._on_delete_todo
                )
                card.pack(fill='x', padx=5, pady=5)

        self._update_status()

    def _update_status(self) -> None:
        all_todos = self.todo_manager.get_all_todos()
        total = len(all_todos)
        completed = sum(1 for t in all_todos if t.completed)
        overdue = sum(1 for t in all_todos if t.is_overdue())

        self.total_label.config(text=f'总计: {total}')
        self.completed_label.config(text=f'已完成: {completed}')
        self.overdue_label.config(text=f'已过期: {overdue}')

    def _on_filter_change(self, *args: any) -> None:
        self._load_todos()

    def _on_add_todo(self) -> None:
        dialog = TodoDialog(self.root, self.theme_name)
        result = dialog.show()
        if result:
            todo = Todo(**result)
            self.todo_manager.add_todo(todo)
            self._load_todos()

    def _on_edit_todo(self, todo_id: int) -> None:
        todo = self.todo_manager.get_todo(todo_id)
        if todo:
            dialog = TodoDialog(self.root, self.theme_name, todo)
            result = dialog.show()
            if result:
                self.todo_manager.update_todo(todo_id, **result)
                self._load_todos()

    def _on_delete_todo(self, todo_id: int) -> None:
        todo = self.todo_manager.get_todo(todo_id)
        if todo:
            result = messagebox.askyesno(
                '确认删除',
                f'确定要删除待办事项 "{todo.title}" 吗？',
                parent=self.root
            )
            if result:
                self.todo_manager.delete_todo(todo_id)
                self._load_todos()

    def _on_toggle_todo(self, todo_id: int) -> None:
        self.todo_manager.toggle_completed(todo_id)
        self._load_todos()

    def _on_settings(self) -> None:
        dialog = SettingsDialog(self.root, self.theme_name, self.topmost)
        result = dialog.show()
        if result:
            if result['theme'] != self.theme_name:
                self.theme_name = result['theme']
                self._apply_theme()
            if result['topmost'] != self.topmost:
                self.topmost = result['topmost']
                self.root.attributes('-topmost', self.topmost)

    def _apply_theme(self) -> None:
        self.colors = Theme.get_colors(self.theme_name)
        self.root.configure(bg=self.colors['bg'])

        # 重新创建UI组件以确保主题正确应用
        for widget in self.root.winfo_children():
            widget.destroy()

        self._setup_ui()
        self._load_todos()

    def _toggle_theme(self) -> None:
        self.theme_name = 'dark' if self.theme_name == 'light' else 'light'
        self._apply_theme()

    def _toggle_topmost(self) -> None:
        self.topmost = not self.topmost
        self.root.attributes('-topmost', self.topmost)

    def _show_about(self) -> None:
        messagebox.showinfo(
            '关于',
            '待办管理器 v1.0\n\n'
            '基于 Python + Tkinter 开发\n'
            '支持添加、编辑、删除、标记完成待办事项\n'
            '支持分类、优先级、截止日期设置\n'
            '数据持久化到本地 JSON 文件',
            parent=self.root
        )

    def _check_reminders(self) -> None:
        overdue_todos = self.todo_manager.get_overdue_todos()
        if overdue_todos:
            overdue_count = len(overdue_todos)
            if overdue_count == 1:
                todo = overdue_todos[0]
                message = f'待办事项 "{todo.title}" 已过期！'
            else:
                message = f'有 {overdue_count} 个待办事项已过期！\n\n'
                for todo in overdue_todos[:5]:
                    message += f'- {todo.title}\n'
                if overdue_count > 5:
                    message += f'...还有 {overdue_count - 5} 个'

            messagebox.showwarning('到期提醒', message, parent=self.root)

        due_soon = self.todo_manager.get_due_soon_todos(days=1)
        if due_soon and not overdue_todos:
            message = '以下待办事项将在今天到期：\n\n'
            for todo in due_soon:
                message += f'- {todo.title}\n'
            messagebox.showinfo('今日提醒', message, parent=self.root)

    def _start_reminder_check(self) -> None:
        def check() -> None:
            now = datetime.datetime.now()
            if now.hour == 9 and now.minute == 0:
                self._check_reminders()
            self.root.after(60000, check)

        self.root.after(1000, check)