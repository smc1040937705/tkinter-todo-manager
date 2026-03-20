import tkinter as tk
from tkinter import ttk
from typing import Callable, Any, Dict
from .theme import Theme
from models.todo import Todo

class ScrollableFrame(tk.Frame):
    def __init__(self, parent: tk.Widget, *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self._window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.scrollable_frame.bind('<Enter>', self._bind_mousewheel)
        self.scrollable_frame.bind('<Leave>', self._unbind_mousewheel)

    def _on_canvas_configure(self, event: tk.Event) -> None:
        canvas_width = event.width
        self.canvas.itemconfig(self._window_id, width=canvas_width)

    def _bind_mousewheel(self, event: tk.Event) -> None:
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mousewheel(self, event: tk.Event) -> None:
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event: tk.Event) -> None:
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear(self) -> None:
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

class TodoCard(tk.Frame):
    def __init__(self, parent: tk.Widget, todo: Todo, theme_name: str,
                 on_toggle: Callable[[int], None],
                 on_edit: Callable[[int], None],
                 on_delete: Callable[[int], None],
                 *args: Any, **kwargs: Any) -> None:
        super().__init__(parent, *args, **kwargs)
        self.todo = todo
        self.theme_name = theme_name
        self.colors = Theme.get_colors(theme_name)
        self.on_toggle = on_toggle
        self.on_edit = on_edit
        self.on_delete = on_delete

        self._setup_ui()

    def _setup_ui(self) -> None:
        bg_color = self.colors['card_bg']
        fg_color = self.colors['completed'] if self.todo.completed else self.colors['fg']
        border_color = self.colors['card_border']

        if self.todo.is_overdue() and not self.todo.completed:
            border_color = self.colors['overdue']
            bg_color = self._lighten_color(self.colors['overdue'], 0.9) if self.theme_name == 'light' else self._darken_color(self.colors['overdue'], 0.7)

        self.config(bg=bg_color, highlightbackground=border_color, highlightthickness=1)

        left_frame = tk.Frame(self, bg=bg_color)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        title_font = Theme.get_font('medium', bold=True) if not self.todo.completed else Theme.get_font('medium')
        self.title_label = tk.Label(
            left_frame,
            text=self.todo.title,
            font=title_font,
            fg=fg_color,
            bg=bg_color,
            anchor='w'
        )
        self.title_label.pack(fill='x')

        if self.todo.description:
            self.desc_label = tk.Label(
                left_frame,
                text=self.todo.description[:100] + ('...' if len(self.todo.description) > 100 else ''),
                font=Theme.get_font('small'),
                fg=self.colors['completed'],
                bg=bg_color,
                anchor='w',
                wraplength=400
            )
            self.desc_label.pack(fill='x', pady=(2, 0))

        meta_frame = tk.Frame(left_frame, bg=bg_color)
        meta_frame.pack(fill='x', pady=(8, 0))

        priority_color = Theme.get_priority_color(self.colors, self.todo.priority)
        self.priority_label = tk.Label(
            meta_frame,
            text=f'[{self.todo.priority}]',
            font=Theme.get_font('small', bold=True),
            fg=priority_color,
            bg=bg_color
        )
        self.priority_label.pack(side='left')

        self.category_label = tk.Label(
            meta_frame,
            text=self.todo.category,
            font=Theme.get_font('small'),
            fg=self.colors['primary'],
            bg=bg_color
        )
        self.category_label.pack(side='left', padx=(10, 0))

        if self.todo.due_date:
            days_left = self.todo.days_until_due()
            due_text = f'截止: {Todo.format_date(self.todo.due_date)}'
            if days_left is not None and days_left < 0:
                due_text += ' (已过期)'
            elif days_left is not None and days_left == 0:
                due_text += ' (今天)'
            elif days_left is not None and days_left <= 3:
                due_text += f' (还有{days_left}天)'

            due_color = self.colors['overdue'] if self.todo.is_overdue() else self.colors['completed']
            self.due_label = tk.Label(
                meta_frame,
                text=due_text,
                font=Theme.get_font('small'),
                fg=due_color,
                bg=bg_color
            )
            self.due_label.pack(side='left', padx=(10, 0))

        right_frame = tk.Frame(self, bg=bg_color)
        right_frame.pack(side='right', padx=10, pady=10)

        self.check_var = tk.BooleanVar(value=self.todo.completed)
        self.check_btn = tk.Checkbutton(
            right_frame,
            variable=self.check_var,
            command=self._on_toggle,
            bg=bg_color,
            activebackground=bg_color,
            selectcolor=bg_color
        )
        self.check_btn.pack(side='left', padx=(0, 5))

        self.edit_btn = tk.Button(
            right_frame,
            text='编辑',
            font=Theme.get_font('small'),
            fg=self.colors['primary'],
            bg=bg_color,
            activebackground=self.colors['primary_hover'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            command=self._on_edit
        )
        self.edit_btn.pack(side='left', padx=2)

        self.delete_btn = tk.Button(
            right_frame,
            text='删除',
            font=Theme.get_font('small'),
            fg=self.colors['danger'],
            bg=bg_color,
            activebackground=self.colors['danger_hover'],
            activeforeground='white',
            relief='flat',
            cursor='hand2',
            command=self._on_delete
        )
        self.delete_btn.pack(side='left', padx=2)

    def _on_toggle(self) -> None:
        self.on_toggle(self.todo.id)

    def _on_edit(self) -> None:
        self.on_edit(self.todo.id)

    def _on_delete(self) -> None:
        self.on_delete(self.todo.id)

    def _lighten_color(self, color: str, factor: float) -> str:
        if color.startswith('#'):
            color = color[1:]
        r = int(color[:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:], 16)
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)
        return f'#{r:02x}{g:02x}{b:02x}'

    def _darken_color(self, color: str, factor: float) -> str:
        if color.startswith('#'):
            color = color[1:]
        r = int(color[:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:], 16)
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return f'#{r:02x}{g:02x}{b:02x}'

