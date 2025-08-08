from commands.base import Command
from services.app_service import AppService
from typing import Dict, Any

class AppListCommand(Command):
    """应用列表命令 - 显示用户拥有的应用"""
    
    def __init__(self, app_service: AppService):
        super().__init__()
        self.app_service = app_service
    
    def execute(self, args: list, context: Dict[str, Any]) -> str:
        user_id = getattr(context.user, 'user_id', None) if hasattr(context, 'user') and context.user else None
        if not user_id:
            return "❌ 请先登录"
        
        if args and args[0].lower() == 'stats':
            return self._show_app_stats(user_id)
        
        return self._show_owned_apps(user_id)
    
    def _show_owned_apps(self, user_id: int) -> str:
        """显示用户拥有的应用列表"""
        owned_app_names = self.app_service.get_user_owned_apps(user_id)
        available_apps = self.app_service.get_available_apps()
        
        # 获取拥有的应用详情
        owned_apps = []
        free_apps = []
        
        for app in available_apps:
            if app['name'] in owned_app_names:
                owned_apps.append(app)
            elif app['price'] == 0:
                free_apps.append(app)
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    📱 我的应用                              │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        if owned_apps:
            output.append("│  💰 已购买应用                                              │")
            output.append("├─────────────────────────────────────────────────────────────┤")
            
            total_spent = 0
            for app in owned_apps:
                price = app['price']
                total_spent += price
                rating_stars = "⭐" * int(app.get('rating', 0))
                
                output.append(f"│ {app['icon']} {app['display_name']:<25} {price:>6.2f} JCC {rating_stars} │")
                output.append(f"│   {app['description'][:50]:<50}   │")
                output.append("├─────────────────────────────────────────────────────────────┤")
            
            output.append(f"│ 💸 总花费: {total_spent:.2f} JCC                                    │")
            output.append("├─────────────────────────────────────────────────────────────┤")
        
        if free_apps:
            output.append("│  🆓 免费应用 (可直接使用)                                    │")
            output.append("├─────────────────────────────────────────────────────────────┤")
            
            for app in free_apps[:5]:  # 只显示前5个免费应用
                rating_stars = "⭐" * int(app.get('rating', 0))
                output.append(f"│ {app['icon']} {app['display_name']:<25} 免费    {rating_stars}     │")
                output.append(f"│   {app['description'][:50]:<50}   │")
                output.append("├─────────────────────────────────────────────────────────────┤")
            
            if len(free_apps) > 5:
                output.append(f"│ ... 还有 {len(free_apps) - 5} 个免费应用                              │")
                output.append("├─────────────────────────────────────────────────────────────┤")
        
        output.append("│  💡 使用提示                                                │")
        output.append("│  • app <应用名>      - 运行应用                             │")
        output.append("│  • app list stats    - 查看应用统计                        │")
        output.append("│  • market            - 浏览应用市场                        │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _show_app_stats(self, user_id: int) -> str:
        """显示应用使用统计"""
        stats = self.app_service.get_app_usage_stats(user_id)
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    📊 应用统计                              │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append(f"│ 📱 应用市场总应用数: {stats['total_apps']:>3}                          │")
        output.append(f"│ ✅ 已拥有应用数:     {stats['owned_apps']:>3}                          │")
        output.append(f"│ 🆓 免费应用数:       {stats['free_apps']:>3}                          │")
        
        if stats['total_apps'] > 0:
            owned_percentage = (stats['owned_apps'] / stats['total_apps']) * 100
            free_percentage = (stats['free_apps'] / stats['total_apps']) * 100
            
            output.append("├─────────────────────────────────────────────────────────────┤")
            output.append(f"│ 📈 拥有率:           {owned_percentage:>5.1f}%                        │")
            output.append(f"│ 🆓 免费应用占比:     {free_percentage:>5.1f}%                        │")
        
        if stats['owned_app_names']:
            output.append("├─────────────────────────────────────────────────────────────┤")
            output.append("│ 🏆 已拥有的应用:                                            │")
            
            for i, app_name in enumerate(stats['owned_app_names'], 1):
                output.append(f"│ {i:>2}. {app_name:<54} │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 使用 'market' 浏览更多应用                               │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def get_help(self) -> str:
        return """
应用列表命令 - 查看拥有的应用

用法:
  app list        - 显示拥有的应用列表
  app list stats  - 显示应用使用统计

示例:
  app list
  app list stats
"""