"""
数据持久化模块
"""
import json
import os
from datetime import datetime


class Storage:
    """JSON文件存储管理器"""

    def __init__(self, data_dir=None, filename="data.json"):
        if data_dir is None:
            # 默认存储路径：用户目录下的 .todo_app/
            home_dir = os.path.expanduser("~")
            data_dir = os.path.join(home_dir, ".todo_app")
        
        self.data_dir = data_dir
        self.filepath = os.path.join(data_dir, filename)
        self._ensure_directory()

    def _ensure_directory(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)

    def save(self, data):
        """保存数据到JSON文件"""
        try:
            self._ensure_directory()
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except (IOError, OSError, json.JSONEncodeError) as e:
            print(f"保存数据失败: {e}")
            return False

    def load(self):
        """从JSON文件加载数据"""
        if not os.path.exists(self.filepath):
            return []
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return []
                return json.loads(content)
        except (IOError, OSError, json.JSONDecodeError) as e:
            print(f"加载数据失败: {e}")
            return []

    def backup(self):
        """创建备份文件"""
        if not os.path.exists(self.filepath):
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.filepath}.{timestamp}.bak"
            
            with open(self.filepath, 'r', encoding='utf-8') as src:
                content = src.read()
            with open(backup_path, 'w', encoding='utf-8') as dst:
                dst.write(content)
            return True
        except (IOError, OSError) as e:
            print(f"创建备份失败: {e}")
            return False

    def clear(self):
        """清空数据文件"""
        try:
            if os.path.exists(self.filepath):
                os.remove(self.filepath)
            return True
        except (IOError, OSError) as e:
            print(f"清空数据失败: {e}")
            return False

    def exists(self):
        """检查数据文件是否存在"""
        return os.path.exists(self.filepath)

    def get_file_size(self):
        """获取文件大小（字节）"""
        if os.path.exists(self.filepath):
            return os.path.getsize(self.filepath)
        return 0

    def get_last_modified(self):
        """获取最后修改时间"""
        if os.path.exists(self.filepath):
            mtime = os.path.getmtime(self.filepath)
            return datetime.fromtimestamp(mtime).isoformat()
        return None
