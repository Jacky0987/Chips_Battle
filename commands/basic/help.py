# -*- coding: utf-8 -*-
"""
帮助命令

提供系统帮助信息和命令使用说明。
"""

from typing import List
from commands.base import BasicCommand, CommandResult, CommandContext
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text


class HelpCommand(BasicCommand):
    """帮助命令"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
    
    @property
    def name(self) -> str:
        return "help"
    
    @property
    def aliases(self) -> List[str]:
        return ["h", "?", "man"]
    
    @property
    def description(self) -> str:
        return "显示帮助信息和命令使用说明"
    
    @property
    def usage(self) -> str:
        return "help [命令名称|分类]"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行帮助命令
        
        Args:
            args: 命令参数
            context: 命令上下文
            
        Returns:
            命令执行结果
        """
        try:
            # 如果没有参数，显示总体帮助
            if not args:
                return await self._show_general_help(context)
            
            # 如果有参数，显示特定命令或分类的帮助
            target = args[0].lower()
            return await self._show_specific_help(target, context)
            
        except Exception as e:
            return self.error(f"显示帮助时发生错误: {str(e)}")
    
    async def _show_general_help(self, context: CommandContext) -> CommandResult:
        """显示总体帮助信息
        
        Args:
            context: 命令上下文
            
        Returns:
            命令执行结果
        """
        # 创建帮助信息文本
        help_text = "\n🎮 游戏帮助\n\n"
        help_text += "欢迎来到 Chips Battle Remake v3.0 Alpha!\n\n"
        help_text += "这是一个命令驱动的游戏世界，你可以通过输入命令来与游戏互动。\n"
        help_text += "输入命令名称来执行操作，使用 'help <命令>' 查看特定命令的详细说明。\n\n"
        
        # 动态获取命令分类信息
        if context.registry:
            help_text += "📋 可用命令:\n\n"
            
            # 获取所有分类
            categories = context.registry.get_categories()
            category_icons = {
                'basic': '🔧',
                'finance': '💰', 
                'stock': '📈',
                'apps': '📱',
                'news': '📰',
                'admin': '⚙️'
            }
            
            for category in sorted(categories):
                icon = category_icons.get(category, '📋')
                commands = context.registry.get_command_names(category)
                if commands:
                    help_text += f"{icon} {category.title()}命令: {', '.join(sorted(commands))}\n"
            
            help_text += "\n"
        else:
            # 备用的硬编码分类信息
            help_text += "📋 命令分类:\n\n"
            help_text += "🔧 基础命令: help, status, profile, quit\n"
            help_text += "💰 财务命令: wallet, transfer, exchange\n"
            help_text += "📈 股票命令: stock, portfolio, trade\n"
            help_text += "📱 应用命令: app, install, launch\n"
            help_text += "📰 新闻命令: news, subscribe\n"
            help_text += "⚙️  管理命令: admin, config, logs\n\n"
        
        # 添加使用提示
        help_text += "💡 使用技巧:\n"
        help_text += "• 命令不区分大小写\n"
        help_text += "• 可以使用命令别名（如 'h' 代替 'help'）\n"
        help_text += "• 输入 'quit' 或 'exit' 退出游戏\n"
        help_text += "• 输入 'status' 查看当前状态\n"
        
        return self.success(help_text)
    
    async def _show_specific_help(self, target: str, context: CommandContext) -> CommandResult:
        """显示特定命令或分类的帮助
        
        Args:
            target: 目标命令或分类
            context: 命令上下文
            
        Returns:
            命令执行结果
        """
        if not context.registry:
            return self.error("命令注册器不可用")
        
        # 首先检查是否为具体命令
        command = context.registry.get_command(target)
        if command:
            help_content = f"\n📖 {command.name.upper()} 命令帮助\n\n"
            help_content += f"📝 描述: {command.description}\n"
            help_content += f"🔧 用法: {command.usage}\n"
            if command.aliases:
                help_content += f"🏷️  别名: {', '.join(command.aliases)}\n"
            help_content += f"📂 分类: {command.category}\n"
            return self.success(help_content)
        
        # 检查是否为分类
        categories = context.registry.get_categories()
        if target in categories:
            category_icons = {
                'basic': '🔧',
                'finance': '💰', 
                'stock': '📈',
                'apps': '📱',
                'news': '📰',
                'admin': '⚙️'
            }
            
            icon = category_icons.get(target, '📋')
            help_content = f"\n{icon} {target.upper()} 分类帮助\n\n"
            
            commands = context.registry.list_commands(target)
            if commands:
                help_content += f"{icon} {target.title()}命令详细说明\n\n"
                for command in sorted(commands, key=lambda c: c.name):
                    help_content += f"• {command.name} - {command.description}\n"
                    if command.aliases:
                        help_content += f"  别名: {', '.join(command.aliases)}\n"
            else:
                help_content += f"该分类下暂无可用命令\n"
            
            return self.success(help_content)
        
        # 未找到目标
        available_categories = ', '.join(sorted(categories)) if categories else '无'
        error_text = f"未找到命令或分类 '{target}'\n\n"
        error_text += f"可用的分类: {available_categories}\n"
        error_text += "使用 'help' 查看所有可用命令"
        
        return self.error(error_text)
    
    def _get_basic_category_help(self) -> Panel:
        """获取基础分类帮助"""
        table = Table(title="🔧 基础命令详细说明")
        table.add_column("命令", style="cyan", no_wrap=True)
        table.add_column("用法", style="white")
        table.add_column("说明", style="dim")
        
        table.add_row("help", "help [命令|分类]", "显示帮助信息")
        table.add_row("status", "status", "显示当前游戏状态")
        table.add_row("profile", "profile [edit]", "查看或编辑个人资料")
        table.add_row("time", "time", "显示当前游戏时间")
        table.add_row("quit", "quit", "退出游戏")
        
        return Panel(table, border_style="blue")
    
    def _get_finance_category_help(self) -> Panel:
        """获取财务分类帮助"""
        table = Table(title="💰 财务命令详细说明")
        table.add_column("命令", style="cyan", no_wrap=True)
        table.add_column("用法", style="white")
        table.add_column("说明", style="dim")
        
        table.add_row("wallet", "wallet [货币类型]", "查看钱包余额")
        table.add_row("transfer", "transfer <用户> <金额> [货币]", "转账给其他用户")
        table.add_row("exchange", "exchange <from> <to> <金额>", "货币兑换")
        table.add_row("history", "history [类型]", "查看交易历史")
        
        return Panel(table, border_style="green")
    
    def _get_stock_category_help(self) -> Panel:
        """获取股票分类帮助"""
        table = Table(title="📈 股票命令详细说明")
        table.add_column("命令", style="cyan", no_wrap=True)
        table.add_column("用法", style="white")
        table.add_column("说明", style="dim")
        
        table.add_row("market", "market [股票代码]", "查看股票市场信息")
        table.add_row("buy", "buy <股票代码> <数量>", "购买股票")
        table.add_row("sell", "sell <股票代码> <数量>", "出售股票")
        table.add_row("portfolio", "portfolio", "查看投资组合")
        table.add_row("watchlist", "watchlist [add|remove] [股票]", "管理关注列表")
        
        return Panel(table, border_style="yellow")
    
    def _get_app_category_help(self) -> Panel:
        """获取应用分类帮助"""
        table = Table(title="📱 应用命令详细说明")
        table.add_column("命令", style="cyan", no_wrap=True)
        table.add_column("用法", style="white")
        table.add_column("说明", style="dim")
        
        table.add_row("apps", "apps [search] [关键词]", "浏览应用市场")
        table.add_row("install", "install <应用ID>", "安装应用")
        table.add_row("uninstall", "uninstall <应用ID>", "卸载应用")
        table.add_row("create", "create <应用名称>", "创建新应用")
        table.add_row("publish", "publish <应用ID>", "发布应用")
        
        return Panel(table, border_style="magenta")
    
    def _get_news_category_help(self) -> Panel:
        """获取新闻分类帮助"""
        table = Table(title="📰 新闻命令详细说明")
        table.add_column("命令", style="cyan", no_wrap=True)
        table.add_column("用法", style="white")
        table.add_column("说明", style="dim")
        
        table.add_row("news", "news [分类] [数量]", "查看新闻")
        table.add_row("publish", "publish <标题> <内容>", "发布新闻（需要权限）")
        table.add_row("subscribe", "subscribe <分类>", "订阅新闻分类")
        table.add_row("unsubscribe", "unsubscribe <分类>", "取消订阅")
        
        return Panel(table, border_style="blue")
    
    def _get_admin_category_help(self) -> Panel:
        """获取管理分类帮助"""
        table = Table(title="⚙️ 管理命令详细说明")
        table.add_column("命令", style="cyan", no_wrap=True)
        table.add_column("用法", style="white")
        table.add_column("说明", style="dim")
        
        table.add_row("users", "users [list|info] [用户]", "用户管理")
        table.add_row("roles", "roles [list|assign] [参数]", "角色管理")
        table.add_row("system", "system [status|config]", "系统管理")
        table.add_row("logs", "logs [类型] [数量]", "查看系统日志")
        
        warning_text = Text()
        warning_text.append("⚠️ 警告: ", style="bold red")
        warning_text.append("管理命令需要相应的管理员权限才能执行。", style="yellow")
        
        content = Columns([table, Panel(warning_text, border_style="red")])
        
        return Panel(content, border_style="red")
    
    def _get_help_command_help(self) -> Panel:
        """获取help命令帮助"""
        content = Text()
        content.append("命令: ", style="bold")
        content.append("help\n", style="cyan")
        content.append("别名: ", style="bold")
        content.append("h, ?, man\n\n", style="dim")
        content.append("用法:\n", style="bold")
        content.append("  help                    # 显示总体帮助\n", style="white")
        content.append("  help <命令名>           # 显示特定命令帮助\n", style="white")
        content.append("  help <分类名>           # 显示分类帮助\n\n", style="white")
        content.append("示例:\n", style="bold")
        content.append("  help wallet             # 查看wallet命令帮助\n", style="green")
        content.append("  help finance            # 查看财务分类帮助\n", style="green")
        
        return Panel(content, title="📖 Help 命令详细说明", border_style="blue")
    
    def _get_status_command_help(self) -> Panel:
        """获取status命令帮助"""
        content = Text()
        content.append("命令: ", style="bold")
        content.append("status\n", style="cyan")
        content.append("别名: ", style="bold")
        content.append("stat, info\n\n", style="dim")
        content.append("说明: 显示当前游戏状态，包括用户信息、时间、余额等\n\n", style="white")
        content.append("显示内容:\n", style="bold")
        content.append("• 用户基本信息\n", style="white")
        content.append("• 当前游戏时间\n", style="white")
        content.append("• 钱包余额\n", style="white")
        content.append("• 在线状态\n", style="white")
        
        return Panel(content, title="📊 Status 命令详细说明", border_style="blue")
    
    def _get_profile_command_help(self) -> Panel:
        """获取profile命令帮助"""
        content = Text()
        content.append("命令: ", style="bold")
        content.append("profile\n", style="cyan")
        content.append("别名: ", style="bold")
        content.append("prof, me\n\n", style="dim")
        content.append("用法:\n", style="bold")
        content.append("  profile                 # 查看个人资料\n", style="white")
        content.append("  profile edit            # 编辑个人资料\n\n", style="white")
        content.append("可编辑字段:\n", style="bold")
        content.append("• 显示名称\n", style="white")
        content.append("• 个人简介\n", style="white")
        content.append("• 时区设置\n", style="white")
        content.append("• 语言偏好\n", style="white")
        
        return Panel(content, title="👤 Profile 命令详细说明", border_style="blue")
    
    def _get_wallet_command_help(self) -> Panel:
        """获取wallet命令帮助"""
        content = Text()
        content.append("命令: ", style="bold")
        content.append("wallet\n", style="cyan")
        content.append("别名: ", style="bold")
        content.append("balance, money\n\n", style="dim")
        content.append("用法:\n", style="bold")
        content.append("  wallet                  # 显示所有货币余额\n", style="white")
        content.append("  wallet <货币类型>       # 显示特定货币余额\n\n", style="white")
        content.append("支持的货币类型:\n", style="bold")
        content.append("• CNY (人民币)\n", style="white")
        content.append("• USD (美元)\n", style="white")
        content.append("• EUR (欧元)\n", style="white")
        content.append("• JCY (游戏币)\n", style="white")
        
        return Panel(content, title="💰 Wallet 命令详细说明", border_style="blue")
    
    def _get_quit_command_help(self) -> Panel:
        """获取quit命令帮助"""
        content = Text()
        content.append("命令: ", style="bold")
        content.append("quit\n", style="cyan")
        content.append("别名: ", style="bold")
        content.append("exit, bye\n\n", style="dim")
        content.append("说明: 安全退出游戏\n\n", style="white")
        content.append("退出时会:\n", style="bold")
        content.append("• 保存当前游戏状态\n", style="white")
        content.append("• 清理会话数据\n", style="white")
        content.append("• 记录退出日志\n", style="white")
        
        return Panel(content, title="🚪 Quit 命令详细说明", border_style="blue")
    
    def validate_args(self, args: List[str]) -> bool:
        """验证命令参数
        
        Args:
            args: 命令参数
            
        Returns:
            是否有效
        """
        # help命令可以接受0-1个参数
        return len(args) <= 1
    
    def get_help(self) -> str:
        """获取命令帮助信息
        
        Returns:
            帮助信息字符串
        """
        return f"""
命令: {self.name}
别名: {', '.join(self.aliases)}
描述: {self.description}
用法: {self.usage}

参数说明:
  [命令名称]  - 要查看帮助的特定命令
  [分类]      - 要查看帮助的命令分类

示例:
  help              # 显示总体帮助
  help wallet       # 显示wallet命令的帮助
  help finance      # 显示财务分类的帮助

可用分类: basic, finance, stock, app, news, admin
"""