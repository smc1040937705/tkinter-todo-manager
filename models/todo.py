import json
import os
import datetime
from typing import List, Dict, Optional, Any

CATEGORIES = ['工作', '学习', '生活']
PRIORITIES = ['高', '中', '低']

class Todo:
    def __init__(self, title: str, description: str = '', category: str = '生活',
                 due_date: Optional[str] = None, priority: str = '中',
                 completed: bool = False, todo_id: Optional[int] = None,
                 created_at: Optional[str] = None):
        self.id = todo_id
        self.title = title
        self.description = description
        self.category = category if category in CATEGORIES else '生活'
        self.due_date = due_date
        self.priority = priority if priority in PRIORITIES else '中'
        self.completed = completed
        self.created_at = created_at or datetime.datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'due_date': self.due_date,
            'priority': self.priority,
            'completed': self.completed,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Todo':
        return cls(
            title=data['title'],
            description=data.get('description', ''),
            category=data.get('category', '生活'),
            due_date=data.get('due_date'),
            priority=data.get('priority', '中'),
            completed=data.get('completed', False),
            todo_id=data.get('id'),
            created_at=data.get('created_at')
        )

    def is_overdue(self) -> bool:
        if not self.due_date or self.completed:
            return False
        try:
            due = datetime.datetime.fromisoformat(self.due_date)
            return due < datetime.datetime.now()
        except (ValueError, TypeError):
            return False

    def days_until_due(self) -> Optional[int]:
        if not self.due_date:
            return None
        try:
            due = datetime.datetime.fromisoformat(self.due_date)
            delta = due.date() - datetime.datetime.now().date()
            return delta.days
        except (ValueError, TypeError):
            return None

    @staticmethod
    def validate_date(date_str: str) -> bool:
        if not date_str:
            return True
        try:
            datetime.datetime.fromisoformat(date_str)
            return True
        except ValueError:
            return False

    @staticmethod
    def format_date(date_str: str) -> str:
        if not date_str:
            return ''
        try:
            date = datetime.datetime.fromisoformat(date_str)
            return date.strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            return date_str

class TodoManager:
    def __init__(self):
        self.todos: List[Todo] = []
        self._next_id = 1
        self._data_dir = os.path.join(os.path.expanduser('~'), '.todo_app')
        self._data_file = os.path.join(self._data_dir, 'data.json')
        self._ensure_data_dir()
        self.load_from_file()

    def _ensure_data_dir(self) -> None:
        if not os.path.exists(self._data_dir):
            os.makedirs(self._data_dir)

    def add_todo(self, todo: Todo) -> Todo:
        todo.id = self._next_id
        self._next_id += 1
        self.todos.append(todo)
        self.save_to_file()
        return todo

    def update_todo(self, todo_id: int, **kwargs) -> bool:
        for todo in self.todos:
            if todo.id == todo_id:
                if 'title' in kwargs:
                    todo.title = kwargs['title']
                if 'description' in kwargs:
                    todo.description = kwargs['description']
                if 'category' in kwargs and kwargs['category'] in CATEGORIES:
                    todo.category = kwargs['category']
                if 'due_date' in kwargs:
                    todo.due_date = kwargs['due_date']
                if 'priority' in kwargs and kwargs['priority'] in PRIORITIES:
                    todo.priority = kwargs['priority']
                if 'completed' in kwargs:
                    todo.completed = kwargs['completed']
                self.save_to_file()
                return True
        return False

    def delete_todo(self, todo_id: int) -> bool:
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                del self.todos[i]
                self.save_to_file()
                return True
        return False

    def get_todo(self, todo_id: int) -> Optional[Todo]:
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None

    def get_all_todos(self) -> List[Todo]:
        return self.todos

    def toggle_completed(self, todo_id: int) -> bool:
        todo = self.get_todo(todo_id)
        if todo:
            todo.completed = not todo.completed
            self.save_to_file()
            return True
        return False

    def filter_by_category(self, category: str) -> List[Todo]:
        if category == '全部':
            return self.todos
        return [t for t in self.todos if t.category == category]

    def filter_by_priority(self, priority: str) -> List[Todo]:
        if priority == '全部':
            return self.todos
        return [t for t in self.todos if t.priority == priority]

    def filter_by_completed(self, completed: Optional[bool]) -> List[Todo]:
        if completed is None:
            return self.todos
        return [t for t in self.todos if t.completed == completed]

    def search_todos(self, keyword: str) -> List[Todo]:
        if not keyword:
            return self.todos
        keyword = keyword.lower()
        return [t for t in self.todos if keyword in t.title.lower() or keyword in t.description.lower()]

    def filter_todos(self, category: str = '全部', priority: str = '全部',
                     completed: Optional[bool] = None, keyword: str = '') -> List[Todo]:
        todos = self.todos
        if category != '全部':
            todos = [t for t in todos if t.category == category]
        if priority != '全部':
            todos = [t for t in todos if t.priority == priority]
        if completed is not None:
            todos = [t for t in todos if t.completed == completed]
        if keyword:
            keyword = keyword.lower()
            todos = [t for t in todos if keyword in t.title.lower() or keyword in t.description.lower()]
        return todos

    def sort_todos(self, todos: List[Todo], sort_by: str = 'due_date', reverse: bool = False) -> List[Todo]:
        def get_sort_key(todo: Todo) -> Any:
            if sort_by == 'due_date':
                return todo.due_date or '9999-12-31'
            elif sort_by == 'priority':
                priority_order = {'高': 0, '中': 1, '低': 2}
                return priority_order.get(todo.priority, 3)
            elif sort_by == 'created_at':
                return todo.created_at
            elif sort_by == 'completed':
                return todo.completed
            return todo.id

        return sorted(todos, key=get_sort_key, reverse=reverse)

    def get_overdue_todos(self) -> List[Todo]:
        return [t for t in self.todos if t.is_overdue()]

    def get_due_soon_todos(self, days: int = 3) -> List[Todo]:
        due_soon = []
        for todo in self.todos:
            if todo.completed:
                continue
            days_left = todo.days_until_due()
            if days_left is not None and 0 <= days_left <= days:
                due_soon.append(todo)
        return due_soon

    def save_to_file(self) -> None:
        data = {
            'next_id': self._next_id,
            'todos': [todo.to_dict() for todo in self.todos]
        }
        with open(self._data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self) -> None:
        if not os.path.exists(self._data_file):
            self.todos = []
            self._next_id = 1
            return
        try:
            with open(self._data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # 确保数据是字典格式
            if isinstance(data, dict):
                self._next_id = data.get('next_id', 1)
                self.todos = [Todo.from_dict(t) for t in data.get('todos', [])]
            else:
                # 数据格式错误，重置
                self.todos = []
                self._next_id = 1
        except (json.JSONDecodeError, IOError, KeyError, AttributeError, TypeError):
            self.todos = []
            self._next_id = 1