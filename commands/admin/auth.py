# -*- coding: utf-8 -*-
"""
Auth命令

权限认证命令，用于管理员权限提升。
"""

from typing import List
from commands.base import Command, CommandResult, CommandContext
from services.auth_service import AuthService


class AuthCommand(Command):
    """权限认证命令 - 管理员权限提升"""
    
    def __init__(self, auth_service: AuthService = None):
        super().__init__()
        self.auth_service = auth_service
    
    @property
    def name(self) -> str:
        return "auth"
    
    @property
    def aliases(self) -> List[str]:
        return ["authenticate", "login"]
    
    @property
    def description(self) -> str:
        return "权限认证 - 管理员权限提升和身份验证"
    
    @property
    def usage(self) -> str:
        return "auth <管理员密码> | auth status | auth exit"
    
    @property
    def category(self) -> str:
        return "admin"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行auth命令
        
        Args:
            args: 命令参数列表
            context: 命令执行上下文
            
        Returns:
            命令执行结果
        """
        try:
            if not args:
                return self._show_auth_help(context)
            
            first_arg = args[0].lower()
            
            # auth status - 查看当前权限状态
            if first_arg == "status":
                return self._show_auth_status(context)
            
            # auth exit - 退出管理员模式
            elif first_arg == "exit":
                return self._exit_admin_mode(context)
            
            # auth <password> - 使用密码进行权限提升
            else:
                password = args[0]
                return await self._authenticate(password, context)
                
        except Exception as e:
            return self.error(f"权限认证失败: {str(e)}")
    
    def _show_auth_help(self, context: CommandContext) -> CommandResult:
        """显示权限认证帮助"""
        is_admin = context.session_data.get('is_admin', False)
        
        if is_admin:
            help_text = """
🔐 权限认证命令帮助 (管理员模式):

📋 可用命令:
  auth status                    - 查看当前权限状态
  auth exit                      - 退出管理员模式

⚠️ 当前状态:
  您当前处于管理员模式，拥有系统最高权限。
  可以使用所有sudo命令进行系统管理。
"""
        else:
            help_text = """
🔐 权限认证命令帮助:

🔑 权限提升:
  auth <管理员密码>              - 使用管理员密码进行权限提升
  auth status                    - 查看当前权限状态

💡 使用说明:
  • 管理员密码为: admin
  • 认证成功后可使用sudo命令进行系统管理
  • 使用 'auth exit' 退出管理员模式

⚠️ 注意事项:
  • 管理员权限仅在当前会话有效
  • 请谨慎使用管理员权限
  • 所有管理员操作都会被记录
"""
        
        return self.success(help_text)
    
    def _show_auth_status(self, context: CommandContext) -> CommandResult:
        """显示当前权限状态"""
        is_admin = context.session_data.get('is_admin', False)
        user = context.user
        username = getattr(user, 'username', 'unknown') if user else 'unknown'
        
        if is_admin:
            status_text = f"""
🔐 权限状态信息:

👤 用户信息:
  用户名: {username}
  权限级别: 管理员 (Admin)
  会话状态: 已认证 ✅

🛡️ 权限详情:
  • 系统管理权限: ✅ 已授权
  • 用户管理权限: ✅ 已授权
  • 角色管理权限: ✅ 已授权
  • 财务管理权限: ✅ 已授权

⏰ 会话信息:
  认证时间: 当前会话
  有效期: 直到退出或会话结束

💡 可用操作:
  • 使用 'sudo' 命令进行系统管理
  • 使用 'auth exit' 退出管理员模式
"""
        else:
            status_text = f"""
🔐 权限状态信息:

👤 用户信息:
  用户名: {username}
  权限级别: 普通用户 (User)
  会话状态: 未认证 ❌

🛡️ 权限详情:
  • 系统管理权限: ❌ 未授权
  • 用户管理权限: ❌ 未授权
  • 角色管理权限: ❌ 未授权
  • 财务管理权限: ❌ 未授权

💡 权限提升:
  使用 'auth <管理员密码>' 进行权限提升
  管理员密码: admin
"""
        
        return self.success(status_text)
    
    async def _authenticate(self, password: str, context: CommandContext) -> CommandResult:
        """执行权限认证"""
        # 检查是否已经是管理员模式
        if context.session_data.get('is_admin', False):
            return self.error("您已经处于管理员模式")
        
        # 验证管理员密码
        if password == "admin":
            # 设置管理员模式
            context.session_data['is_admin'] = True
            context.session_data['admin_auth_time'] = context.game_time
            
            user = context.user
            username = getattr(user, 'username', 'unknown') if user else 'unknown'
            
            success_text = f"""
🔐 权限认证成功！

✅ 管理员身份验证通过
👤 用户: {username}
⏰ 认证时间: {context.game_time}

🛡️ 已获得权限:
  • 系统管理权限
  • 用户管理权限
  • 角色管理权限
  • 财务管理权限

💡 可用操作:
  • 使用 'sudo' 命令进行系统管理
  • 使用 'auth status' 查看权限状态
  • 使用 'auth exit' 退出管理员模式

⚠️ 安全提醒:
  请谨慎使用管理员权限，所有操作都会被记录。
"""
            
            return self.success(success_text)
        else:
            return self.error("❌ 管理员密码错误，权限认证失败")
    
    def _exit_admin_mode(self, context: CommandContext) -> CommandResult:
        """退出管理员模式"""
        if not context.session_data.get('is_admin', False):
            return self.error("您当前不在管理员模式")
        
        # 清除管理员模式状态
        context.session_data['is_admin'] = False
        context.session_data.pop('admin_auth_time', None)
        
        user = context.user
        username = getattr(user, 'username', 'unknown') if user else 'unknown'
        
        exit_text = f"""
🔐 已退出管理员模式

👤 用户: {username}
📉 权限级别: 普通用户
⏰ 退出时间: {context.game_time}

✅ 权限状态已重置:
  • 系统管理权限: 已撤销
  • 用户管理权限: 已撤销
  • 角色管理权限: 已撤销
  • 财务管理权限: 已撤销

💡 如需再次使用管理员权限，请使用 'auth <密码>' 重新认证。
"""
        
        return self.success(exit_text)