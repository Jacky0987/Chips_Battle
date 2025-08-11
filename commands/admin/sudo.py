# -*- coding: utf-8 -*-
"""
Sudo命令

提供管理员权限提升功能，允许管理员执行特权命令。
"""

from typing import List
from commands.base import Command, CommandResult, CommandContext
from services.auth_service import AuthService


class SudoCommand(Command):
    """Sudo命令 - 管理员权限提升"""
    
    def __init__(self, auth_service: AuthService = None):
        super().__init__()
        self.auth_service = auth_service
    
    @property
    def category(self) -> str:
        return "admin"
    
    @property
    def name(self) -> str:
        return "sudo"
    
    @property
    def aliases(self) -> List[str]:
        return ["su", "admin"]
    
    @property
    def description(self) -> str:
        return "管理员权限提升 - 执行管理员命令"
    
    @property
    def usage(self) -> str:
        return "sudo <命令> [参数...]"
    
    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行sudo命令，需要先通过auth命令获得管理员权限"""
        # 检查是否已经通过auth命令获得管理员权限
        is_admin = context.session_data.get('is_admin', False)
        if not is_admin:
            return self.error("❌ 需要管理员权限。请先使用 'auth <密码>' 进行权限提升。")
        
        return await self._execute_admin_command(args, context)
    
    async def _execute_admin_command(self, args: List[str], context: CommandContext) -> CommandResult:
        """执行管理员命令"""
        if not args:
            return self._show_admin_help()
            
        subcommand = args[0].lower()
        sub_args = args[1:] if len(args) > 1 else []
        
        if subcommand == "help":
            return self._show_admin_help()
        elif subcommand == "exit":
            return self._exit_sudo_mode(context)
        elif subcommand == "user":
            return await self._handle_user_command(sub_args, context)
        elif subcommand == "role":
            return await self._handle_role_command(sub_args, context)
        elif subcommand == "system":
            return await self._handle_system_command(sub_args, context)
        elif subcommand == "money":
            return await self._handle_money_command(sub_args, context)
        else:
            return self.error(f"未知的sudo命令: {subcommand}\n使用 'sudo help' 查看帮助")
    
    def _show_sudo_help(self) -> CommandResult:
        """显示sudo帮助信息"""
        help_text = """
🔐 Sudo 管理员命令帮助:

⚠️ 权限要求:
  需要先使用 'auth <密码>' 进行管理员权限提升
  
💡 使用说明:
  - 管理员密码为: admin
  - 认证成功后可使用sudo命令进行系统管理
  - 使用 'sudo help' 查看管理员命令列表
"""
        return self.success(help_text)
    
    def _show_admin_help(self) -> CommandResult:
        """显示管理员帮助信息"""
        help_text = """
🔐 Sudo 管理员命令帮助:

📋 基本命令:
  sudo help                      - 显示此帮助信息
  sudo exit                      - 退出管理员模式

👥 用户管理:
  sudo user list                 - 列出所有用户
  sudo user info <用户>          - 查看用户详细信息
  sudo user ban <用户>           - 封禁用户
  sudo user unban <用户>         - 解封用户
  sudo user delete <用户>        - 删除用户

🎭 角色管理:
  sudo role list                 - 列出所有角色
  sudo role create <角色>        - 创建新角色
  sudo role delete <角色>        - 删除角色
  sudo role assign <用户> <角色> - 分配角色给用户
  sudo role revoke <用户> <角色> - 撤销用户角色

💰 资金管理:
  sudo money add <用户> <金额>   - 给用户增加资金
  sudo money sub <用户> <金额>   - 扣除用户资金
  sudo money set <用户> <金额>   - 设置用户资金
  sudo money info <用户>         - 查看用户资金信息

⚙️ 系统管理:
  sudo system status             - 查看系统状态
  sudo system restart            - 重启系统服务
  sudo system backup             - 创建系统备份
  sudo system logs               - 查看系统日志

