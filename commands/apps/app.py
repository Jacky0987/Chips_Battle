# -*- coding: utf-8 -*-
"""
App命令

应用管理和启动命令，提供应用的统一入口。
"""

from typing import List, Dict, Any
from commands.base import AppCommand, CommandResult, CommandContext
from services.app_service import AppService


class AppCommand(AppCommand):
    """应用命令 - 应用管理和启动的统一入口"""
    
    def __init__(self, app_service: AppService = None):
        super().__init__()
        self.app_service = app_service
    
    @property
    def name(self) -> str:
        return "app"
    
    @property
    def aliases(self) -> List[str]:
        return ["application", "apps"]
    
    @property
    def description(self) -> str:
        return "应用管理 - 启动应用、查看应用列表、访问应用市场"
    
    @property
    def usage(self) -> str:
        return "app <应用名.app> | app list | app market [子命令]"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行app命令
        
        Args:
            args: 命令参数列表
            context: 命令执行上下文
            
        Returns:
            命令执行结果
        """
        try:
            if not args:
                return self._show_app_help()
            
            first_arg = args[0].lower()
            
            # app list - 显示已拥有的应用
            if first_arg == "list":
                return await self._show_owned_apps(context)
            
            # app market - 访问应用市场
            elif first_arg == "market":
                return await self._handle_market_command(args[1:], context)
            
            # app upgrade - 升级计算机硬件解锁应用市场
            elif first_arg == "upgrade":
                return await self._upgrade_computer(context)
            
            # app <应用名.app> - 启动特定应用
            elif first_arg.endswith(".app"):
                app_name = first_arg[:-4]  # 移除.app后缀
                return await self._launch_app(app_name, args[1:], context)
            
            # 如果没有.app后缀，尝试作为应用名处理
            else:
                return await self._launch_app(first_arg, args[1:], context)
                
        except Exception as e:
            return self.error(f"应用命令执行失败: {str(e)}")
    
    def _show_app_help(self) -> CommandResult:
        """显示应用命令帮助"""
        help_text = """
📱 应用管理命令帮助:

🚀 启动应用:
  app <应用名.app>               - 启动指定应用
  app calc.app                   - 启动计算器应用
  app news.app                   - 启动新闻应用

📋 应用管理:
  app list                       - 查看已拥有的应用列表
  app list stats                 - 查看应用使用统计

🛒 应用市场:
  app market                     - 浏览应用市场主页
  app market app <应用名>        - 查看应用详情
  app market buy <应用名>        - 购买应用
  app market search <关键词>     - 搜索应用

⚙️ 系统升级:
  app upgrade                    - 升级计算机硬件解锁应用市场

💡 使用提示:
  - 应用名可以带.app后缀，也可以不带
  - 启动应用后会进入应用的专用环境
  - 使用 'exit' 或 'quit' 退出应用环境
