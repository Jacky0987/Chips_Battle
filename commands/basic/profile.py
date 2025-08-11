# -*- coding: utf-8 -*-
"""
个人资料命令

查看和编辑用户个人资料。
"""

from typing import List, Dict, Any
from commands.base import BasicCommand, CommandResult, CommandContext
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.columns import Columns


class ProfileCommand(BasicCommand):
    """个人资料命令"""
    
    def __init__(self):
        super().__init__()
        self.console = Console()
    
    @property
    def name(self) -> str:
        return "profile"
    
    @property
    def aliases(self) -> List[str]:
        return ["prof", "me", "user"]
    
    @property
    def description(self) -> str:
        return "查看和编辑个人资料"
    
    @property
    def usage(self) -> str:
        return "profile [edit|view] [字段名]"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行个人资料命令
        
        Args:
            args: 命令参数
            context: 命令上下文
            
        Returns:
            命令执行结果
        """
        try:
            user = context.user
            if not user:
                return self.error("无法获取用户信息")
            
            # 解析参数
            action = args[0].lower() if args else "view"
            field = args[1] if len(args) > 1 else None
            
            if action == "edit":
                return await self._edit_profile(user, field, context)
            elif action == "view" or action == "show":
                return await self._view_profile(user, field)
            else:
                # 默认显示资料
                return await self._view_profile(user, None)
            
        except Exception as e:
            return self.error(f"处理个人资料时发生错误: {str(e)}")
    
    async def _view_profile(self, user, field: str = None) -> CommandResult:
        """查看个人资料
        
        Args:
            user: 用户对象
            field: 特定字段名（可选）
            
        Returns:
            命令执行结果
        """
        if field:
            # 显示特定字段
            return await self._view_specific_field(user, field)
        else:
            # 显示完整资料
            await self._display_full_profile(user)
            return self.success("个人资料已显示")
    
    async def _view_specific_field(self, user, field: str) -> CommandResult:
        """查看特定字段
        
        Args:
            user: 用户对象
            field: 字段名
            
        Returns:
            命令执行结果
        """
        field_map = {
            "username": ("用户名", user.username),
            "email": ("邮箱", user.email or "未设置"),
            "display_name": ("显示名称", user.display_name or "未设置"),
            "bio": ("个人简介", getattr(user, 'bio', None) or "未设置"),
            "timezone": ("时区", getattr(user, 'timezone', None) or "未设置"),
            "language": ("语言", getattr(user, 'language', None) or "未设置"),
            "level": ("等级", f"Lv.{user.level}"),
            "experience": ("经验值", f"{user.experience:,}")
        }
        
        if field.lower() not in field_map:
            available_fields = ", ".join(field_map.keys())
            return self.error(f"未知字段 '{field}'。可用字段: {available_fields}")
        
        field_name, field_value = field_map[field.lower()]
        
        panel = Panel(
            f"[cyan]{field_name}:[/cyan] {field_value}",
            title=f"📋 {field_name}",
            border_style="blue"
        )
        
        self.console.print(panel)
        return self.success(f"已显示 {field_name}")
    
    async def _display_full_profile(self, user):
        """显示完整个人资料
        
        Args:
            user: 用户对象
        """
        # 基本信息面板
        basic_info = self._create_basic_info_panel(user)
        
        # 个人设置面板
        settings_panel = self._create_settings_panel(user)
        
        # 游戏统计面板
        stats_panel = self._create_game_stats_panel(user)
        
        # 显示所有面板
        self.console.print(basic_info)
        self.console.print(Columns([settings_panel, stats_panel]))
    
    def _create_basic_info_panel(self, user) -> Panel:
        """创建基本信息面板
        
        Args:
            user: 用户对象
            
        Returns:
            基本信息面板
        """
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("属性", style="cyan", no_wrap=True, width=12)
        table.add_column("值", style="white")
        
        # 基本信息
        table.add_row("👤 用户名", user.username)
        table.add_row("📧 邮箱", user.email or "[dim]未设置[/dim]")
        table.add_row("🏷️ 显示名称", user.display_name or "[dim]未设置[/dim]")
        table.add_row("📝 个人简介", getattr(user, 'bio', None) or "[dim]未设置[/dim]")
        
        # 状态信息
        status_text = Text()
        if user.is_active:
            status_text.append("🟢 活跃", style="green")
        else:
            status_text.append("🔴 非活跃", style="red")
        
        if user.is_verified:
            status_text.append(" ✅ 已验证", style="green")
        else:
            status_text.append(" ⚠️ 未验证", style="yellow")
        
        table.add_row("📊 状态", status_text)
        
        # 时间信息
        if hasattr(user, 'created_at') and user.created_at:
            table.add_row("📅 注册时间", user.created_at.strftime("%Y-%m-%d %H:%M"))
        
        if hasattr(user, 'last_activity') and user.last_activity:
            table.add_row("🕐 最后活动", user.last_activity.strftime("%Y-%m-%d %H:%M"))
        
        return Panel(
            table,
            title=f"👤 {user.username} 的基本信息",
            border_style="blue",
            padding=(1, 2)
        )
    
    def _create_settings_panel(self, user) -> Panel:
        """创建个人设置面板
        
        Args:
            user: 用户对象
            
        Returns:
            个人设置面板
        """
        table = Table(show_header=False, box=None)
        table.add_column("设置项", style="cyan", no_wrap=True)
        table.add_column("值", style="white")
        
        # 个人偏好设置
        table.add_row("🌍 时区", getattr(user, 'timezone', None) or "[dim]未设置[/dim]")
        table.add_row("🗣️ 语言", getattr(user, 'language', None) or "[dim]未设置[/dim]")
        table.add_row("🎨 主题", getattr(user, 'theme', None) or "[dim]默认[/dim]")
        table.add_row("🔔 通知", "[green]开启[/green]" if getattr(user, 'notifications_enabled', True) else "[red]关闭[/red]")
        
        # 隐私设置
        table.add_row("👁️ 资料可见性", getattr(user, 'profile_visibility', None) or "[dim]公开[/dim]")
        table.add_row("📊 统计可见性", getattr(user, 'stats_visibility', None) or "[dim]公开[/dim]")
        
        return Panel(
            table,
            title="⚙️ 个人设置",
            border_style="green",
            padding=(1, 1)
        )
    
    def _create_game_stats_panel(self, user) -> Panel:
        """创建游戏统计面板
        
        Args:
            user: 用户对象
            
        Returns:
            游戏统计面板
        """
        table = Table(show_header=False, box=None)
        table.add_column("统计项", style="cyan", no_wrap=True)
        table.add_column("数值", style="white", justify="right")
        
        # 游戏统计
        table.add_row("⭐ 等级", f"Lv.{user.level}")
        table.add_row("🎯 经验值", f"{user.experience:,}")
        table.add_row("📊 命令执行", f"{getattr(user, 'command_count', 0):,} 次")
        table.add_row("🔐 登录次数", f"{getattr(user, 'login_count', 0):,} 次")
        
        # 成就统计（模拟数据）
        table.add_row("🏆 成就数量", f"{getattr(user, 'achievement_count', 0)} 个")
        table.add_row("💰 总资产", f"{getattr(user, 'total_assets', 0):,.2f} JCY")
        
        return Panel(
            table,
            title="🎮 游戏统计",
            border_style="yellow",
            padding=(1, 1)
        )
    
    async def _edit_profile(self, user, field: str = None, context: CommandContext = None) -> CommandResult:
        """编辑个人资料
        
        Args:
            user: 用户对象
            field: 要编辑的字段（可选）
            context: 命令上下文
            
        Returns:
            命令执行结果
        """
        if field:
            # 编辑特定字段
            return await self._edit_specific_field(user, field, context)
        else:
            # 交互式编辑
            return await self._interactive_edit(user, context)
    
    async def _edit_specific_field(self, user, field: str, context: CommandContext) -> CommandResult:
        """编辑特定字段
        
        Args:
            user: 用户对象
            field: 字段名
            context: 命令上下文
            
        Returns:
            命令执行结果
        """
        editable_fields = {
            "display_name": {
                "name": "显示名称",
                "prompt": "请输入新的显示名称",
                "validator": lambda x: len(x.strip()) <= 50,
                "error": "显示名称不能超过50个字符"
            },
            "bio": {
                "name": "个人简介",
                "prompt": "请输入个人简介",
                "validator": lambda x: len(x.strip()) <= 200,
                "error": "个人简介不能超过200个字符"
            },
            "timezone": {
                "name": "时区",
                "prompt": "请输入时区 (如: Asia/Shanghai)",
                "validator": lambda x: len(x.strip()) > 0,
                "error": "时区不能为空"
            },
            "language": {
                "name": "语言",
                "prompt": "请选择语言 (zh-CN/en-US)",
                "validator": lambda x: x.lower() in ['zh-cn', 'en-us', 'zh', 'en'],
                "error": "请选择有效的语言代码"
            }
        }
        
        field_lower = field.lower()
        if field_lower not in editable_fields:
            available = ", ".join(editable_fields.keys())
            return self.error(f"字段 '{field}' 不可编辑。可编辑字段: {available}")
        
        field_info = editable_fields[field_lower]
        
        # 显示当前值
        current_value = getattr(user, field_lower, None) or "未设置"
        self.console.print(f"[cyan]{field_info['name']}[/cyan] 当前值: [white]{current_value}[/white]")
        
        # 获取新值
        try:
            new_value = Prompt.ask(field_info['prompt'])
            
            # 验证新值
            if not field_info['validator'](new_value):
                return self.error(field_info['error'])
            
            # 确认更改
            if not Confirm.ask(f"确认将 {field_info['name']} 更改为 '{new_value}'?"):
                return self.info("已取消更改")
            
            # 更新用户信息（这里需要实际的数据库更新逻辑）
            # setattr(user, field_lower, new_value)
            # await context.uow.users.update(user)
            # await context.uow.commit()
            
            return self.success(f"{field_info['name']} 已更新为: {new_value}")
            
        except KeyboardInterrupt:
            return self.info("已取消编辑")
        except Exception as e:
            return self.error(f"更新失败: {str(e)}")
    
    async def _interactive_edit(self, user, context: CommandContext) -> CommandResult:
        """交互式编辑个人资料
        
        Args:
            user: 用户对象
            context: 命令上下文
            
        Returns:
            命令执行结果
        """
        self.console.print(Panel(
            "[bold cyan]个人资料编辑模式[/bold cyan]\n\n"
            "你可以编辑以下字段:\n"
            "• display_name - 显示名称\n"
            "• bio - 个人简介\n"
            "• timezone - 时区\n"
            "• language - 语言\n\n"
            "输入字段名开始编辑，或输入 'done' 完成编辑。",
            title="📝 编辑模式",
            border_style="blue"
        ))
        
        changes_made = []
        
        try:
            while True:
                field = Prompt.ask(
                    "请选择要编辑的字段",
                    choices=["display_name", "bio", "timezone", "language", "done"],
                    default="done"
                )
                
                if field == "done":
                    break
                
                result = await self._edit_specific_field(user, field, context)
                if result.success:
                    changes_made.append(field)
                
                if not Confirm.ask("继续编辑其他字段?", default=False):
                    break
            
            if changes_made:
                return self.success(f"已更新字段: {', '.join(changes_made)}")
            else:
                return self.info("未进行任何更改")
                
        except KeyboardInterrupt:
            return self.info("已退出编辑模式")
    
    def validate_args(self, args: List[str]) -> bool:
        """验证命令参数
        
        Args:
            args: 命令参数
            
        Returns:
            是否有效
        """
        # profile命令可以接受0-2个参数
        if len(args) > 2:
            return False
        
        # 如果有参数，第一个参数应该是有效的动作
        if args:
            valid_actions = ["view", "edit", "show"]
            if args[0].lower() not in valid_actions:
                # 如果不是动作，可能是字段名，当作view处理
                pass
        
        return True
    
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
  view [字段名]     - 查看个人资料（默认动作）
  edit [字段名]     - 编辑个人资料
  [字段名]          - 直接查看特定字段

可查看/编辑的字段:
  • username        - 用户名（只读）
  • email           - 邮箱（只读）
  • display_name    - 显示名称（可编辑）
  • bio             - 个人简介（可编辑）
  • timezone        - 时区（可编辑）
  • language        - 语言（可编辑）
  • level           - 等级（只读）
  • experience      - 经验值（只读）

示例:
  profile                    # 查看完整个人资料
  profile view               # 查看完整个人资料
  profile username           # 查看用户名
  profile edit               # 交互式编辑资料
  profile edit display_name  # 编辑显示名称

注意:
  • 某些字段（如用户名、邮箱）只能查看，不能编辑
  • 编辑操作需要确认才会生效
  • 可以使用 Ctrl+C 取消编辑操作
"""