⚠️ 注意:
  - 您当前处于管理员模式
  - 请谨慎使用系统管理命令
  - 操作会被记录在审计日志中
"""
        return self.success(help_text)
    
    def _exit_sudo_mode(self, context: CommandContext) -> CommandResult:
        """退出sudo模式"""
        # 清除管理员模式状态
        context.session_data['is_admin'] = False
        return self.success("已退出管理员模式")
    
    async def _handle_user_command(self, args: List[str], context: CommandContext) -> CommandResult:
        """处理用户管理命令"""
        if not args:
            return self.error("请指定用户管理操作\n使用 'sudo user list' 查看所有用户")
        
        action = args[0].lower()
        
        if action == "list":
            return await self._list_users(context)
        elif action == "info" and len(args) > 1:
            return await self._user_info(args[1], context)
        elif action == "ban" and len(args) > 1:
            return await self._ban_user(args[1], context)
        elif action == "unban" and len(args) > 1:
            return await self._unban_user(args[1], context)
        elif action == "delete" and len(args) > 1:
            return await self._delete_user(args[1], context)
        else:
            return self.error(f"未知的用户管理操作: {action}")
    
    async def _handle_role_command(self, args: List[str], context: CommandContext) -> CommandResult:
        """处理角色管理命令"""
        if not args:
            return self.error("请指定角色管理操作\n使用 'sudo role list' 查看所有角色")
        
        action = args[0].lower()
        
        if action == "list":
            return await self._list_roles(context)
        elif action == "create" and len(args) > 1:
            return await self._create_role(args[1], context)
        elif action == "delete" and len(args) > 1:
            return await self._delete_role(args[1], context)
        elif action == "assign" and len(args) > 2:
            return await self._assign_role(args[1], args[2], context)
        elif action == "revoke" and len(args) > 2:
            return await self._revoke_role(args[1], args[2], context)
        else:
            return self.error(f"未知的角色管理操作: {action}")
    
    async def _handle_system_command(self, args: List[str], context: CommandContext) -> CommandResult:
        """处理系统管理命令"""
        if not args:
            return self.error("请指定系统管理操作\n使用 'sudo system status' 查看系统状态")
        
        action = args[0].lower()
        
        if action == "status":
            return await self._system_status(context)
        elif action == "restart":
            return await self._system_restart(context)
        elif action == "backup":
            return await self._system_backup(context)
        elif action == "logs":
            return await self._system_logs(context)
        else:
            return self.error(f"未知的系统管理操作: {action}")
    
    # 用户管理方法
    async def _list_users(self, context: CommandContext) -> CommandResult:
        """列出所有用户"""
        try:
            from sqlalchemy import select, func
            from models.auth.user import User
            from rich.table import Table
            from rich.console import Console
            
            # 获取所有用户
            result = await context.uow.session.execute(
                select(User).order_by(User.created_at.desc())
            )
            users = result.scalars().all()
            
            if not users:
                return self.success("系统中暂无用户")
            
            # 创建表格
            table = Table(title="用户列表")
            table.add_column("ID", style="cyan")
            table.add_column("用户名", style="green")
            table.add_column("邮箱", style="blue")
            table.add_column("显示名", style="yellow")
            table.add_column("状态", style="red")
            table.add_column("注册时间", style="magenta")
            
            for user in users:
                status = "正常" if user.is_active else "禁用"
                if hasattr(user, 'is_verified') and not user.is_verified:
                    status += "/未验证"
                
                table.add_row(
                    user.user_id[:8] + "...",
                    user.username,
                    user.email or "未设置",
                    user.display_name or user.username,
                    status,
                    user.created_at.strftime("%Y-%m-%d %H:%M")
                )
            
            # 渲染表格到字符串
            console = Console(width=120, legacy_windows=False)
            with console.capture() as capture:
                console.print(table)
            
            return self.success(f"找到 {len(users)} 个用户:\n{capture.get()}")
            
        except Exception as e:
            return self.error(f"获取用户列表失败: {str(e)}")
    
    async def _user_info(self, username: str, context: CommandContext) -> CommandResult:
        """查看用户信息"""
        try:
            from sqlalchemy import select
            from models.auth.user import User
            from models.bank.bank_account import BankAccount
            from models.bank.bank_card import BankCard
            from rich.table import Table
            from rich.console import Console
            
            # 查找用户
            result = await context.uow.session.execute(
                select(User).filter(User.username == username)
            )
            user = result.scalars().first()
            
            if not user:
                return self.error(f"用户 '{username}' 不存在")
            
            # 获取用户的银行信息
            accounts_result = await context.uow.session.execute(
                select(BankAccount).filter(BankAccount.user_id == user.user_id)
            )
            accounts = accounts_result.scalars().all()
            
            cards_result = await context.uow.session.execute(
                select(BankCard).filter(BankCard.user_id == user.user_id)
            )
            cards = cards_result.scalars().all()
            
            # 创建用户信息表格
            table = Table(title=f"用户信息 - {username}")
            table.add_column("属性", style="cyan")
            table.add_column("值", style="green")
            
            # 基本信息
            table.add_row("用户ID", user.user_id)
            table.add_row("用户名", user.username)
            table.add_row("邮箱", user.email or "未设置")
            table.add_row("显示名", user.display_name or user.username)
            table.add_row("状态", "正常" if user.is_active else "禁用")
            table.add_row("注册时间", user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
            table.add_row("最后更新", user.updated_at.strftime("%Y-%m-%d %H:%M:%S"))
            
            # 银行信息
            table.add_row("银行卡数量", str(len(cards)))
            table.add_row("银行账户数量", str(len(accounts)))
            
            if accounts:
                total_balance = sum(float(acc.balance or 0) for acc in accounts)
                table.add_row("总资产", f"{total_balance:.2f}")
            
            # 渲染表格
            console = Console(width=100, legacy_windows=False)
            with console.capture() as capture:
                console.print(table)
            
            return self.success(f"用户信息:\n{capture.get()}")
            
        except Exception as e:
            return self.error(f"获取用户信息失败: {str(e)}")
    
    async def _ban_user(self, username: str, context: CommandContext) -> CommandResult:
        """封禁用户"""
        try:
            from sqlalchemy import select, update
            from models.auth.user import User
            
            # 查找用户
            result = await context.uow.session.execute(
                select(User).filter(User.username == username)
            )
            user = result.scalars().first()
            
            if not user:
                return self.error(f"用户 '{username}' 不存在")
            
            if not user.is_active:
                return self.error(f"用户 '{username}' 已经被封禁")
            
            # 封禁用户
            await context.uow.session.execute(
                update(User)
                .where(User.user_id == user.user_id)
                .values(is_active=False)
            )
            
            await context.uow.commit()
            
            return self.success(f"用户 '{username}' 已被封禁")
            
        except Exception as e:
            return self.error(f"封禁用户失败: {str(e)}")
    
    async def _unban_user(self, username: str, context: CommandContext) -> CommandResult:
        """解封用户"""
        try:
            from sqlalchemy import select, update
            from models.auth.user import User
            
            # 查找用户
            result = await context.uow.session.execute(
                select(User).filter(User.username == username)
            )
            user = result.scalars().first()
            
            if not user:
                return self.error(f"用户 '{username}' 不存在")
            
            if user.is_active:
                return self.error(f"用户 '{username}' 未被封禁")
            
            # 解封用户
            await context.uow.session.execute(
                update(User)
                .where(User.user_id == user.user_id)
                .values(is_active=True)
            )
            
            await context.uow.commit()
            
            return self.success(f"用户 '{username}' 已被解封")
            
        except Exception as e:
            return self.error(f"解封用户失败: {str(e)}")
    
    async def _delete_user(self, username: str, context: CommandContext) -> CommandResult:
        """删除用户"""
        try:
            from sqlalchemy import select, delete
            from models.auth.user import User
            from models.bank.bank_account import BankAccount
            from models.bank.bank_card import BankCard
            
            # 查找用户
            result = await context.uow.session.execute(
                select(User).filter(User.username == username)
            )
            user = result.scalars().first()
            
            if not user:
                return self.error(f"用户 '{username}' 不存在")
            
            # 检查用户是否有银行资产
            accounts_result = await context.uow.session.execute(
                select(BankAccount).filter(BankAccount.user_id == user.user_id)
            )
            accounts = accounts_result.scalars().all()
            
            total_balance = sum(float(acc.balance or 0) for acc in accounts)
            if total_balance > 0:
                return self.error(f"用户 '{username}' 仍有资产 {total_balance:.2f}，无法删除")
            
            # 删除用户的银行卡和账户
            await context.uow.session.execute(
                delete(BankCard).where(BankCard.user_id == user.user_id)
            )
            await context.uow.session.execute(
                delete(BankAccount).where(BankAccount.user_id == user.user_id)
            )
            
            # 删除用户
            await context.uow.session.execute(
                delete(User).where(User.user_id == user.user_id)
            )
            
            await context.uow.commit()
            
            return self.success(f"用户 '{username}' 已删除")
            
        except Exception as e:
            return self.error(f"删除用户失败: {str(e)}")
    
    # 角色管理方法
    async def _list_roles(self, context: CommandContext) -> CommandResult:
        """列出所有角色"""
        try:
            from sqlalchemy import select
            from models.auth.role import Role
            from rich.table import Table
            from rich.console import Console
            
            # 获取所有角色
            result = await context.uow.session.execute(
                select(Role).order_by(Role.name)
            )
            roles = result.scalars().all()
            
            if not roles:
                return self.success("系统中暂无角色")
            
            # 创建角色表格
            table = Table(title="角色列表")
            table.add_column("ID", style="cyan")
            table.add_column("角色名", style="green")
            table.add_column("描述", style="blue")
            table.add_column("创建时间", style="magenta")
            
            for role in roles:
                table.add_row(
                    str(role.role_id),
                    role.name,
                    role.description or "无描述",
                    role.created_at.strftime("%Y-%m-%d %H:%M") if hasattr(role, 'created_at') and role.created_at else "未知"
                )
            
            # 渲染表格
            console = Console(width=100, legacy_windows=False)
            with console.capture() as capture:
                console.print(table)
            
            return self.success(f"找到 {len(roles)} 个角色:\n{capture.get()}")
            
        except Exception as e:
            return self.error(f"获取角色列表失败: {str(e)}")
    
    async def _create_role(self, role_name: str, context: CommandContext) -> CommandResult:
        """创建角色"""
        try:
            from sqlalchemy import select
            from models.auth.role import Role
            import uuid
            from datetime import datetime
            
            # 检查角色是否已存在
            result = await context.uow.session.execute(
                select(Role).filter(Role.name == role_name)
            )
            existing_role = result.scalars().first()
            
            if existing_role:
                return self.error(f"角色 '{role_name}' 已存在")
            
            # 创建新角色
            new_role = Role(
                role_id=str(uuid.uuid4()),
                name=role_name,
                description=f"管理员创建的角色: {role_name}",
                created_at=GameTime.now() if GameTime.is_initialized() else datetime.now(),
                updated_at=GameTime.now() if GameTime.is_initialized() else datetime.now()
            )
            
            context.uow.session.add(new_role)
            await context.uow.commit()
            
            return self.success(f"角色 '{role_name}' 创建成功")
            
        except Exception as e:
            return self.error(f"创建角色失败: {str(e)}")
    
    async def _delete_role(self, role_name: str, context: CommandContext) -> CommandResult:
        """删除角色"""
        try:
            from sqlalchemy import select, delete
            from models.auth.role import Role
            
            # 查找角色
            result = await context.uow.session.execute(
                select(Role).filter(Role.name == role_name)
            )
            role = result.scalars().first()
            
            if not role:
                return self.error(f"角色 '{role_name}' 不存在")
            
            # 删除角色
            await context.uow.session.execute(
                delete(Role).where(Role.role_id == role.role_id)
            )
            
            await context.uow.commit()
            
            return self.success(f"角色 '{role_name}' 已删除")
            
        except Exception as e:
            return self.error(f"删除角色失败: {str(e)}")
    
    async def _assign_role(self, username: str, role_name: str, context: CommandContext) -> CommandResult:
        """分配角色"""
        try:
            from sqlalchemy import select
            from models.auth.user import User
            from models.auth.role import Role
            from models.auth.user_role import UserRole
            import uuid
            from datetime import datetime
            
            # 查找用户
            user_result = await context.uow.session.execute(
                select(User).filter(User.username == username)
            )
            user = user_result.scalars().first()
            
            if not user:
                return self.error(f"用户 '{username}' 不存在")
            
            # 查找角色
            role_result = await context.uow.session.execute(
                select(Role).filter(Role.name == role_name)
            )
            role = role_result.scalars().first()
            
            if not role:
                return self.error(f"角色 '{role_name}' 不存在")
            
            # 检查是否已经分配
            existing_result = await context.uow.session.execute(
                select(UserRole).filter(
                    UserRole.user_id == user.user_id,
                    UserRole.role_id == role.role_id
                )
            )
            existing = existing_result.scalars().first()
            
            if existing:
                return self.error(f"用户 '{username}' 已经拥有角色 '{role_name}'")
            
            # 分配角色
            user_role = UserRole(
                user_role_id=str(uuid.uuid4()),
                user_id=user.user_id,
                role_id=role.role_id,
                assigned_at=GameTime.now() if GameTime.is_initialized() else datetime.now()
            )
            
            context.uow.session.add(user_role)
            await context.uow.commit()
            
            return self.success(f"已为用户 '{username}' 分配角色 '{role_name}'")
            
        except Exception as e:
            return self.error(f"分配角色失败: {str(e)}")
    
    async def _revoke_role(self, username: str, role_name: str, context: CommandContext) -> CommandResult:
        """撤销角色"""
        try:
            from sqlalchemy import select, delete
            from models.auth.user import User
            from models.auth.role import Role
            from models.auth.user_role import UserRole
            
            # 查找用户
            user_result = await context.uow.session.execute(
                select(User).filter(User.username == username)
            )
            user = user_result.scalars().first()
            
            if not user:
                return self.error(f"用户 '{username}' 不存在")
            
            # 查找角色
            role_result = await context.uow.session.execute(
                select(Role).filter(Role.name == role_name)
            )
            role = role_result.scalars().first()
            
            if not role:
                return self.error(f"角色 '{role_name}' 不存在")
            
            # 查找用户角色关系
            user_role_result = await context.uow.session.execute(
                select(UserRole).filter(
                    UserRole.user_id == user.user_id,
                    UserRole.role_id == role.role_id
                )
            )
            user_role = user_role_result.scalars().first()
            
            if not user_role:
                return self.error(f"用户 '{username}' 没有角色 '{role_name}'")
            
            # 撤销角色
            await context.uow.session.execute(
                delete(UserRole).where(
                    UserRole.user_id == user.user_id,
                    UserRole.role_id == role.role_id
                )
            )
            
            await context.uow.commit()
            
            return self.success(f"已撤销用户 '{username}' 的角色 '{role_name}'")
            
        except Exception as e:
            return self.error(f"撤销角色失败: {str(e)}")
    
    # 系统管理方法
    async def _system_status(self, context: CommandContext) -> CommandResult:
        """系统状态"""
        try:
            from sqlalchemy import select, func, text
            from models.auth.user import User
            from models.bank.bank_account import BankAccount
            from models.bank.bank_card import BankCard
            from rich.table import Table
            from rich.console import Console
            import psutil
            import datetime
            
            # 获取系统统计信息
            user_count_result = await context.uow.session.execute(select(func.count(User.user_id)))
            user_count = user_count_result.scalar()
            
            active_user_count_result = await context.uow.session.execute(
                select(func.count(User.user_id)).filter(User.is_active == True)
            )
            active_user_count = active_user_count_result.scalar()
            
            account_count_result = await context.uow.session.execute(select(func.count(BankAccount.account_id)))
            account_count = account_count_result.scalar()
            
            card_count_result = await context.uow.session.execute(select(func.count(BankCard.card_id)))
            card_count = card_count_result.scalar()
            
            # 系统资源信息
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # 创建状态表格
            table = Table(title="系统状态")
            table.add_column("项目", style="cyan")
            table.add_column("值", style="green")
            
            # 添加数据库统计
            table.add_row("总用户数", str(user_count))
            table.add_row("活跃用户数", str(active_user_count))
            table.add_row("银行账户数", str(account_count))
            table.add_row("银行卡数", str(card_count))
            
            # 添加系统资源
            table.add_row("CPU使用率", f"{cpu_percent}%")
            table.add_row("内存使用率", f"{memory.percent}%")
            table.add_row("磁盘使用率", f"{disk.percent}%")
            table.add_row("系统时间", (GameTime.now() if GameTime.is_initialized() else datetime.now()).strftime("%Y-%m-%d %H:%M:%S"))
            
            # 渲染表格
            console = Console(width=80, legacy_windows=False)
            with console.capture() as capture:
                console.print(table)
            
            return self.success(f"系统状态:\n{capture.get()}")
            
        except Exception as e:
            return self.error(f"获取系统状态失败: {str(e)}")
    
    async def _system_restart(self, context: CommandContext) -> CommandResult:
        """系统重启"""
        # TODO: 实现系统重启功能
        return self.success("系统重启功能待实现")
    
    async def _system_backup(self, context: CommandContext) -> CommandResult:
        """系统备份"""
        # TODO: 实现系统备份功能
        return self.success("系统备份功能待实现")
    
    async def _system_logs(self, context: CommandContext) -> CommandResult:
        """查看系统日志"""
        try:
            import os
            from datetime import datetime
            from rich.table import Table
            from rich.console import Console
            from core.game_time import GameTime
            
            # 获取当前时间
            current_time = GameTime.now() if GameTime.is_initialized() else datetime.now()
            time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 模拟系统日志（实际项目中应该从日志文件或数据库读取）
            logs = [
                {
                    "time": time_str,
                    "level": "INFO",
                    "module": "system",
                    "message": "系统正常运行"
                },
                {
                    "time": time_str,
                    "level": "INFO",
                    "module": "auth",
                    "message": "用户认证服务正常"
                },
                {
                    "time": time_str,
                    "level": "INFO",
                    "module": "bank",
                    "message": "银行服务正常运行"
                },
                {
                    "time": time_str,
                    "level": "INFO",
                    "module": "database",
                    "message": "数据库连接正常"
                }
            ]
            
            # 创建日志表格
            table = Table(title="系统日志 (最近记录)")
            table.add_column("时间", style="cyan")
            table.add_column("级别", style="yellow")
            table.add_column("模块", style="green")
            table.add_column("消息", style="white")
            
            for log in logs:
                level_style = "green" if log["level"] == "INFO" else "red" if log["level"] == "ERROR" else "yellow"
                table.add_row(
                    log["time"],
                    f"[{level_style}]{log['level']}[/{level_style}]",
                    log["module"],
                    log["message"]
                )
            
            # 渲染表格
            console = Console(width=120, legacy_windows=False)
            with console.capture() as capture:
                console.print(table)
            
            return self.success(f"系统日志:\n{capture.get()}")
            
        except Exception as e:
            return self.error(f"获取系统日志失败: {str(e)}")
    
    async def _handle_money_command(self, args: List[str], context: CommandContext) -> CommandResult:
        """处理资金管理命令"""
        if not args:
            return self.error("请指定资金管理操作\n使用 'sudo money info <用户>' 查看用户资金")
        
        action = args[0].lower()
        
        if action == "add" and len(args) >= 3:
            return await self._add_user_money(args[1], args[2], context)
        elif action == "sub" and len(args) >= 3:
            return await self._subtract_user_money(args[1], args[2], context)
        elif action == "set" and len(args) >= 3:
            return await self._set_user_money(args[1], args[2], context)
        elif action == "info" and len(args) >= 2:
            return await self._get_user_money_info(args[1], context)
        else:
            return self.error(f"未知的资金管理操作: {action}")
    
    async def _add_user_money(self, username: str, amount_str: str, context: CommandContext) -> CommandResult:
        """给用户增加资金"""
        try:
            from decimal import Decimal
            from sqlalchemy import select, update
            from models.auth.user import User
            from models.finance.account import Account
            from dal.database import DatabaseEngine
            
            amount = Decimal(amount_str)
            if amount <= 0:
                return self.error("金额必须大于0")
            
            db_engine = DatabaseEngine()
            async with db_engine.get_session() as session:
                # 查找用户
                user_result = await session.execute(select(User).filter_by(username=username))
                user = user_result.scalars().first()
                if not user:
                    return self.error(f"用户 '{username}' 不存在")
                
                # 查找用户的JCC账户
                account_result = await session.execute(
                    select(Account).filter_by(user_id=user.user_id, currency_code='JCC')
                )
                account = account_result.scalars().first()
                if not account:
                    return self.error(f"用户 '{username}' 没有JCC账户")
                
                # 增加余额
                old_balance = account.balance
                new_balance = old_balance + amount
                
                await session.execute(
                    update(Account)
                    .where(Account.account_id == account.account_id)
                    .values(balance=new_balance, available_balance=new_balance)
                )
                await session.commit()
                
                return self.success(
                    f"✅ 已为用户 '{username}' 增加 {amount} JCC\n"
                    f"原余额: {old_balance} JCC\n"
                    f"新余额: {new_balance} JCC"
                )
                
        except ValueError:
            return self.error("无效的金额格式")
        except Exception as e:
            return self.error(f"增加用户资金失败: {str(e)}")
    
    async def _subtract_user_money(self, username: str, amount_str: str, context: CommandContext) -> CommandResult:
        """扣除用户资金"""
        try:
            from decimal import Decimal
            from sqlalchemy import select, update
            from models.auth.user import User
            from models.finance.account import Account
            from dal.database import DatabaseEngine
            
            amount = Decimal(amount_str)
            if amount <= 0:
                return self.error("金额必须大于0")
            
            db_engine = DatabaseEngine()
            async with db_engine.get_session() as session:
                # 查找用户
                user_result = await session.execute(select(User).filter_by(username=username))
                user = user_result.scalars().first()
                if not user:
                    return self.error(f"用户 '{username}' 不存在")
                
                # 查找用户的JCC账户
                account_result = await session.execute(
                    select(Account).filter_by(user_id=user.user_id, currency_code='JCC')
                )
                account = account_result.scalars().first()
                if not account:
                    return self.error(f"用户 '{username}' 没有JCC账户")
                
                # 检查余额是否足够
                old_balance = account.balance
                if old_balance < amount:
                    return self.error(f"用户余额不足。当前余额: {old_balance} JCC，尝试扣除: {amount} JCC")
                
                # 扣除余额
                new_balance = old_balance - amount
                
                await session.execute(
                    update(Account)
                    .where(Account.account_id == account.account_id)
                    .values(balance=new_balance, available_balance=new_balance)
                )
                await session.commit()
                
                return self.success(
                    f"✅ 已从用户 '{username}' 扣除 {amount} JCC\n"
                    f"原余额: {old_balance} JCC\n"
                    f"新余额: {new_balance} JCC"
                )
                
        except ValueError:
            return self.error("无效的金额格式")
        except Exception as e:
            return self.error(f"扣除用户资金失败: {str(e)}")
    
    async def _set_user_money(self, username: str, amount_str: str, context: CommandContext) -> CommandResult:
        """设置用户资金"""
        try:
            from decimal import Decimal
            from sqlalchemy import select, update
            from models.auth.user import User
            from models.finance.account import Account
            from dal.database import DatabaseEngine
            
            amount = Decimal(amount_str)
            if amount < 0:
                return self.error("金额不能为负数")
            
            db_engine = DatabaseEngine()
            async with db_engine.get_session() as session:
                # 查找用户
                user_result = await session.execute(select(User).filter_by(username=username))
                user = user_result.scalars().first()
                if not user:
                    return self.error(f"用户 '{username}' 不存在")
                
                # 查找用户的JCC账户
                account_result = await session.execute(
                    select(Account).filter_by(user_id=user.user_id, currency_code='JCC')
                )
                account = account_result.scalars().first()
                if not account:
                    return self.error(f"用户 '{username}' 没有JCC账户")
                
                # 设置余额
                old_balance = account.balance
                
                await session.execute(
                    update(Account)
                    .where(Account.account_id == account.account_id)
                    .values(balance=amount, available_balance=amount)
                )
                await session.commit()
                
                return self.success(
                    f"✅ 已设置用户 '{username}' 余额为 {amount} JCC\n"
                    f"原余额: {old_balance} JCC\n"
                    f"新余额: {amount} JCC"
                )
                
        except ValueError:
            return self.error("无效的金额格式")
        except Exception as e:
            return self.error(f"设置用户资金失败: {str(e)}")
    
    async def _get_user_money_info(self, username: str, context: CommandContext) -> CommandResult:
        """查看用户资金信息"""
        try:
            from sqlalchemy import select
            from models.auth.user import User
            from models.finance.account import Account
            from models.bank.bank_account import BankAccount
            from dal.database import DatabaseEngine
            
            db_engine = DatabaseEngine()
            async with db_engine.get_session() as session:
                # 查找用户
                user_result = await session.execute(select(User).filter_by(username=username))
                user = user_result.scalars().first()
                if not user:
                    return self.error(f"用户 '{username}' 不存在")
                
                # 查找用户的所有账户
                accounts_result = await session.execute(
                    select(Account).filter_by(user_id=user.user_id)
                )
                accounts = accounts_result.scalars().all()
                
                # 查找用户的银行账户
                bank_accounts_result = await session.execute(
                    select(BankAccount).filter_by(user_id=user.user_id)
                )
                bank_accounts = bank_accounts_result.scalars().all()
                
                info_text = f"💰 用户 '{username}' 资金信息:\n\n"
                
                if accounts:
                    info_text += "📊 账户余额:\n"
                    total_balance = 0
                    for account in accounts:
                        info_text += f"  • {account.currency_code}: {account.balance}\n"
                        if account.currency_code == 'JCC':
                            total_balance += float(account.balance)
                    info_text += f"\n💎 总资产 (JCC): {total_balance}\n\n"
                else:
                    info_text += "❌ 用户没有任何账户\n\n"
                
                if bank_accounts:
                    info_text += "🏦 银行账户:\n"
                    for bank_account in bank_accounts:
                        info_text += f"  • 账户号: {bank_account.account_number}\n"
                        info_text += f"    余额: {bank_account.balance} {bank_account.currency_id}\n"
                        info_text += f"    状态: {bank_account.status}\n"
                else:
                    info_text += "❌ 用户没有银行账户\n"
                
                return self.success(info_text)
                
        except Exception as e:
            return self.error(f"获取用户资金信息失败: {str(e)}")