"""
        return self.success(help_text)
    
    async def _show_owned_apps(self, context: CommandContext) -> CommandResult:
        """显示用户拥有的应用列表"""
        user_id = getattr(context.user, 'user_id', None) if hasattr(context, 'user') and context.user else None
        if not user_id:
            return self.error("请先登录")
        
        try:
            owned_app_names = await self.app_service.get_user_owned_apps(user_id)
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
                
                for app in owned_apps:
                    rating_stars = "⭐" * int(app.get('rating', 0))
                    output.append(f"│ {app['icon']} {app['display_name']:<25} {rating_stars:<10} │")
                    output.append(f"│   启动: app {app['name']}.app                               │")
                    output.append("├─────────────────────────────────────────────────────────────┤")
            
            if free_apps:
                output.append("│  🆓 免费应用                                                │")
                output.append("├─────────────────────────────────────────────────────────────┤")
                
                for app in free_apps:
                    rating_stars = "⭐" * int(app.get('rating', 0))
                    output.append(f"│ {app['icon']} {app['display_name']:<25} {rating_stars:<10} │")
                    output.append(f"│   启动: app {app['name']}.app                               │")
                    output.append("├─────────────────────────────────────────────────────────────┤")
            
            if not owned_apps and not free_apps:
                output.append("│  暂无可用应用                                                │")
                output.append("│  使用 'app market' 浏览应用市场                             │")
                output.append("├─────────────────────────────────────────────────────────────┤")
            
            output.append("│  💡 使用提示                                                │")
            output.append("│  • app <应用名>.app  - 启动应用                             │")
            output.append("│  • app market        - 浏览应用市场                         │")
            output.append("╰─────────────────────────────────────────────────────────────╯")
            
            return self.success("\n".join(output))
            
        except Exception as e:
            return self.error(f"获取应用列表失败: {str(e)}")
    
    async def _handle_market_command(self, args: List[str], context: CommandContext) -> CommandResult:
        """处理市场相关命令"""
        try:
            from services.app_service import AppService
            from dal.unit_of_work import UnitOfWork
            from core.event_bus import EventBus
            from services.currency_service import CurrencyService
            
            # 创建服务实例
            uow = UnitOfWork()
            event_bus = EventBus()
            currency_service = CurrencyService(uow)
            app_service = AppService(uow, event_bus, currency_service)
            
            user_id = getattr(context.user, 'user_id', None) if hasattr(context, 'user') and context.user else None
            if not user_id:
                return self.error("请先登录")
            
            # 检查是否有资格使用应用市场
            eligibility = await app_service.check_market_unlock_eligibility(user_id)
            
            if not eligibility['eligible']:
                return self.error(
                    f"🔒 应用市场尚未解锁\n\n"
                    f"💰 当前总资产: {eligibility['total_balance']:,.2f} JCC\n"
                    f"🎯 解锁要求: {eligibility['required_balance']:,.2f} JCC\n"
                    f"📈 还需要: {eligibility['remaining_needed']:,.2f} JCC\n\n"
                    f"💡 使用 'app upgrade' 升级您的计算机硬件以解锁应用市场。"
                )
            
            # 导入并调用MarketCommand
            from commands.apps.market import MarketCommand
            market_command = MarketCommand(app_service=app_service)
            return await market_command.execute(args, context)
            
        except ImportError:
            return self.error("应用市场功能暂时不可用")
        except Exception as e:
            return self.error(f"访问应用市场时发生错误: {str(e)}")
    
    async def _upgrade_computer(self, context: CommandContext) -> CommandResult:
        """升级计算机硬件以解锁应用市场"""
        try:
            from services.app_service import AppService
            from dal.unit_of_work import UnitOfWork
            from core.event_bus import EventBus
            from services.currency_service import CurrencyService
            
            # 创建服务实例
            uow = UnitOfWork()
            event_bus = EventBus()
            currency_service = CurrencyService(uow)
            app_service = AppService(uow, event_bus, currency_service)
            
            user_id = getattr(context.user, 'user_id', None) if hasattr(context, 'user') and context.user else None
            if not user_id:
                return self.error("请先登录")
            
            # 检查解锁资格
            eligibility = await app_service.check_market_unlock_eligibility(user_id)
            
            if not eligibility['eligible']:
                return self.error(
                    f"💻 计算机硬件升级失败\n\n"
                    f"❌ 资金不足，无法升级硬件解锁应用市场。\n"
                    f"💰 当前总资产: {eligibility['total_balance']:,.2f} JCC\n"
                    f"🎯 所需资产: {eligibility['required_balance']:,.2f} JCC\n"
                    f"📈 还需要: {eligibility['remaining_needed']:,.2f} JCC\n\n"
                    f"💡 提示: 继续交易和投资以增加您的资产！"
                )
            
            # 执行解锁
            result = await app_service.unlock_app_market(user_id)
            
            if result['success']:
                upgrade_text = (
                    "💻 计算机硬件升级\n\n"
                    "🔧 正在检查系统要求... ✅\n"
                    f"💰 检查资金状况... ✅ ({eligibility['total_balance']:,.2f} JCC)\n"
                    "⚡ 升级处理器和内存... ✅\n"
                    "🔓 解锁应用市场功能... ✅\n\n"
                    "🎉 升级完成！应用市场现已可用。\n\n"
                    "📱 现在您可以：\n"
                    "  • 使用 'app market' 浏览应用商店\n"
                    "  • 购买专业交易工具\n"
                    "  • 解锁高级功能\n\n"
                    "🚀 开始探索应用市场吧！"
                )
                return self.success(upgrade_text)
            else:
                return self.error(f"升级失败: {result['message']}")
                
        except Exception as e:
            return self.error(f"升级过程中发生错误: {str(e)}")
    
    async def _launch_app(self, app_name: str, args: List[str], context: CommandContext) -> CommandResult:
        """启动指定应用"""
        user_id = getattr(context.user, 'user_id', None) if hasattr(context, 'user') and context.user else None
        if not user_id:
            return self.error("请先登录")
        
        # 检查用户是否拥有该应用
        can_use = await self.app_service.can_use_app(user_id, app_name)
        if not can_use:
            return self.error(f"您没有应用 '{app_name}'，请先在应用市场购买")
        
        # 根据应用名称启动对应的应用
        try:
            if app_name == "calc" or app_name == "calculator":
                from commands.apps.calculator import CalculatorCommand
                app_command = CalculatorCommand()
                return await self._enter_app_environment(app_command, args, context)
            
            elif app_name == "news":
                from commands.apps.news import NewsCommand
                app_command = NewsCommand()
                return await self._enter_app_environment(app_command, args, context)
            
            elif app_name == "weather":
                from commands.apps.weather import WeatherCommand
                app_command = WeatherCommand()
                return await self._enter_app_environment(app_command, args, context)
            
            else:
                return self.error(f"应用 '{app_name}' 暂未实现")
                
        except Exception as e:
            return self.error(f"启动应用失败: {str(e)}")
    
    async def _enter_app_environment(self, app_command, args: List[str], context: CommandContext) -> CommandResult:
        """进入应用环境"""
        # 设置应用环境标识
        context.session_data['current_app'] = app_command.name
        context.session_data['app_prompt'] = f"({app_command.name}.app)@{getattr(context.user, 'username', 'user')}$> "
        
        # 如果有参数，直接执行应用命令
        if args:
            result = await app_command.execute(args, context)
            return result
        else:
            # 显示应用欢迎信息
            welcome_text = f"""
🚀 已启动 {app_command.description}

💡 使用提示:
  • 输入命令来使用应用功能
  • 输入 'help' 查看应用帮助
  • 输入 'exit' 或 'quit' 退出应用

当前环境: {app_command.name}.app
"""
            return CommandResult(
                success=True, 
                message=welcome_text,
                action="enter_app",
                data={"app_name": app_command.name, "prompt": context.session_data['app_prompt']}
            )