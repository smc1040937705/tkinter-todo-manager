"""
JSON数据读写测试
"""
import unittest
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.storage import Storage


class TestStorage(unittest.TestCase):
    """测试存储模块"""

    def setUp(self):
        """测试前准备临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = Storage(data_dir=self.temp_dir, filename="test_data.json")

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load(self):
        """测试保存和加载数据"""
        data = [
            {"id": "1", "title": "测试1", "completed": False},
            {"id": "2", "title": "测试2", "completed": True}
        ]
        
        # 保存
        result = self.storage.save(data)
        self.assertTrue(result)
        
        # 加载
        loaded = self.storage.load()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]["title"], "测试1")
        self.assertEqual(loaded[1]["title"], "测试2")

    def test_save_empty_list(self):
        """测试保存空列表"""
        result = self.storage.save([])
        self.assertTrue(result)
        
        loaded = self.storage.load()
        self.assertEqual(loaded, [])

    def test_load_nonexistent_file(self):
        """测试加载不存在的文件"""
        loaded = self.storage.load()
        self.assertEqual(loaded, [])

    def test_load_empty_file(self):
        """测试加载空文件"""
        # 创建空文件
        with open(self.storage.filepath, 'w', encoding='utf-8') as f:
            f.write("")
        
        loaded = self.storage.load()
        self.assertEqual(loaded, [])

    def test_load_whitespace_file(self):
        """测试加载只有空白字符的文件"""
        with open(self.storage.filepath, 'w', encoding='utf-8') as f:
            f.write("   \n\t  ")
        
        loaded = self.storage.load()
        self.assertEqual(loaded, [])

    def test_exists(self):
        """测试文件存在检查"""
        self.assertFalse(self.storage.exists())
        
        self.storage.save([{"test": "data"}])
        self.assertTrue(self.storage.exists())

    def test_clear(self):
        """测试清空数据"""
        self.storage.save([{"test": "data"}])
        self.assertTrue(self.storage.exists())
        
        result = self.storage.clear()
        self.assertTrue(result)
        self.assertFalse(self.storage.exists())

    def test_get_file_size(self):
        """测试获取文件大小"""
        self.assertEqual(self.storage.get_file_size(), 0)
        
        self.storage.save([{"test": "data"}])
        size = self.storage.get_file_size()
        self.assertGreater(size, 0)

    def test_get_last_modified(self):
        """测试获取最后修改时间"""
        self.assertIsNone(self.storage.get_last_modified())
        
        self.storage.save([{"test": "data"}])
        mtime = self.storage.get_last_modified()
        self.assertIsNotNone(mtime)

    def test_backup(self):
        """测试备份功能"""
        self.storage.save([{"test": "data"}])
        
        result = self.storage.backup()
        self.assertTrue(result)
        
        # 检查备份文件是否存在
        backup_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.bak')]
        self.assertEqual(len(backup_files), 1)

    def test_backup_nonexistent(self):
        """测试备份不存在的文件"""
        result = self.storage.backup()
        self.assertFalse(result)

    def test_unicode_data(self):
        """测试Unicode数据保存"""
        data = [
            {"title": "中文测试", "description": "包含中文、日本語、한국어"},
            {"title": "Emoji测试 🎉", "description": "Hello 👋 World 🌍"}
        ]
        
        self.storage.save(data)
        loaded = self.storage.load()
        
        self.assertEqual(loaded[0]["title"], "中文测试")
        self.assertEqual(loaded[1]["title"], "Emoji测试 🎉")

    def test_nested_data(self):
        """测试嵌套数据结构"""
        data = {
            "users": [
                {"name": "张三", "todos": [{"title": "任务1"}, {"title": "任务2"}]},
                {"name": "李四", "todos": [{"title": "任务3"}]}
            ],
            "settings": {"theme": "dark", "notifications": True}
        }
        
        self.storage.save(data)
        loaded = self.storage.load()
        
        self.assertEqual(len(loaded["users"]), 2)
        self.assertEqual(loaded["settings"]["theme"], "dark")

    def test_default_path(self):
        """测试默认路径"""
        storage = Storage()
        home_dir = os.path.expanduser("~")
        expected_dir = os.path.join(home_dir, ".todo_app")
        expected_path = os.path.join(expected_dir, "data.json")
        
        self.assertEqual(storage.data_dir, expected_dir)
        self.assertEqual(storage.filepath, expected_path)


class TestStorageErrorHandling(unittest.TestCase):
    """测试存储错误处理"""

    def test_load_corrupted_json(self):
        """测试加载损坏的JSON"""
        temp_dir = tempfile.mkdtemp()
        try:
            storage = Storage(data_dir=temp_dir, filename="corrupted.json")
            
            # 写入损坏的JSON
            with open(storage.filepath, 'w', encoding='utf-8') as f:
                f.write("{invalid json content")
            
            # 应该返回空列表而不是抛出异常
            loaded = storage.load()
            self.assertEqual(loaded, [])
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
