import unittest
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta

from models.todo import Todo
from models.data_manager import DataManager


class TestTodoModel(unittest.TestCase):
    def setUp(self):
        self.todo = Todo(
            title="测试待办",
            category=Todo.CATEGORY_WORK,
            priority=Todo.PRIORITY_HIGH,
            due_date=datetime.now() + timedelta(days=1),
            description="这是一个测试待办"
        )
    
    def test_todo_creation(self):
        self.assertEqual(self.todo.title, "测试待办")
        self.assertEqual(self.todo.category, Todo.CATEGORY_WORK)
        self.assertEqual(self.todo.priority, Todo.PRIORITY_HIGH)
        self.assertFalse(self.todo.completed)
        self.assertIsNotNone(self.todo.created_at)
    
    def test_todo_to_dict(self):
        data = self.todo.to_dict()
        self.assertEqual(data["title"], "测试待办")
        self.assertEqual(data["category"], Todo.CATEGORY_WORK)
        self.assertEqual(data["priority"], Todo.PRIORITY_HIGH)
        self.assertFalse(data["completed"])
        self.assertIsNotNone(data["due_date"])
        self.assertIsNotNone(data["created_at"])
    
    def test_todo_from_dict(self):
        data = {
            "id": 1,
            "title": "从字典创建",
            "category": Todo.CATEGORY_STUDY,
            "priority": Todo.PRIORITY_MEDIUM,
            "due_date": "2024-12-31 18:00",
            "description": "测试描述",
            "completed": True,
            "created_at": "2024-01-01 10:00:00"
        }
        todo = Todo.from_dict(data)
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.title, "从字典创建")
        self.assertEqual(todo.category, Todo.CATEGORY_STUDY)
        self.assertEqual(todo.priority, Todo.PRIORITY_MEDIUM)
        self.assertTrue(todo.completed)
        self.assertIsNotNone(todo.due_date)
    
    def test_is_overdue(self):
        overdue_todo = Todo(
            title="过期待办",
            due_date=datetime.now() - timedelta(days=1)
        )
        self.assertTrue(overdue_todo.is_overdue())
        
        future_todo = Todo(
            title="未来待办",
            due_date=datetime.now() + timedelta(days=1)
        )
        self.assertFalse(future_todo.is_overdue())
        
        completed_overdue = Todo(
            title="已完成过期",
            due_date=datetime.now() - timedelta(days=1),
            completed=True
        )
        self.assertFalse(completed_overdue.is_overdue())
    
    def test_is_due_today(self):
        today_todo = Todo(
            title="今日待办",
            due_date=datetime.now()
        )
        self.assertTrue(today_todo.is_due_today())
        
        tomorrow_todo = Todo(
            title="明日待办",
            due_date=datetime.now() + timedelta(days=1)
        )
        self.assertFalse(tomorrow_todo.is_due_today())
    
    def test_is_due_soon(self):
        soon_todo = Todo(
            title="即将到期",
            due_date=datetime.now() + timedelta(hours=12)
        )
        self.assertTrue(soon_todo.is_due_soon(24))
        
        later_todo = Todo(
            title="较晚到期",
            due_date=datetime.now() + timedelta(hours=48)
        )
        self.assertFalse(later_todo.is_due_soon(24))


class TestDataManagerCRUD(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.temp_dir, "test_data.json")
        self.data_manager = DataManager(self.data_path)
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_add_todo(self):
        todo = Todo(title="新增待办")
        added = self.data_manager.add(todo)
        
        self.assertIsNotNone(added.id)
        self.assertEqual(added.title, "新增待办")
        
        retrieved = self.data_manager.get(added.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, "新增待办")
    
    def test_update_todo(self):
        todo = Todo(title="原始标题")
        added = self.data_manager.add(todo)
        
        added.title = "更新标题"
        added.priority = Todo.PRIORITY_HIGH
        
        self.assertTrue(self.data_manager.update(added))
        
        retrieved = self.data_manager.get(added.id)
        self.assertEqual(retrieved.title, "更新标题")
        self.assertEqual(retrieved.priority, Todo.PRIORITY_HIGH)
    
    def test_delete_todo(self):
        todo = Todo(title="待删除待办")
        added = self.data_manager.add(todo)
        
        self.assertTrue(self.data_manager.delete(added.id))
        self.assertIsNone(self.data_manager.get(added.id))
        
        self.assertFalse(self.data_manager.delete(99999))
    
    def test_toggle_complete(self):
        todo = Todo(title="切换完成状态")
        added = self.data_manager.add(todo)
        
        self.assertFalse(added.completed)
        
        self.data_manager.toggle_complete(added.id)
        retrieved = self.data_manager.get(added.id)
        self.assertTrue(retrieved.completed)
        
        self.data_manager.toggle_complete(added.id)
        retrieved = self.data_manager.get(added.id)
        self.assertFalse(retrieved.completed)


