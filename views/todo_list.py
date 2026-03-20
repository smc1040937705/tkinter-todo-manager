import tkinter as tk
from datetime import datetime
from typing import Optional, Callable, List

from .theme import Theme
from models.todo import Todo


class TodoListView(tk.Canvas):
    def __init__(
        self,
        parent: tk.Widget,
        theme: Theme,
        on_select: Optional[Callable[[Optional[Todo]], None]] = None,
        on_double_click: Optional[Callable[[Todo], None]] = None
    ):
        super().__init__(parent, highlightthickness=0)
        
        self.theme = theme
        self.on_select = on_select
        self.on_double_click = on_double_click
        
        self._todos: List[Todo] = []
        self._selected_id: Optional[int] = None
        self._card_frames: List[tk.Frame] = []
        self._inner_frame: Optional[tk.Frame] = None
        
        self._setup_scroll_region()
        self._bind_events()
    
    def _setup_scroll_region(self):
        self._inner_frame = tk.Frame(self, bg=self.theme.get_color("bg"))
        
        self._window_id = self.create_window((0, 0), window=self._inner_frame, anchor="nw")
        
        self._inner_frame.bind("<Configure>", self._on_frame_configure)
        self.bind("<Configure>", self._on_canvas_configure)
    
    def _on_frame_configure(self, event):
        self.configure(scrollregion=self.bbox("all"))
    
    def _on_canvas_configure(self, event):
        self.itemconfig(self._window_id, width=event.width)
    
    def _bind_events(self):
        self.bind("<Button-1>", self._on_canvas_click)
        self.bind("<Double-Button-1>", self._on_double_click_event)
        
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Button-4>", self._on_mousewheel)
        self.bind("<Button-5>", self._on_mousewheel)
        
        self._bind_mousewheel_to_children(self._inner_frame)
    
    def _bind_mousewheel_to_children(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)
        
        for child in widget.winfo_children():
            self._bind_mousewheel_to_children(child)
    
    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.yview_scroll(1, "units")
    
    def _on_canvas_click(self, event):
        self._deselect_all()
        if self.on_select:
            self.on_select(None)
    
    def _on_double_click_event(self, event):
        if self._selected_id and self.on_double_click:
            todo = next((t for t in self._todos if t.id == self._selected_id), None)
            if todo:
                self.on_double_click(todo)
    
    def update_todos(self, todos: List[Todo]):
        self._todos = todos
        self._selected_id = None
        self._render_todos()
    
    def _render_todos(self):
        for card in self._card_frames:
            card.destroy()
        self._card_frames.clear()
        
        if not self._todos:
            self._render_empty_state()
            return
        
        colors = self.theme.get_all_colors()
        fonts = self.theme.FONTS
        
        for i, todo in enumerate(self._todos):
            card = self._create_todo_card(todo, i, colors, fonts)
            self._card_frames.append(card)
        
        self._bind_mousewheel_to_children(self._inner_frame)
    
    def _render_empty_state(self):
        colors = self.theme.get_all_colors()
        fonts = self.theme.FONTS
        
        empty_frame = tk.Frame(
            self._inner_frame,
            bg=colors["bg"],
            pady=50
        )
        empty_frame.pack(fill=tk.X)
        
        tk.Label(
            empty_frame,
            text="📝",
            font=("Segoe UI Emoji", 48),
            bg=colors["bg"],
            fg=colors["disabled"]
        ).pack()
        
        tk.Label(
            empty_frame,
            text="暂无待办事项",
            font=fonts["subtitle"],
            bg=colors["bg"],
            fg=colors["disabled"]
        ).pack(pady=10)
        
        tk.Label(
            empty_frame,
            text="点击上方「添加待办」按钮创建新待办",
            font=fonts["normal"],
            bg=colors["bg"],
            fg=colors["disabled"]
        ).pack()
        
        self._card_frames.append(empty_frame)
    
    def _create_todo_card(
        self,
        todo: Todo,
        index: int,
        colors: dict,
        fonts: dict
    ) -> tk.Frame:
        card = tk.Frame(
            self._inner_frame,
            bg=colors["card_bg"],
            relief="solid",
            bd=1,
            pady=8,
            padx=10
        )
        card.pack(fill=tk.X, pady=3, padx=5)
        
        card.todo_id = todo.id
        
        card.bind("<Button-1>", lambda e: self._on_card_click(todo.id))
        card.bind("<Double-Button-1>", lambda e: self._on_double_click_event(e))
        
        header_frame = tk.Frame(card, bg=colors["card_bg"])
        header_frame.pack(fill=tk.X)
        header_frame.bind("<Button-1>", lambda e: self._on_card_click(todo.id))
        
        priority_color = self._get_priority_color(todo.priority, colors)
        
        priority_indicator = tk.Frame(
            header_frame,
            bg=priority_color,
            width=4
        )
        priority_indicator.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        title_frame = tk.Frame(header_frame, bg=colors["card_bg"])
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        title_frame.bind("<Button-1>", lambda e: self._on_card_click(todo.id))
        
        title_text = todo.title
        if todo.completed:
            title_text = f"✓ {title_text}"
        
        title_fg = colors["completed_fg"] if todo.completed else colors["fg"]
        if todo.is_overdue() and not todo.completed:
            title_fg = colors["overdue_fg"]
        
        title_label = tk.Label(
            title_frame,
            text=title_text,
            font=fonts["todo_title"],
            bg=colors["card_bg"],
            fg=title_fg,
            anchor="w"
        )
        title_label.pack(fill=tk.X)
        title_label.bind("<Button-1>", lambda e: self._on_card_click(todo.id))
        
        detail_frame = tk.Frame(card, bg=colors["card_bg"])
        detail_frame.pack(fill=tk.X, pady=(5, 0))
        detail_frame.bind("<Button-1>", lambda e: self._on_card_click(todo.id))
        
        category_label = tk.Label(
            detail_frame,
            text=f"📁 {todo.category}",
            font=fonts["todo_detail"],
            bg=colors["card_bg"],
            fg=colors["disabled"]
        )
        category_label.pack(side=tk.LEFT)
        category_label.bind("<Button-1>", lambda e: self._on_card_click(todo.id))
        
        priority_text = Todo.PRIORITIES.get(todo.priority, "中")
        priority_label = tk.Label(
            detail_frame,
            text=f"⚡ {priority_text}",
            font=fonts["todo_detail"],
            bg=colors["card_bg"],
            fg=priority_color
        )
        priority_label.pack(side=tk.LEFT, padx=(15, 0))
        priority_label.bind("<Button-1>", lambda e: self._on_card_click(todo.id))
        
        if todo.due_date:
            due_text = self._format_due_date(todo.due_date, todo.is_overdue())
            due_fg = colors["overdue_fg"] if todo.is_overdue() else colors["disabled"]
            
            due_label = tk.Label(
                detail_frame,
                text=due_text,
                font=fonts["todo_detail"],
                bg=colors["card_bg"],
                fg=due_fg
            )
            due_label.pack(side=tk.RIGHT)
            due_label.bind("<Button-1>", lambda e: self._on_card_click(todo.id))
        
        return card
    
    def _get_priority_color(self, priority: int, colors: dict) -> str:
        if priority == Todo.PRIORITY_HIGH:
            return colors["priority_high"]
        elif priority == Todo.PRIORITY_MEDIUM:
            return colors["priority_medium"]
        return colors["priority_low"]
    
    def _format_due_date(self, due_date: datetime, is_overdue: bool) -> str:
        now = datetime.now()
        diff = due_date - now
        
        if is_overdue:
            days = abs(diff.days)
            if days == 0:
                return "⏰ 已过期"
            elif days == 1:
                return "⏰ 昨天过期"
            else:
                return f"⏰ {days}天前过期"
        
        if diff.days == 0:
            hours = diff.seconds // 3600
            if hours == 0:
                minutes = diff.seconds // 60
                return f"⏰ {minutes}分钟后"
            return f"⏰ 今天 {due_date.strftime('%H:%M')}"
        elif diff.days == 1:
            return f"⏰ 明天 {due_date.strftime('%H:%M')}"
        else:
            return f"⏰ {due_date.strftime('%m-%d %H:%M')}"
    
    def _on_card_click(self, todo_id: int):
        self._deselect_all()
        self._selected_id = todo_id
        
        for card in self._card_frames:
            if hasattr(card, 'todo_id') and card.todo_id == todo_id:
                colors = self.theme.get_all_colors()
                card.configure(bg=colors["accent"], bd=2)
                self._update_card_colors(card, colors["accent"], "white")
                break
        
        if self.on_select:
            todo = next((t for t in self._todos if t.id == todo_id), None)
            self.on_select(todo)
    
    def _deselect_all(self):
        colors = self.theme.get_all_colors()
        for card in self._card_frames:
            if hasattr(card, 'todo_id'):
                card.configure(bg=colors["card_bg"], bd=1)
                self._update_card_colors(card, colors["card_bg"], colors["fg"])
    
    def _update_card_colors(self, card: tk.Frame, bg_color: str, fg_color: str):
        for widget in card.winfo_children():
            if isinstance(widget, tk.Frame):
                if not hasattr(widget, '_is_priority_indicator'):
                    widget.configure(bg=bg_color)
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=bg_color)
                    elif isinstance(child, tk.Frame):
                        child.configure(bg=bg_color)
                        for subchild in child.winfo_children():
                            if isinstance(subchild, tk.Label):
                                subchild.configure(bg=bg_color)
            elif isinstance(widget, tk.Label):
                widget.configure(bg=bg_color)
    
    def get_selected(self) -> Optional[Todo]:
        if self._selected_id:
            return next((t for t in self._todos if t.id == self._selected_id), None)
        return None
    
    def apply_theme(self):
        colors = self.theme.get_all_colors()
        self.configure(bg=colors["bg"])
        self._inner_frame.configure(bg=colors["bg"])
        self._render_todos()
