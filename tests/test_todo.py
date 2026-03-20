"""
待办事项CRUD操作测试
"""
import unittest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from models.todo import TodoItem, TodoManager, Category, Priority


class TestTodoItem(unittest.TestCase):
    """测试待办事项类"""

    def test_create_todo(self):
        """测试创建待办事项"""
        todo = TodoItem(
            title="测试待办",
            category=Category.WORK,
            priority=Priority.HIGH,
            due_date="2025-12-31",
            description="这是一个测试"
        )
        
        self.assertEqual(todo.title, "测试待办")
        self.assertEqual(todo.category, Category.WORK)
        self.assertEqual(todo.priority, Priority.HIGH)
        self.assertEqual(todo.due_date, "2025-12-31")
        self.assertEqual(todo.description, "这是一个测试")
        self.assertFalse(todo.completed)
        self.assertIsNotNone(todo.id)
        self.assertIsNotNone(todo.created_at)

    def test_create_todo_with_string_category(self):
        """测试使用字符串创建分类"""
        todo = TodoItem(title="测试", category="学习")
        self.assertEqual(todo.category, Category.STUDY)

    def test_create_todo_with_string_priority(self):
        """测试使用字符串创建优先级"""
        todo = TodoItem(title="测试", priority="高")
        self.assertEqual(todo.priority, Priority.HIGH)

    def test_default_values(self):
        """测试默认值"""
        todo = TodoItem(title="测试")
        self.assertEqual(todo.category, Category.WORK)
        self.assertEqual(todo.priority, Priority.MEDIUM)
        self.assertIsNone(todo.due_date)
        self.assertEqual(todo.description, "")

    def test_mark_complete(self):
        """测试标记完成"""
        todo = TodoItem(title="测试")
        self.assertFalse(todo.completed)
        
        todo.mark_complete()
        self.assertTrue(todo.completed)

    def test_mark_incomplete(self):
        """测试标记未完成"""
        todo = TodoItem(title="测试", completed=True)
        self.assertTrue(todo.completed)
        
        todo.mark_incomplete()
        self.assertFalse(todo.completed)

    def test_update(self):
        """测试更新待办事项"""
        todo = TodoItem(title="原始标题", category=Category.WORK)
        
        todo.update(title="新标题", category=Category.STUDY, priority=Priority.HIGH)
        
        self.assertEqual(todo.title, "新标题")
        self.assertEqual(todo.category, Category.STUDY)
        self.assertEqual(todo.priority, Priority.HIGH)

    def test_to_dict(self):
        """测试转换为字典"""
        todo = TodoItem(
            title="测试",
            category=Category.WORK,
            priority=Priority.HIGH,
            due_date="2025-12-31"
        )
        
        data = todo.to_dict()
        
        self.assertEqual(data["title"], "测试")
        self.assertEqual(data["category"], "工作")
        self.assertEqual(data["priority"], "高")
        self.assertEqual(data["due_date"], "2025-12-31")
        self.assertIn("id", data)
        self.assertIn("created_at", data)

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "id": "test-id-123",
            "title": "测试",
            "category": "学习",
            "priority": "高",
            "due_date": "2025-12-31",
            "description": "描述",
            "completed": True,
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-02T00:00:00"
        }
        
        todo = TodoItem.from_dict(data)
        
        self.assertEqual(todo.id, "test-id-123")
        self.assertEqual(todo.title, "测试")
        self.assertEqual(todo.category, Category.STUDY)
        self.assertEqual(todo.priority, Priority.HIGH)
        self.assertTrue(todo.completed)

    def test_is_overdue(self):
        """测试逾期检查"""
        # 已逾期的待办
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        overdue_todo = TodoItem(title="逾期", due_date=yesterday)
        self.assertTrue(overdue_todo.is_overdue())
        
        # 未逾期的待办
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        future_todo = TodoItem(title="未来", due_date=tomorrow)
        self.assertFalse(future_todo.is_overdue())
        
        # 已完成的待办不算逾期
        completed_todo = TodoItem(title="已完成", due_date=yesterday, completed=True)
        self.assertFalse(completed_todo.is_overdue())
        
        # 无日期的待办不算逾期
        no_date_todo = TodoItem(title="无日期")
        self.assertFalse(no_date_todo.is_overdue())

    def test_is_due_today(self):
        """测试今天到期检查"""
        today = datetime.now().strftime("%Y-%m-%d")
        today_todo = TodoItem(title="今天", due_date=today)
        self.assertTrue(today_todo.is_due_today())
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow_todo = TodoItem(title="明天", due_date=tomorrow)
        self.assertFalse(tomorrow_todo.is_due_today())