class StyledButton(tk.Button):
    def __init__(self, parent: tk.Widget, text: str, colors: Dict[str, str],
                 style: str = 'primary', *args: Any, **kwargs: Any) -> None:
        self.colors = colors
        self.style = style

        style_colors = {
            'primary': (colors['primary'], colors['primary_hover']),
            'success': (colors['success'], self._darken_color(colors['success'], 0.85)),
            'danger': (colors['danger'], colors['danger_hover']),
            'default': (colors['input_bg'], colors['bg']),
        }

        bg, hover_bg = style_colors.get(style, style_colors['default'])
        fg = 'white' if style != 'default' else colors['fg']
        active_fg = 'white' if style != 'default' else fg

        # 合并默认值和传入的参数
        button_kwargs = {
            'font': Theme.get_font('normal'),
            'fg': fg,
            'bg': bg,
            'activebackground': hover_bg,
            'activeforeground': active_fg,
            'relief': 'flat',
            'cursor': 'hand2',
            'padx': 15,
            'pady': 5,
        }
        button_kwargs.update(kwargs)
        
        super().__init__(
            parent,
            text=text,
            *args,
            **button_kwargs
        )

        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self._default_bg = bg
        self._hover_bg = hover_bg

    def _on_enter(self, event: tk.Event) -> None:
        self.config(bg=self._hover_bg)

    def _on_leave(self, event: tk.Event) -> None:
        self.config(bg=self._default_bg)

    def _darken_color(self, color: str, factor: float) -> str:
        if color.startswith('#'):
            color = color[1:]
        r = int(color[:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:], 16)
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        return f'#{r:02x}{g:02x}{b:02x}'

class StyledEntry(tk.Entry):
    def __init__(self, parent: tk.Widget, colors: Dict[str, str], *args: Any, **kwargs: Any) -> None:
        super().__init__(
            parent,
            font=Theme.get_font('normal'),
            fg=colors['fg'],
            bg=colors['input_bg'],
            insertbackground=colors['fg'],
            relief='solid',
            highlightthickness=1,
            highlightbackground=colors['input_border'],
            highlightcolor=colors['primary'],
            *args,
            **kwargs
        )

class StyledCombobox(ttk.Combobox):
    def __init__(self, parent: tk.Widget, colors: Dict[str, str], *args: Any, **kwargs: Any) -> None:
        super().__init__(
            parent,
            font=Theme.get_font('normal'),
            state='readonly',
            *args,
            **kwargs
        )

class StyledText(tk.Text):
    def __init__(self, parent: tk.Widget, colors: Dict[str, str], *args: Any, **kwargs: Any) -> None:
        super().__init__(
            parent,
            font=Theme.get_font('normal'),
            fg=colors['fg'],
            bg=colors['input_bg'],
            insertbackground=colors['fg'],
            relief='solid',
            highlightthickness=1,
            highlightbackground=colors['input_border'],
            highlightcolor=colors['primary'],
            *args,
            **kwargs
        )