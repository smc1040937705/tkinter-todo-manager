from datetime import datetime, timedelta
from typing import Optional, Dict, Any


class Todo:
    PRIORITY_LOW = 1
    PRIORITY_MEDIUM = 2
    PRIORITY_HIGH = 3
    
    CATEGORY_WORK = "工作"
    CATEGORY_STUDY = "学习"
    CATEGORY_LIFE = "生活"
    
    PRIORITIES = {
        PRIORITY_LOW: "低",
        PRIORITY_MEDIUM: "中",
        PRIORITY_HIGH: "高"
    }
    
    CATEGORIES = [CATEGORY_WORK, CATEGORY_STUDY, CATEGORY_LIFE]
    
    def __init__(
        self,
        title: str,
        category: str = CATEGORY_WORK,
        priority: int = PRIORITY_MEDIUM,
        due_date: Optional[datetime] = None,
        description: str = "",
        completed: bool = False,
        created_at: Optional[datetime] = None,
        todo_id: Optional[int] = None
    ):
        self.id = todo_id
        self.title = title
        self.category = category
        self.priority = priority
        self.due_date = due_date
        self.description = description
        self.completed = completed
        self.created_at = created_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "due_date": self.due_date.strftime("%Y-%m-%d %H:%M") if self.due_date else None,
            "description": self.description,
            "completed": self.completed,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Todo':
        due_date = None
        if data.get("due_date"):
            try:
                due_date = datetime.strptime(data["due_date"], "%Y-%m-%d %H:%M")
            except ValueError:
                pass
        
        created_at = datetime.now()
        if data.get("created_at"):
            try:
                created_at = datetime.strptime(data["created_at"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
        
        return cls(
            todo_id=data.get("id"),
            title=data.get("title", ""),
            category=data.get("category", cls.CATEGORY_WORK),
            priority=data.get("priority", cls.PRIORITY_MEDIUM),
            due_date=due_date,
            description=data.get("description", ""),
            completed=data.get("completed", False),
            created_at=created_at
        )
    
    def is_overdue(self) -> bool:
        if self.completed or not self.due_date:
            return False
        return datetime.now() > self.due_date
    
    def is_due_today(self) -> bool:
        if not self.due_date:
            return False
        today = datetime.now().date()
        return self.due_date.date() == today
    
    def is_due_soon(self, hours: int = 24) -> bool:
        if self.completed or not self.due_date:
            return False
        time_diff = self.due_date - datetime.now()
        return timedelta(0) < time_diff <= timedelta(hours=hours)
    
    def __repr__(self) -> str:
        return f"Todo(id={self.id}, title='{self.title}', category='{self.category}', priority={self.priority}, completed={self.completed})"
