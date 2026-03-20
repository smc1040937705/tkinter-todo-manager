"""
待办事项数据模型
"""
from datetime import datetime
from enum import Enum
import uuid


class Priority(Enum):
    """优先级枚举"""
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"


class Category(Enum):
    """分类枚举"""
    WORK = "工作"
    STUDY = "学习"
    LIFE = "生活"


class TodoItem:
    """待办事项类"""

    def __init__(self, title, category=Category.WORK, priority=Priority.MEDIUM,
                 due_date=None, description="", completed=False, todo_id=None):
        self.id = todo_id or str(uuid.uuid4())
        self.title = title
        self.category = category if isinstance(category, Category) else Category(category)
        self.priority = priority if isinstance(priority, Priority) else Priority(priority)
        self.due_date = due_date  # 格式: "YYYY-MM-DD"
        self.description = description
        self.completed = completed
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self):
        """转换为字典，用于JSON序列化"""
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category.value,
            "priority": self.priority.value,
            "due_date": self.due_date,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        todo = cls(
            title=data["title"],
            category=data.get("category", "工作"),
            priority=data.get("priority", "中"),
            due_date=data.get("due_date"),
            description=data.get("description", ""),
            completed=data.get("completed", False),
            todo_id=data.get("id")
        )
        todo.created_at = data.get("created_at", datetime.now().isoformat())
        todo.updated_at = data.get("updated_at", datetime.now().isoformat())
        return todo

    def update(self, **kwargs):
        """更新待办事项"""
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ["id", "created_at"]:
                if key == "category":
                    value = Category(value) if not isinstance(value, Category) else value
                elif key == "priority":
                    value = Priority(value) if not isinstance(value, Priority) else value
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()

    def mark_complete(self):
        """标记为完成"""
        self.completed = True
        self.updated_at = datetime.now().isoformat()

    def mark_incomplete(self):
        """标记为未完成"""
        self.completed = False
        self.updated_at = datetime.now().isoformat()

    def is_overdue(self):
        """检查是否已逾期"""
        if not self.due_date or self.completed:
            return False
        try:
            due = datetime.strptime(self.due_date, "%Y-%m-%d")
            return due < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            return False

    def is_due_today(self):
        """检查是否今天到期"""
        if not self.due_date:
            return False
        try:
            due = datetime.strptime(self.due_date, "%Y-%m-%d")
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            return due == today
        except ValueError:
            return False

    def __repr__(self):
        return f"<TodoItem {self.title} ({self.category.value})>"


class TodoManager:
    """待办事项管理器"""

    def __init__(self):
        self.todos = []

    def add(self, todo):
        """添加待办事项"""
        if isinstance(todo, dict):
            todo = TodoItem.from_dict(todo)
        self.todos.append(todo)
        return todo

    def delete(self, todo_id):
        """删除待办事项"""
        for i, todo in enumerate(self.todos):
            if todo.id == todo_id:
                del self.todos[i]
                return True
        return False

    def get(self, todo_id):
        """获取单个待办事项"""
        for todo in self.todos:
            if todo.id == todo_id:
                return todo
        return None

    def update(self, todo_id, **kwargs):
        """更新待办事项"""
        todo = self.get(todo_id)
        if todo:
            todo.update(**kwargs)
            return True
        return False

    def get_all(self):
        """获取所有待办事项"""
        return self.todos.copy()

    def get_by_category(self, category):
        """按分类筛选"""
        cat = category if isinstance(category, Category) else Category(category)
        return [t for t in self.todos if t.category == cat]

    def get_by_priority(self, priority):
        """按优先级筛选"""
        pri = priority if isinstance(priority, Priority) else Priority(priority)
        return [t for t in self.todos if t.priority == pri]

    def get_completed(self):
        """获取已完成的待办事项"""
        return [t for t in self.todos if t.completed]

    def get_incomplete(self):
        """获取未完成的待办事项"""
        return [t for t in self.todos if not t.completed]

    def get_overdue(self):
        """获取已逾期的待办事项"""
        return [t for t in self.todos if t.is_overdue()]

    def get_due_today(self):
        """获取今天到期的待办事项"""
        return [t for t in self.todos if t.is_due_today()]

    def search(self, keyword):
        """搜索待办事项"""
        keyword = keyword.lower()
        results = []
        for todo in self.todos:
            if (keyword in todo.title.lower() or
                keyword in todo.description.lower() or
                keyword in todo.category.value.lower()):
                results.append(todo)
        return results

    def sort_by_date(self, reverse=False):
        """按日期排序"""
        def get_date(todo):
            if todo.due_date:
                try:
                    return datetime.strptime(todo.due_date, "%Y-%m-%d")
                except ValueError:
                    pass
            return datetime.max
        return sorted(self.todos, key=get_date, reverse=reverse)

    def sort_by_priority(self, reverse=True):
        """按优先级排序（高->低）"""
        priority_order = {Priority.HIGH: 3, Priority.MEDIUM: 2, Priority.LOW: 1}
        return sorted(self.todos, key=lambda t: priority_order.get(t.priority, 0), reverse=reverse)

    def clear_completed(self):
        """清除已完成的待办事项"""
        self.todos = [t for t in self.todos if not t.completed]

    def to_list(self):
        """转换为列表，用于JSON序列化"""
        return [todo.to_dict() for todo in self.todos]

    @classmethod
    def from_list(cls, data_list):
        """从列表创建管理器"""
        manager = cls()
        for data in data_list:
            manager.add(TodoItem.from_dict(data))
        return manager