class TestCategoryFilter(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.temp_dir, "test_data.json")
        self.data_manager = DataManager(self.data_path)
        
        self.todos = [
            Todo(title="工作待办1", category=Todo.CATEGORY_WORK),
            Todo(title="工作待办2", category=Todo.CATEGORY_WORK),
            Todo(title="学习待办1", category=Todo.CATEGORY_STUDY),
            Todo(title="生活待办1", category=Todo.CATEGORY_LIFE),
        ]
        
        for todo in self.todos:
            self.data_manager.add(todo)
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_get_by_category(self):
        work_todos = self.data_manager.get_by_category(Todo.CATEGORY_WORK)
        self.assertEqual(len(work_todos), 2)
        
        study_todos = self.data_manager.get_by_category(Todo.CATEGORY_STUDY)
        self.assertEqual(len(study_todos), 1)
        
        life_todos = self.data_manager.get_by_category(Todo.CATEGORY_LIFE)
        self.assertEqual(len(life_todos), 1)
    
    def test_filter_todos_by_category(self):
        filtered = self.data_manager.filter_todos(category=Todo.CATEGORY_WORK)
        self.assertEqual(len(filtered), 2)
        for todo in filtered:
            self.assertEqual(todo.category, Todo.CATEGORY_WORK)
    
    def test_filter_todos_by_priority(self):
        high_priority = Todo(title="高优先级", priority=Todo.PRIORITY_HIGH)
        self.data_manager.add(high_priority)
        
        filtered = self.data_manager.filter_todos(priority=Todo.PRIORITY_HIGH)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].priority, Todo.PRIORITY_HIGH)
    
    def test_filter_todos_by_completed(self):
        todo = self.data_manager.add(Todo(title="已完成待办"))
        self.data_manager.toggle_complete(todo.id)
        
        completed = self.data_manager.filter_todos(completed=True)
        self.assertEqual(len(completed), 1)
        self.assertTrue(completed[0].completed)
        
        pending = self.data_manager.filter_todos(completed=False)
        self.assertEqual(len(pending), 4)
        for t in pending:
            self.assertFalse(t.completed)
    
    def test_filter_todos_overdue(self):
        overdue = Todo(
            title="过期待办",
            due_date=datetime.now() - timedelta(days=1)
        )
        self.data_manager.add(overdue)
        
        overdue_todos = self.data_manager.filter_todos(overdue_only=True)
        self.assertEqual(len(overdue_todos), 1)
        self.assertTrue(overdue_todos[0].is_overdue())
    
    def test_combined_filters(self):
        todo = Todo(
            title="组合筛选测试",
            category=Todo.CATEGORY_WORK,
            priority=Todo.PRIORITY_HIGH,
            due_date=datetime.now() - timedelta(days=1)
        )
        self.data_manager.add(todo)
        
        filtered = self.data_manager.filter_todos(
            category=Todo.CATEGORY_WORK,
            priority=Todo.PRIORITY_HIGH,
            overdue_only=True
        )
        self.assertEqual(len(filtered), 1)