class TestTodoManager(unittest.TestCase):
    """测试待办事项管理器"""

    def setUp(self):
        """测试前准备"""
        self.manager = TodoManager()

    def test_add_todo(self):
        """测试添加待办"""
        todo = TodoItem(title="测试")
        result = self.manager.add(todo)
        
        self.assertEqual(result, todo)
        self.assertEqual(len(self.manager.todos), 1)

    def test_add_dict(self):
        """测试添加字典"""
        data = {"title": "字典测试", "category": "工作"}
        result = self.manager.add(data)
        
        self.assertIsInstance(result, TodoItem)
        self.assertEqual(result.title, "字典测试")

    def test_delete_todo(self):
        """测试删除待办"""
        todo = TodoItem(title="测试")
        self.manager.add(todo)
        
        result = self.manager.delete(todo.id)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.todos), 0)
        
        # 删除不存在的ID
        result = self.manager.delete("non-existent")
        self.assertFalse(result)

    def test_get_todo(self):
        """测试获取单个待办"""
        todo = TodoItem(title="测试")
        self.manager.add(todo)
        
        result = self.manager.get(todo.id)
        self.assertEqual(result, todo)
        
        # 获取不存在的ID
        result = self.manager.get("non-existent")
        self.assertIsNone(result)

    def test_update_todo(self):
        """测试更新待办"""
        todo = TodoItem(title="原始")
        self.manager.add(todo)
        
        result = self.manager.update(todo.id, title="更新后")
        self.assertTrue(result)
        self.assertEqual(todo.title, "更新后")
        
        # 更新不存在的ID
        result = self.manager.update("non-existent", title="测试")
        self.assertFalse(result)

    def test_get_by_category(self):
        """测试按分类获取"""
        work_todo = TodoItem(title="工作", category=Category.WORK)
        study_todo = TodoItem(title="学习", category=Category.STUDY)
        
        self.manager.add(work_todo)
        self.manager.add(study_todo)
        
        work_items = self.manager.get_by_category(Category.WORK)
        self.assertEqual(len(work_items), 1)
        self.assertEqual(work_items[0].title, "工作")

    def test_get_by_priority(self):
        """测试按优先级获取"""
        high_todo = TodoItem(title="高", priority=Priority.HIGH)
        low_todo = TodoItem(title="低", priority=Priority.LOW)
        
        self.manager.add(high_todo)
        self.manager.add(low_todo)
        
        high_items = self.manager.get_by_priority(Priority.HIGH)
        self.assertEqual(len(high_items), 1)
        self.assertEqual(high_items[0].title, "高")

    def test_get_completed(self):
        """测试获取已完成"""
        completed = TodoItem(title="已完成", completed=True)
        incomplete = TodoItem(title="未完成")
        
        self.manager.add(completed)
        self.manager.add(incomplete)
        
        completed_items = self.manager.get_completed()
        self.assertEqual(len(completed_items), 1)
        self.assertEqual(completed_items[0].title, "已完成")

    def test_get_incomplete(self):
        """测试获取未完成"""
        completed = TodoItem(title="已完成", completed=True)
        incomplete = TodoItem(title="未完成")
        
        self.manager.add(completed)
        self.manager.add(incomplete)
        
        incomplete_items = self.manager.get_incomplete()
        self.assertEqual(len(incomplete_items), 1)
        self.assertEqual(incomplete_items[0].title, "未完成")

    def test_get_overdue(self):
        """测试获取逾期"""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        overdue = TodoItem(title="逾期", due_date=yesterday)
        future = TodoItem(title="未来", due_date="2099-12-31")
        
        self.manager.add(overdue)
        self.manager.add(future)
        
        overdue_items = self.manager.get_overdue()
        self.assertEqual(len(overdue_items), 1)
        self.assertEqual(overdue_items[0].title, "逾期")

    def test_clear_completed(self):
        """测试清除已完成"""
        self.manager.add(TodoItem(title="已完成1", completed=True))
        self.manager.add(TodoItem(title="已完成2", completed=True))
        self.manager.add(TodoItem(title="未完成"))
        
        self.manager.clear_completed()
        
        self.assertEqual(len(self.manager.todos), 1)
        self.assertEqual(self.manager.todos[0].title, "未完成")

    def test_to_list(self):
        """测试转换为列表"""
        self.manager.add(TodoItem(title="测试1"))
        self.manager.add(TodoItem(title="测试2"))
        
        data_list = self.manager.to_list()
        
        self.assertEqual(len(data_list), 2)
        self.assertEqual(data_list[0]["title"], "测试1")
        self.assertEqual(data_list[1]["title"], "测试2")

    def test_from_list(self):
        """测试从列表创建"""
        data_list = [
            {"title": "测试1", "category": "工作"},
            {"title": "测试2", "category": "学习"}
        ]
        
        manager = TodoManager.from_list(data_list)
        
        self.assertEqual(len(manager.todos), 2)
        self.assertEqual(manager.todos[0].title, "测试1")
        self.assertEqual(manager.todos[1].title, "测试2")


if __name__ == "__main__":
    unittest.main()
