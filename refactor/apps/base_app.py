"""
应用基类 - 所有应用的基础类
"""

from abc import ABC, abstractmethod
from datetime import datetime


class BaseApp(ABC):
    """应用基类"""
    
    def __init__(self, app_id, name, description, price, category, version="1.0", emoji="📱"):
        self.app_id = app_id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.version = version
        self.emoji = emoji
        self.install_date = None
        self.usage_count = 0
        self.last_used = None
    
    @abstractmethod
    def run(self, main_app, *args):
        """运行应用 - 子类必须实现"""
        pass
    
    def get_info(self):
        """获取应用信息"""
        return {
            'id': self.app_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category': self.category,
            'version': self.version,
            'emoji': self.emoji,
            'install_date': self.install_date,
            'usage_count': self.usage_count,
            'last_used': self.last_used
        }
    
    def update_usage(self):
        """更新使用统计"""
        self.usage_count += 1
        self.last_used = datetime.now().isoformat()
    
    def show_help(self):
        """显示应用帮助信息 - 子类可覆盖"""
        return f"""
{self.emoji} {self.name} - 帮助信息

📖 应用介绍:
{self.description}

🔧 版本信息:
  版本: {self.version}
  类别: {self.category}
  使用次数: {self.usage_count}

💡 使用方法:
  appmarket.app {self.app_id} [参数...]

⚠️ 注意: 请查看具体应用的使用说明
""" 