class TestDateValidationAndSorting(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.temp_dir, "test_data.json")
        self.data_manager = DataManager(self.data_path)
        
        now = datetime.now()
        self.todos = [
            Todo(title="昨天", due_date=now - timedelta(days=1)),
            Todo(title="今天", due_date=now),
            Todo(title="明天", due_date=now + timedelta(days=1)),
            Todo(title="下周", due_date=now + timedelta(days=7)),
            Todo(title="无日期", due_date=None),
        ]
        
        for todo in self.todos:
            self.data_manager.add(todo)
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_sort_by_due_date(self):
        todos = self.data_manager.get_all()
        sorted_todos = self.data_manager.sort_todos(todos, by="due_date")
        
        has_date = [t for t in sorted_todos if t.due_date]
        for i in range(len(has_date) - 1):
            self.assertLessEqual(has_date[i].due_date, has_date[i+1].due_date)
    
    def test_sort_by_due_date_reverse(self):
        todos = self.data_manager.get_all()
        sorted_todos = self.data_manager.sort_todos(todos, by="due_date", reverse=True)
        
        has_date = [t for t in sorted_todos if t.due_date]
        for i in range(len(has_date) - 1):
            self.assertGreaterEqual(has_date[i].due_date, has_date[i+1].due_date)
    
    def test_sort_by_priority(self):
        priorities = [
            Todo(title="低优先级", priority=Todo.PRIORITY_LOW),
            Todo(title="高优先级", priority=Todo.PRIORITY_HIGH),
            Todo(title="中优先级", priority=Todo.PRIORITY_MEDIUM),
        ]
        for t in priorities:
            self.data_manager.add(t)
        
        todos = self.data_manager.get_all()
        sorted_todos = self.data_manager.sort_todos(todos, by="priority")
        
        priority_todos = [t for t in sorted_todos if t.title in ["低优先级", "高优先级", "中优先级"]]
        self.assertEqual(priority_todos[0].priority, Todo.PRIORITY_HIGH)
        self.assertEqual(priority_todos[1].priority, Todo.PRIORITY_MEDIUM)
        self.assertEqual(priority_todos[2].priority, Todo.PRIORITY_LOW)
    
    def test_sort_by_created_at(self):
        todos = self.data_manager.get_all()
        sorted_todos = self.data_manager.sort_todos(todos, by="created_at")
        
        for i in range(len(sorted_todos) - 1):
            self.assertLessEqual(
                sorted_todos[i].created_at,
                sorted_todos[i+1].created_at
            )
    
    def test_sort_by_title(self):
        titles = ["Zebra", "Apple", "Banana", "Cherry"]
        for title in titles:
            self.data_manager.add(Todo(title=title))
        
        todos = self.data_manager.get_all()
        sorted_todos = self.data_manager.sort_todos(todos, by="title")
        
        title_todos = [t for t in sorted_todos if t.title in titles]
        expected_order = ["Apple", "Banana", "Cherry", "Zebra"]
        actual_order = [t.title for t in title_todos]
        self.assertEqual(actual_order, expected_order)
    
    def test_date_validation_in_from_dict(self):
        valid_data = {
            "title": "有效日期",
            "due_date": "2024-12-31 18:00"
        }
        todo = Todo.from_dict(valid_data)
        self.assertIsNotNone(todo.due_date)
        
        invalid_data = {
            "title": "无效日期",
            "due_date": "invalid-date"
        }
        todo = Todo.from_dict(invalid_data)
        self.assertIsNone(todo.due_date)


