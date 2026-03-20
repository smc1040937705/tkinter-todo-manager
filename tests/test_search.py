"""
搜索匹配规则和日期校验排序测试
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from models.todo import TodoItem, TodoManager, Category, Priority


class TestSearch(unittest.TestCase):
    """测试搜索功能"""

    def setUp(self):
        """测试前准备"""
        self.manager = TodoManager()
        
        # 添加测试数据
        self.manager.add(TodoItem(
            title="完成项目报告",
            category=Category.WORK,
            priority=Priority.HIGH,
            description="需要提交给经理"
        ))
        
        self.manager.add(TodoItem(
            title="学习Python",
            category=Category.STUDY,
            priority=Priority.MEDIUM,
            description="完成在线课程"
        ))
        
        self.manager.add(TodoItem(
            title="购买生活用品",
            category=Category.LIFE,
            priority=Priority.LOW,
            description="去超市买牛奶和面包"
        ))
        
        self.manager.add(TodoItem(
            title="Python项目",
            category=Category.WORK,
            priority=Priority.HIGH,
            description="使用Python编写脚本"
        ))

    def test_search_by_title(self):
        """测试按标题搜索"""
        results = self.manager.search("Python")
        
        self.assertEqual(len(results), 2)
        titles = [r.title for r in results]
        self.assertIn("学习Python", titles)
        self.assertIn("Python项目", titles)

    def test_search_by_description(self):
        """测试按描述搜索"""
        results = self.manager.search("超市")
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "购买生活用品")

    def test_search_by_category(self):
        """测试按分类搜索"""
        results = self.manager.search("工作")
        
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r.category, Category.WORK)

    def test_search_case_insensitive(self):
        """测试搜索不区分大小写"""
        results_lower = self.manager.search("python")
        results_upper = self.manager.search("PYTHON")
        results_mixed = self.manager.search("Python")
        
        self.assertEqual(len(results_lower), 2)
        self.assertEqual(len(results_upper), 2)
        self.assertEqual(len(results_mixed), 2)

    def test_search_partial_match(self):
        """测试部分匹配"""
        results = self.manager.search("项目")
        
        self.assertEqual(len(results), 2)
        titles = [r.title for r in results]
        self.assertIn("完成项目报告", titles)
        self.assertIn("Python项目", titles)

    def test_search_empty_keyword(self):
        """测试空关键词搜索"""
        results = self.manager.search("")
        
        # 空关键词应该匹配所有
        self.assertEqual(len(results), 4)

    def test_search_no_match(self):
        """测试无匹配结果"""
        results = self.manager.search("不存在的待办")
        
        self.assertEqual(len(results), 0)

    def test_search_special_characters(self):
        """测试特殊字符搜索"""
        self.manager.add(TodoItem(title="测试-特殊_字符.待办"))
        
        results = self.manager.search("特殊")
        self.assertEqual(len(results), 1)


class TestDateValidation(unittest.TestCase):
    """测试日期校验"""

    def test_valid_date_format(self):
        """测试有效日期格式"""
        todo = TodoItem(title="测试", due_date="2025-12-31")
        self.assertEqual(todo.due_date, "2025-12-31")

    def test_date_parsing(self):
        """测试日期解析"""
        todo = TodoItem(title="测试", due_date="2025-03-15")
        
        # 验证日期格式正确
        parsed = datetime.strptime(todo.due_date, "%Y-%m-%d")
        self.assertEqual(parsed.year, 2025)
        self.assertEqual(parsed.month, 3)
        self.assertEqual(parsed.day, 15)

    def test_overdue_calculation(self):
        """测试逾期计算"""
        # 昨天
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        todo_yesterday = TodoItem(title="昨天", due_date=yesterday)
        self.assertTrue(todo_yesterday.is_overdue())
        
        # 今天
        today = datetime.now().strftime("%Y-%m-%d")
        todo_today = TodoItem(title="今天", due_date=today)
        self.assertFalse(todo_today.is_overdue())
        self.assertTrue(todo_today.is_due_today())
        
        # 明天
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        todo_tomorrow = TodoItem(title="明天", due_date=tomorrow)
        self.assertFalse(todo_tomorrow.is_overdue())
        self.assertFalse(todo_tomorrow.is_due_today())

    def test_invalid_date_not_overdue(self):
        """测试无效日期不会导致逾期"""
        todo = TodoItem(title="测试", due_date="invalid-date")
        self.assertFalse(todo.is_overdue())
        self.assertFalse(todo.is_due_today())

    def test_no_date_not_overdue(self):
        """测试无日期不会导致逾期"""
        todo = TodoItem(title="测试")
        self.assertIsNone(todo.due_date)
        self.assertFalse(todo.is_overdue())
        self.assertFalse(todo.is_due_today())


class TestSorting(unittest.TestCase):
    """测试排序功能"""

    def setUp(self):
        """测试前准备"""
        self.manager = TodoManager()

    def test_sort_by_date(self):
        """测试按日期排序"""
        self.manager.add(TodoItem(title="明天", due_date="2025-12-25"))
        self.manager.add(TodoItem(title="昨天", due_date="2025-12-23"))
        self.manager.add(TodoItem(title="今天", due_date="2025-12-24"))
        self.manager.add(TodoItem(title="无日期"))
        
        sorted_todos = self.manager.sort_by_date()
        
        self.assertEqual(sorted_todos[0].title, "昨天")
        self.assertEqual(sorted_todos[1].title, "今天")
        self.assertEqual(sorted_todos[2].title, "明天")
        # 无日期的应该在最后
        self.assertEqual(sorted_todos[3].title, "无日期")

    def test_sort_by_date_reverse(self):
        """测试按日期倒序排序"""
        self.manager.add(TodoItem(title="明天", due_date="2025-12-25"))
        self.manager.add(TodoItem(title="昨天", due_date="2025-12-23"))
        self.manager.add(TodoItem(title="今天", due_date="2025-12-24"))
        
        sorted_todos = self.manager.sort_by_date(reverse=True)
        
        self.assertEqual(sorted_todos[0].title, "明天")
        self.assertEqual(sorted_todos[1].title, "今天")
        self.assertEqual(sorted_todos[2].title, "昨天")

    def test_sort_by_priority(self):
        """测试按优先级排序"""
        self.manager.add(TodoItem(title="低", priority=Priority.LOW))
        self.manager.add(TodoItem(title="高", priority=Priority.HIGH))
        self.manager.add(TodoItem(title="中", priority=Priority.MEDIUM))
        
        sorted_todos = self.manager.sort_by_priority()
        
        self.assertEqual(sorted_todos[0].title, "高")
        self.assertEqual(sorted_todos[1].title, "中")
        self.assertEqual(sorted_todos[2].title, "低")

    def test_sort_by_priority_reverse(self):
        """测试按优先级倒序排序"""
        self.manager.add(TodoItem(title="低", priority=Priority.LOW))
        self.manager.add(TodoItem(title="高", priority=Priority.HIGH))
        self.manager.add(TodoItem(title="中", priority=Priority.MEDIUM))
        
        sorted_todos = self.manager.sort_by_priority(reverse=False)
        
        self.assertEqual(sorted_todos[0].title, "低")
        self.assertEqual(sorted_todos[1].title, "中")
        self.assertEqual(sorted_todos[2].title, "高")


class TestCategoryFilter(unittest.TestCase):
    """测试分类筛选逻辑"""

    def setUp(self):
        """测试前准备"""
        self.manager = TodoManager()
        
        self.manager.add(TodoItem(title="工作1", category=Category.WORK))
        self.manager.add(TodoItem(title="工作2", category=Category.WORK))
        self.manager.add(TodoItem(title="学习1", category=Category.STUDY))
        self.manager.add(TodoItem(title="生活1", category=Category.LIFE))

    def test_filter_by_work(self):
        """测试工作分类筛选"""
        results = self.manager.get_by_category(Category.WORK)
        
        self.assertEqual(len(results), 2)
        for r in results:
            self.assertEqual(r.category, Category.WORK)

    def test_filter_by_study(self):
        """测试学习分类筛选"""
        results = self.manager.get_by_category(Category.STUDY)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "学习1")

    def test_filter_by_life(self):
        """测试生活分类筛选"""
        results = self.manager.get_by_category(Category.LIFE)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "生活1")

    def test_filter_by_string_category(self):
        """测试使用字符串分类筛选"""
        results = self.manager.get_by_category("工作")
        
        self.assertEqual(len(results), 2)

    def test_filter_empty_result(self):
        """测试筛选结果为空"""
        # 添加一个新的管理器，没有生活分类
        empty_manager = TodoManager()
        empty_manager.add(TodoItem(title="工作", category=Category.WORK))
        
        results = empty_manager.get_by_category(Category.LIFE)
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
