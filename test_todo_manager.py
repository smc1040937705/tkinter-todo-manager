#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
待办管理器测试文件
"""

import unittest
import os
import json
import tempfile
import shutil
from datetime import datetime, timedelta
from models.todo import Todo, TodoManager, CATEGORIES, PRIORITIES

class TestTodo(unittest.TestCase):
    """测试 Todo 类"""

    def test_todo_creation(self):
        """测试待办事项创建"""
        todo = Todo(
            title='测试待办',
            description='测试描述',
            category='工作',
            priority='高',
            due_date='2024-12-31T00:00:00'
        )
        self.assertEqual(todo.title, '测试待办')
        self.assertEqual(todo.description, '测试描述')
        self.assertEqual(todo.category, '工作')
        self.assertEqual(todo.priority, '高')
        self.assertEqual(todo.due_date, '2024-12-31T00:00:00')
        self.assertFalse(todo.completed)

    def test_todo_default_values(self):
        """测试待办事项默认值"""
        todo = Todo(title='测试待办')
        self.assertEqual(todo.description, '')
        self.assertEqual(todo.category, '生活')
        self.assertEqual(todo.priority, '中')
        self.assertIsNone(todo.due_date)
        self.assertFalse(todo.completed)

    def test_todo_invalid_category(self):
        """测试无效分类处理"""
        todo = Todo(title='测试待办', category='无效分类')
        self.assertEqual(todo.category, '生活')

    def test_todo_invalid_priority(self):
        """测试无效优先级处理"""
        todo = Todo(title='测试待办', priority='无效优先级')
        self.assertEqual(todo.priority, '中')

    def test_todo_to_dict(self):
        """测试转换为字典"""
        todo = Todo(title='测试待办', description='描述', category='学习', priority='低')
        todo_dict = todo.to_dict()
        self.assertEqual(todo_dict['title'], '测试待办')
        self.assertEqual(todo_dict['description'], '描述')
        self.assertEqual(todo_dict['category'], '学习')
        self.assertEqual(todo_dict['priority'], '低')

    def test_todo_from_dict(self):
        """测试从字典创建"""
        data = {
            'id': 1,
            'title': '字典待办',
            'description': '字典描述',
            'category': '工作',
            'priority': '高',
            'completed': True,
            'due_date': '2024-12-31T00:00:00',
            'created_at': '2024-01-01T00:00:00'
        }
        todo = Todo.from_dict(data)
        self.assertEqual(todo.id, 1)
        self.assertEqual(todo.title, '字典待办')
        self.assertEqual(todo.category, '工作')
        self.assertTrue(todo.completed)

    def test_is_overdue(self):
        """测试是否过期"""
        # 已过期
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        todo = Todo(title='过期待办', due_date=past_date)
        self.assertTrue(todo.is_overdue())

        # 未过期
        future_date = (datetime.now() + timedelta(days=1)).isoformat()
        todo2 = Todo(title='未过期待办', due_date=future_date)
        self.assertFalse(todo2.is_overdue())

        # 已完成的不算过期
        todo3 = Todo(title='已完成过期', due_date=past_date, completed=True)
        self.assertFalse(todo3.is_overdue())

    def test_days_until_due(self):
        """测试剩余天数计算"""
        # 今天
        today = datetime.now().isoformat()
        todo = Todo(title='今天到期', due_date=today)
        self.assertEqual(todo.days_until_due(), 0)

        # 明天
        tomorrow = (datetime.now() + timedelta(days=1)).isoformat()
        todo2 = Todo(title='明天到期', due_date=tomorrow)
        self.assertEqual(todo2.days_until_due(), 1)

        # 无截止日期
        todo3 = Todo(title='无截止日期')
        self.assertIsNone(todo3.days_until_due())

    def test_format_date(self):
        """测试日期格式化"""
        iso_date = '2024-12-31T10:30:00'
        formatted = Todo.format_date(iso_date)
        self.assertEqual(formatted, '2024-12-31')

class TestTodoManager(unittest.TestCase):
    """测试 TodoManager 类"""

    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.original_home = os.environ.get('HOME') or os.environ.get('USERPROFILE')
        os.environ['HOME'] = self.test_dir
        os.environ['USERPROFILE'] = self.test_dir

        self.data_dir = os.path.join(self.test_dir, '.todo_app')
        os.makedirs(self.data_dir, exist_ok=True)

        self.manager = TodoManager()
        self.manager._data_dir = self.data_dir
        self.manager._data_file = os.path.join(self.data_dir, 'data.json')
        self.manager.todos = []
        self.manager._next_id = 1

    def tearDown(self):
        """测试后清理"""
        if self.original_home:
            os.environ['HOME'] = self.original_home
            os.environ['USERPROFILE'] = self.original_home
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_add_todo(self):
        """测试添加待办"""
        todo = Todo(title='新待办')
        added_todo = self.manager.add_todo(todo)
        self.assertEqual(added_todo.id, 1)
        self.assertEqual(len(self.manager.todos), 1)
        self.assertEqual(self.manager.todos[0].title, '新待办')

    def test_get_todo(self):
        """测试获取待办"""
        todo = Todo(title='获取测试')
        added = self.manager.add_todo(todo)
        retrieved = self.manager.get_todo(added.id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.title, '获取测试')

        not_found = self.manager.get_todo(999)
        self.assertIsNone(not_found)

    def test_update_todo(self):
        """测试更新待办"""
        todo = Todo(title='原始标题', description='原始描述')
        added = self.manager.add_todo(todo)

        result = self.manager.update_todo(added.id, title='新标题', description='新描述')
        self.assertTrue(result)

        updated = self.manager.get_todo(added.id)
        self.assertEqual(updated.title, '新标题')
        self.assertEqual(updated.description, '新描述')

        result2 = self.manager.update_todo(999, title='无效')
        self.assertFalse(result2)

    def test_delete_todo(self):
        """测试删除待办"""
        todo = Todo(title='要删除的')
        added = self.manager.add_todo(todo)
        self.assertEqual(len(self.manager.todos), 1)

        result = self.manager.delete_todo(added.id)
        self.assertTrue(result)
        self.assertEqual(len(self.manager.todos), 0)

        result2 = self.manager.delete_todo(999)
        self.assertFalse(result2)

    def test_toggle_completed(self):
        """测试切换完成状态"""
        todo = Todo(title='切换测试')
        added = self.manager.add_todo(todo)
        self.assertFalse(added.completed)

        result = self.manager.toggle_completed(added.id)
        self.assertTrue(result)
        toggled = self.manager.get_todo(added.id)
        self.assertTrue(toggled.completed)

        result2 = self.manager.toggle_completed(added.id)
        self.assertTrue(result2)
        toggled2 = self.manager.get_todo(added.id)
        self.assertFalse(toggled2.completed)

    def test_filter_by_category(self):
        """测试按分类筛选"""
        self.manager.add_todo(Todo(title='工作1', category='工作'))
        self.manager.add_todo(Todo(title='学习1', category='学习'))
        self.manager.add_todo(Todo(title='生活1', category='生活'))
        self.manager.add_todo(Todo(title='生活2', category='生活'))

        work_todos = self.manager.filter_by_category('工作')
        self.assertEqual(len(work_todos), 1)
        self.assertEqual(work_todos[0].category, '工作')

        life_todos = self.manager.filter_by_category('生活')
        self.assertEqual(len(life_todos), 2)

        all_todos = self.manager.filter_by_category('全部')
        self.assertEqual(len(all_todos), 4)

    def test_filter_by_priority(self):
        """测试按优先级筛选"""
        self.manager.add_todo(Todo(title='高优1', priority='高'))
        self.manager.add_todo(Todo(title='中优1', priority='中'))
        self.manager.add_todo(Todo(title='中优2', priority='中'))
        self.manager.add_todo(Todo(title='低优1', priority='低'))

        high_todos = self.manager.filter_by_priority('高')
        self.assertEqual(len(high_todos), 1)

        medium_todos = self.manager.filter_by_priority('中')
        self.assertEqual(len(medium_todos), 2)

        all_todos = self.manager.filter_by_priority('全部')
        self.assertEqual(len(all_todos), 4)

    def test_filter_by_completed(self):
        """测试按完成状态筛选"""
        todo1 = self.manager.add_todo(Todo(title='已完成'))
        todo2 = self.manager.add_todo(Todo(title='未完成'))
        self.manager.toggle_completed(todo1.id)

        completed = self.manager.filter_by_completed(True)
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].title, '已完成')

        not_completed = self.manager.filter_by_completed(False)
        self.assertEqual(len(not_completed), 1)
        self.assertEqual(not_completed[0].title, '未完成')

        all_todos = self.manager.filter_by_completed(None)
        self.assertEqual(len(all_todos), 2)

    def test_search_todos(self):
        """测试搜索功能"""
        self.manager.add_todo(Todo(title='购买牛奶', description='早餐需要'))
        self.manager.add_todo(Todo(title='学习Python', description='编程学习'))
        self.manager.add_todo(Todo(title='项目报告', description='工作相关'))
        self.manager.add_todo(Todo(title='牛奶采购', description='超市购物'))

        # 搜索标题
        milk_todos = self.manager.search_todos('牛奶')
        self.assertEqual(len(milk_todos), 2)

        # 搜索描述
        work_todos = self.manager.search_todos('工作')
        self.assertEqual(len(work_todos), 1)

        # 不区分大小写
        python_todos = self.manager.search_todos('python')
        self.assertEqual(len(python_todos), 1)

        # 空搜索返回全部
        all_todos = self.manager.search_todos('')
        self.assertEqual(len(all_todos), 4)

        # 无匹配
        no_match = self.manager.search_todos('不存在的关键词')
        self.assertEqual(len(no_match), 0)

    def test_filter_todos_combined(self):
        """测试组合筛选"""
        self.manager.add_todo(Todo(title='工作高优', category='工作', priority='高'))
        self.manager.add_todo(Todo(title='工作中优', category='工作', priority='中'))
        self.manager.add_todo(Todo(title='学习高优', category='学习', priority='高'))
        self.manager.add_todo(Todo(title='生活低优', category='生活', priority='低'))

        # 组合筛选：工作分类 + 高优先级
        filtered = self.manager.filter_todos(category='工作', priority='高')
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].title, '工作高优')

    def test_sort_todos_by_due_date(self):
        """测试按截止日期排序"""
        today = datetime.now()
        todo1 = Todo(title='今天', due_date=today.isoformat())
        todo2 = Todo(title='明天', due_date=(today + timedelta(days=1)).isoformat())
        todo3 = Todo(title='无日期')

        self.manager.add_todo(todo3)
        self.manager.add_todo(todo2)
        self.manager.add_todo(todo1)

        sorted_todos = self.manager.sort_todos(self.manager.todos, sort_by='due_date')
        self.assertEqual(sorted_todos[0].title, '今天')
        self.assertEqual(sorted_todos[1].title, '明天')
        self.assertEqual(sorted_todos[2].title, '无日期')

    def test_sort_todos_by_priority(self):
        """测试按优先级排序"""
        todo1 = Todo(title='低', priority='低')
        todo2 = Todo(title='高', priority='高')
        todo3 = Todo(title='中', priority='中')

        self.manager.add_todo(todo1)
        self.manager.add_todo(todo2)
        self.manager.add_todo(todo3)

        sorted_todos = self.manager.sort_todos(self.manager.todos, sort_by='priority')
        self.assertEqual(sorted_todos[0].title, '高')
        self.assertEqual(sorted_todos[1].title, '中')
        self.assertEqual(sorted_todos[2].title, '低')

    def test_get_overdue_todos(self):
        """测试获取过期待办"""
        past = (datetime.now() - timedelta(days=1)).isoformat()
        future = (datetime.now() + timedelta(days=1)).isoformat()

        self.manager.add_todo(Todo(title='过期1', due_date=past))
        self.manager.add_todo(Todo(title='过期2', due_date=past))
        self.manager.add_todo(Todo(title='未过期', due_date=future))
        self.manager.add_todo(Todo(title='过期已完成', due_date=past, completed=True))

        overdue = self.manager.get_overdue_todos()
        self.assertEqual(len(overdue), 2)

    def test_get_due_soon_todos(self):
        """测试获取即将到期待办"""
        today = datetime.now().isoformat()
        tomorrow = (datetime.now() + timedelta(days=1)).isoformat()
        next_week = (datetime.now() + timedelta(days=7)).isoformat()

        self.manager.add_todo(Todo(title='今天', due_date=today))
        self.manager.add_todo(Todo(title='明天', due_date=tomorrow))
        self.manager.add_todo(Todo(title='下周', due_date=next_week))
        self.manager.add_todo(Todo(title='今天已完成', due_date=today, completed=True))

        due_soon = self.manager.get_due_soon_todos(days=3)
        self.assertEqual(len(due_soon), 2)

    def test_save_and_load(self):
        """测试数据保存和加载"""
        self.manager.add_todo(Todo(title='保存测试1', description='描述1', category='工作'))
        self.manager.add_todo(Todo(title='保存测试2', priority='高', completed=True))
        self.manager.save_to_file()

        new_manager = TodoManager()
        new_manager._data_dir = self.data_dir
        new_manager._data_file = os.path.join(self.data_dir, 'data.json')
        new_manager.load_from_file()

        self.assertEqual(len(new_manager.todos), 2)
        self.assertEqual(new_manager.todos[0].title, '保存测试1')
        self.assertEqual(new_manager.todos[1].priority, '高')
        self.assertTrue(new_manager.todos[1].completed)

    def test_validate_date(self):
        """测试日期验证"""
        self.assertTrue(Todo.validate_date('2024-12-31T00:00:00'))
        self.assertTrue(Todo.validate_date(''))
        self.assertFalse(Todo.validate_date('无效日期'))
        self.assertFalse(Todo.validate_date('2024/12/31'))

class TestConstants(unittest.TestCase):
    """测试常量定义"""

    def test_categories(self):
        """测试分类常量"""
        self.assertEqual(CATEGORIES, ['工作', '学习', '生活'])

    def test_priorities(self):
        """测试优先级常量"""
        self.assertEqual(PRIORITIES, ['高', '中', '低'])

if __name__ == '__main__':
    unittest.main(verbosity=2)