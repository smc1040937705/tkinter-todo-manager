import json
import os
from datetime import datetime
from typing import List, Optional
from .todo import Todo


class DataManager:
    def __init__(self, data_path: Optional[str] = None):
        if data_path is None:
            user_home = os.path.expanduser("~")
            self.data_dir = os.path.join(user_home, ".todo_app")
            self.data_path = os.path.join(self.data_dir, "data.json")
        else:
            self.data_path = data_path
            self.data_dir = os.path.dirname(data_path)
        
        self._todos: List[Todo] = []
        self._next_id = 1
        self._ensure_data_dir()
        self.load()
    
    def _ensure_data_dir(self) -> None:
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def load(self) -> bool:
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._todos = [Todo.from_dict(item) for item in data.get("todos", [])]
                    self._next_id = data.get("next_id", 1)
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"加载数据失败: {e}")
            self._todos = []
            self._next_id = 1
            return False
    
    def save(self) -> bool:
        try:
            self._ensure_data_dir()
            data = {
                "todos": [todo.to_dict() for todo in self._todos],
                "next_id": self._next_id
            }
            with open(self.data_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            print(f"保存数据失败: {e}")
            return False
    
    def add(self, todo: Todo) -> Todo:
        todo.id = self._next_id
        self._next_id += 1
        self._todos.append(todo)
        self.save()
        return todo
    
    def update(self, todo: Todo) -> bool:
        for i, t in enumerate(self._todos):
            if t.id == todo.id:
                self._todos[i] = todo
                self.save()
                return True
        return False
    
    def delete(self, todo_id: int) -> bool:
        for i, todo in enumerate(self._todos):
            if todo.id == todo_id:
                del self._todos[i]
                self.save()
                return True
        return False
    
    def get(self, todo_id: int) -> Optional[Todo]:
        for todo in self._todos:
            if todo.id == todo_id:
                return todo
        return None
    
    def get_all(self) -> List[Todo]:
        return self._todos.copy()
    
    def get_by_category(self, category: str) -> List[Todo]:
        return [todo for todo in self._todos if todo.category == category]
    
    def get_by_priority(self, priority: int) -> List[Todo]:
        return [todo for todo in self._todos if todo.priority == priority]
    
    def get_completed(self) -> List[Todo]:
        return [todo for todo in self._todos if todo.completed]
    
    def get_pending(self) -> List[Todo]:
        return [todo for todo in self._todos if not todo.completed]
    
    def get_overdue(self) -> List[Todo]:
        return [todo for todo in self._todos if todo.is_overdue()]
    
    def get_due_today(self) -> List[Todo]:
        return [todo for todo in self._todos if todo.is_due_today()]
    
    def search(self, keyword: str) -> List[Todo]:
        keyword = keyword.lower().strip()
        if not keyword:
            return []
        results = []
        for todo in self._todos:
            if (keyword in todo.title.lower() or 
                keyword in todo.description.lower() or
                keyword in todo.category.lower()):
                results.append(todo)
        return results
    
    def filter_todos(
        self,
        category: Optional[str] = None,
        priority: Optional[int] = None,
        completed: Optional[bool] = None,
        overdue_only: bool = False
    ) -> List[Todo]:
        results = self._todos.copy()
        
        if category:
            results = [t for t in results if t.category == category]
        
        if priority is not None:
            results = [t for t in results if t.priority == priority]
        
        if completed is not None:
            results = [t for t in results if t.completed == completed]
        
        if overdue_only:
            results = [t for t in results if t.is_overdue()]
        
        return results
    
    def sort_todos(
        self,
        todos: List[Todo],
        by: str = "due_date",
        reverse: bool = False
    ) -> List[Todo]:
        def sort_key(todo: Todo):
            if by == "due_date":
                return (todo.due_date is None, todo.due_date or datetime.max)
            elif by == "priority":
                return -todo.priority
            elif by == "created_at":
                return todo.created_at
            elif by == "title":
                return todo.title.lower()
            elif by == "category":
                return todo.category
            return todo.created_at
        
        return sorted(todos, key=sort_key, reverse=reverse)
    
    def toggle_complete(self, todo_id: int) -> bool:
        todo = self.get(todo_id)
        if todo:
            todo.completed = not todo.completed
            self.save()
            return True
        return False
    
    def get_statistics(self) -> dict:
        total = len(self._todos)
        completed = len(self.get_completed())
        overdue = len(self.get_overdue())
        due_today = len(self.get_due_today())
        
        by_category = {}
        for cat in Todo.CATEGORIES:
            by_category[cat] = len(self.get_by_category(cat))
        
        return {
            "total": total,
            "completed": completed,
            "pending": total - completed,
            "overdue": overdue,
            "due_today": due_today,
            "by_category": by_category
        }