class TestJSONDataPersistence(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.temp_dir, "test_data.json")
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_save_and_load(self):
        dm1 = DataManager(self.data_path)
        
        todos = [
            Todo(title="待办1", category=Todo.CATEGORY_WORK, priority=Todo.PRIORITY_HIGH),
            Todo(title="待办2", category=Todo.CATEGORY_STUDY, priority=Todo.PRIORITY_MEDIUM),
            Todo(title="待办3", category=Todo.CATEGORY_LIFE, priority=Todo.PRIORITY_LOW),
        ]
        
        for todo in todos:
            dm1.add(todo)
        
        dm2 = DataManager(self.data_path)
        
        loaded_todos = dm2.get_all()
        self.assertEqual(len(loaded_todos), 3)
        
        titles = [t.title for t in loaded_todos]
        self.assertIn("待办1", titles)
        self.assertIn("待办2", titles)
        self.assertIn("待办3", titles)
    
    def test_json_file_structure(self):
        dm = DataManager(self.data_path)
        
        todo = Todo(
            title="测试JSON结构",
            category=Todo.CATEGORY_WORK,
            priority=Todo.PRIORITY_HIGH,
            due_date=datetime(2024, 12, 31, 18, 0),
            description="描述内容"
        )
        dm.add(todo)
        
        with open(self.data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.assertIn("todos", data)
        self.assertIn("next_id", data)
        self.assertEqual(data["next_id"], 2)
        self.assertEqual(len(data["todos"]), 1)
        
        todo_data = data["todos"][0]
        self.assertEqual(todo_data["title"], "测试JSON结构")
        self.assertEqual(todo_data["category"], Todo.CATEGORY_WORK)
        self.assertEqual(todo_data["priority"], Todo.PRIORITY_HIGH)
        self.assertEqual(todo_data["due_date"], "2024-12-31 18:00")
        self.assertEqual(todo_data["description"], "描述内容")
    
    def test_persist_completed_status(self):
        dm1 = DataManager(self.data_path)
        todo = dm1.add(Todo(title="完成状态测试"))
        dm1.toggle_complete(todo.id)
        
        dm2 = DataManager(self.data_path)
        loaded = dm2.get(todo.id)
        self.assertTrue(loaded.completed)
    
    def test_handle_corrupted_json(self):
        with open(self.data_path, 'w', encoding='utf-8') as f:
            f.write("invalid json content {{{")
        
        dm = DataManager(self.data_path)
        self.assertEqual(len(dm.get_all()), 0)
    
    def test_auto_create_data_directory(self):
        nested_path = os.path.join(self.temp_dir, "nested", "dir", "data.json")
        dm = DataManager(nested_path)
        
        self.assertTrue(os.path.exists(os.path.dirname(nested_path)))
        
        dm.add(Todo(title="测试"))
        self.assertTrue(os.path.exists(nested_path))


class TestSearchFunctionality(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.temp_dir, "test_data.json")
        self.data_manager = DataManager(self.data_path)
        
        self.todos = [
            Todo(title="完成项目报告", category=Todo.CATEGORY_WORK, description="季度报告"),
            Todo(title="学习Python编程", category=Todo.CATEGORY_STUDY, description="基础教程"),
            Todo(title="购买生活用品", category=Todo.CATEGORY_LIFE, description="牙膏和洗发水"),
            Todo(title="项目会议", category=Todo.CATEGORY_WORK, description="讨论项目进度"),
            Todo(title="阅读技术文档", category=Todo.CATEGORY_STUDY, description="Python高级特性"),
        ]
        
        for todo in self.todos:
            self.data_manager.add(todo)
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_search_by_title(self):
        results = self.data_manager.search("项目")
        self.assertEqual(len(results), 2)
        titles = [t.title for t in results]
        self.assertIn("完成项目报告", titles)
        self.assertIn("项目会议", titles)
    
    def test_search_by_description(self):
        results = self.data_manager.search("Python")
        self.assertEqual(len(results), 2)
        titles = [t.title for t in results]
        self.assertIn("学习Python编程", titles)
        self.assertIn("阅读技术文档", titles)
    
    def test_search_by_category(self):
        results = self.data_manager.search("工作")
        self.assertGreaterEqual(len(results), 2)
    
    def test_search_case_insensitive(self):
        results = self.data_manager.search("PYTHON")
        self.assertEqual(len(results), 2)
        
        results = self.data_manager.search("python")
        self.assertEqual(len(results), 2)
    
    def test_search_partial_match(self):
        results = self.data_manager.search("报告")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "完成项目报告")
    
    def test_search_empty_keyword(self):
        results = self.data_manager.search("")
        self.assertEqual(len(results), 0)
        
        results = self.data_manager.search("   ")
        self.assertEqual(len(results), 0)
    
    def test_search_no_match(self):
        results = self.data_manager.search("不存在的关键词xyz")
        self.assertEqual(len(results), 0)


class TestStatistics(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_path = os.path.join(self.temp_dir, "test_data.json")
        self.data_manager = DataManager(self.data_path)
    
    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_statistics(self):
        todos = [
            Todo(title="工作1", category=Todo.CATEGORY_WORK),
            Todo(title="工作2", category=Todo.CATEGORY_WORK),
            Todo(title="学习1", category=Todo.CATEGORY_STUDY),
            Todo(title="生活1", category=Todo.CATEGORY_LIFE, due_date=datetime.now() - timedelta(days=1)),
        ]
        
        for todo in todos:
            self.data_manager.add(todo)
        
        self.data_manager.toggle_complete(todos[0].id)
        
        stats = self.data_manager.get_statistics()
        
        self.assertEqual(stats["total"], 4)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["pending"], 3)
        self.assertEqual(stats["overdue"], 1)
        self.assertEqual(stats["by_category"][Todo.CATEGORY_WORK], 2)
        self.assertEqual(stats["by_category"][Todo.CATEGORY_STUDY], 1)
        self.assertEqual(stats["by_category"][Todo.CATEGORY_LIFE], 1)


if __name__ == "__main__":
    unittest.main()
