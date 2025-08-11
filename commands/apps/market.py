from commands.base import AppCommand, CommandResult
from services.app_service import AppService
from typing import Dict, Any

class MarketCommand(AppCommand):
    """应用市场命令 - 显示Mac OS风格的应用市场界面"""
    
    def __init__(self, app_service: AppService):
        super().__init__()
        self.app_service = app_service
    
    @property
    def name(self) -> str:
        return "market"
    
    @property
    def description(self) -> str:
        return "应用市场命令 - 浏览和购买应用"
    
    async def execute(self, args: list, context: Dict[str, Any]) -> CommandResult:
        try:
            if not args:
                message = await self._show_market_home(context)
                return CommandResult(success=True, message=message)
            
            subcommand = args[0].lower()
            
            if subcommand == 'app':
                if len(args) < 2:
                    return CommandResult(success=False, message="用法: market app <应用名称>")
                app_name = args[1]
                message = await self._show_app_detail(app_name, context)
                return CommandResult(success=True, message=message)
            elif subcommand == 'category':
                if len(args) < 2:
                    message = self._show_categories()
                    return CommandResult(success=True, message=message)
                category = args[1]
                message = self._show_category_apps(category)
                return CommandResult(success=True, message=message)
            elif subcommand == 'search':
                if len(args) < 2:
                    return CommandResult(success=False, message="用法: market search <关键词>")
                keyword = ' '.join(args[1:])
                message = self._search_apps(keyword)
                return CommandResult(success=True, message=message)
            elif subcommand == 'buy':
                if len(args) < 2:
                    return CommandResult(success=False, message="用法: market buy <应用名称>")
                app_name = args[1]
                message = await self._buy_app(app_name, context)
                return CommandResult(success=True, message=message)
            else:
                return CommandResult(success=False, message="未知的子命令。可用命令: app, category, search, buy")
        except Exception as e:
            return CommandResult(success=False, message=f"命令执行出错: {str(e)}")
    
    async def _show_market_home(self, context: Dict[str, Any]) -> str:
        """显示应用市场主页"""
        apps = self.app_service.get_available_apps()
        user_id = getattr(context.user, 'user_id', None) if hasattr(context, 'user') and context.user else None
        owned_apps = await self.app_service.get_user_owned_apps(user_id) if user_id else []
        
        # Mac OS风格的界面
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                    🍎 JC App Store                         │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│  🌟 精选应用                                                │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        # 显示精选应用
        featured_apps = [app for app in apps if app['name'] in ['stock_tracker', 'news', 'calculator']]
        for app in featured_apps[:3]:
            price_str = "免费" if app['price'] == 0 else f"{app['price']} JCC"
            owned_str = " ✅" if app['name'] in owned_apps else ""
            rating_stars = "⭐" * int(app.get('rating', 0))
            
            output.append(f"│ {app['icon']} {app['display_name']:<20} {price_str:>10} {rating_stars} {owned_str}│")
            output.append(f"│   {app['description'][:50]:<50}   │")
            output.append("├─────────────────────────────────────────────────────────────┤")
        
        output.append("│  📱 分类浏览                                                │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        # 显示分类
        categories = {}
        for app in apps:
            category = app['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(app)
        
        for category, category_apps in categories.items():
            count = len(category_apps)
            output.append(f"│ 📂 {category:<15} ({count} 个应用)                        │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│  💡 使用提示                                                │")
        output.append("│  • market app <名称>     - 查看应用详情                     │")
        output.append("│  • market category <分类> - 浏览分类应用                    │")
        output.append("│  • market buy <名称>     - 购买应用                         │")
        output.append("│  • market search <关键词> - 搜索应用                        │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    async def _show_app_detail(self, app_name: str, context: Dict[str, Any]) -> str:
        """显示应用详情"""
        app = self.app_service.get_app_by_name(app_name)
        if not app:
            return f"❌ 应用 '{app_name}' 不存在"
        
        user_id = getattr(context.user, 'user_id', None) if hasattr(context, 'user') and context.user else None
        owned_apps = await self.app_service.get_user_owned_apps(user_id) if user_id else []
        is_owned = app_name in owned_apps
        
        price_str = "免费" if app['price'] == 0 else f"{app['price']} JCC"
        rating_stars = "⭐" * int(app.get('rating', 0))
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append(f"│ {app['icon']} {app['display_name']:<25} v{app['version']:<10}        │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append(f"│ 💰 价格: {price_str:<20} 📊 评分: {rating_stars}           │")
        output.append(f"│ 👨‍💻 开发者: {app['developer']:<15} 📁 大小: {app['file_size']:<10}    │")
        output.append(f"│ 📂 分类: {app['category']:<15} 📥 下载: {app['downloads']:,} 次     │")
        
        if is_owned:
            output.append("│ ✅ 已拥有                                                   │")
        else:
            output.append("│ 🛒 未购买                                                   │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 📝 应用描述                                                 │")
        
        # 分行显示描述
        description_lines = [app['description'][i:i+55] for i in range(0, len(app['description']), 55)]
        for line in description_lines:
            output.append(f"│ {line:<59} │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ ✨ 主要功能                                                 │")
        
        for feature in app.get('features', []):
            output.append(f"│ • {feature:<57} │")
        
        if app.get('requirements'):
            output.append("├─────────────────────────────────────────────────────────────┤")
            output.append("│ ⚠️  系统要求                                                │")
            for req in app['requirements']:
                output.append(f"│ • {req:<57} │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        if not is_owned and app['price'] > 0:
            output.append(f"│ 💡 使用 'market buy {app_name}' 购买此应用                   │")
        elif not is_owned and app['price'] == 0:
            output.append(f"│ 💡 使用 'app {app_name}' 直接运行此免费应用                   │")
        else:
            output.append(f"│ 💡 使用 'app {app_name}' 运行此应用                          │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _show_categories(self) -> str:
        """显示所有分类"""
        apps = self.app_service.get_available_apps()
        categories = {}
        
        for app in apps:
            category = app['category']
            if category not in categories:
                categories[category] = []
            categories[category].append(app)
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append("│                      📂 应用分类                            │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        for category, category_apps in categories.items():
            count = len(category_apps)
            free_count = len([app for app in category_apps if app['price'] == 0])
            paid_count = count - free_count
            
            output.append(f"│ 📁 {category:<15} 总计: {count:>2} (免费: {free_count}, 付费: {paid_count})     │")
        
        output.append("├─────────────────────────────────────────────────────────────┤")
        output.append("│ 💡 使用 'market category <分类名>' 查看分类下的应用          │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _show_category_apps(self, category: str) -> str:
        """显示指定分类的应用"""
        apps = self.app_service.get_available_apps()
        category_apps = [app for app in apps if app['category'] == category]
        
        if not category_apps:
            return f"❌ 分类 '{category}' 不存在或没有应用"
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append(f"│                   📂 {category} 分类应用                     │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        for app in category_apps:
            price_str = "免费" if app['price'] == 0 else f"{app['price']} JCC"
            rating_stars = "⭐" * int(app.get('rating', 0))
            
            output.append(f"│ {app['icon']} {app['display_name']:<20} {price_str:>10} {rating_stars}    │")
            output.append(f"│   {app['description'][:50]:<50}   │")
            output.append("├─────────────────────────────────────────────────────────────┤")
        
        output.append("│ 💡 使用 'market app <应用名>' 查看详情                      │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    def _search_apps(self, keyword: str) -> str:
        """搜索应用"""
        apps = self.app_service.get_available_apps()
        keyword_lower = keyword.lower()
        
        matching_apps = []
        for app in apps:
            if (keyword_lower in app['name'].lower() or 
                keyword_lower in app['display_name'].lower() or 
                keyword_lower in app['description'].lower() or
                keyword_lower in app['category'].lower()):
                matching_apps.append(app)
        
        if not matching_apps:
            return f"❌ 没有找到包含 '{keyword}' 的应用"
        
        output = []
        output.append("╭─────────────────────────────────────────────────────────────╮")
        output.append(f"│                🔍 搜索结果: '{keyword}'                      │")
        output.append("├─────────────────────────────────────────────────────────────┤")
        
        for app in matching_apps:
            price_str = "免费" if app['price'] == 0 else f"{app['price']} JCC"
            rating_stars = "⭐" * int(app.get('rating', 0))
            
            output.append(f"│ {app['icon']} {app['display_name']:<20} {price_str:>10} {rating_stars}    │")
            output.append(f"│   {app['description'][:50]:<50}   │")
            output.append("├─────────────────────────────────────────────────────────────┤")
        
        output.append(f"│ 找到 {len(matching_apps)} 个相关应用                                    │")
        output.append("╰─────────────────────────────────────────────────────────────╯")
        
        return "\n".join(output)
    
    async def _buy_app(self, app_name: str, context: Dict[str, Any]) -> str:
        """购买应用"""
        user_id = getattr(context.user, 'user_id', None) if hasattr(context, 'user') and context.user else None
        if not user_id:
            return "❌ 请先登录"
        
        result = await self.app_service.purchase_app(user_id, app_name)
        
        if result['success']:
            return f"✅ {result['message']}"
        else:
            return f"❌ {result['message']}"
    
    def get_help(self) -> str:
        return """
应用市场命令 - 浏览和购买应用

用法:
  market                    - 显示应用市场主页
  market app <应用名>       - 查看应用详情
  market category [分类]    - 浏览分类应用
  market search <关键词>    - 搜索应用
  market buy <应用名>       - 购买应用

示例:
  market
  market app calculator
  market category 工具
  market search 天气
  market buy weather
"""