# -*- coding: utf-8 -*-
"""
数据库初始化脚本

创建所有必要的数据库表和初始数据。
"""

import asyncio
from datetime import datetime
from sqlalchemy import text
from dal.database import DatabaseEngine
from models import Base, User, Role, Permission
from models.auth import user_roles, role_permissions
from config.settings import Settings
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text


class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self):
        self.settings = Settings()
        self.db_engine = DatabaseEngine(self.settings)
        self.console = Console()
    
    async def initialize(self):
        """初始化数据库"""
        self.console.print(Panel(
            Text("🗄️ 正在初始化数据库...", style="bold blue"),
            title="数据库初始化",
            border_style="blue"
        ))
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                
                # 1. 初始化数据库引擎
                task1 = progress.add_task("初始化数据库引擎...", total=None)
                await self.db_engine.initialize()
                progress.update(task1, description="✅ 数据库引擎已初始化")
                
                # 2. 创建所有表
                task2 = progress.add_task("创建数据库表...", total=None)
                await self._create_tables()
                progress.update(task2, description="✅ 数据库表已创建")
                
                # 3. 创建默认权限
                task3 = progress.add_task("创建默认权限...", total=None)
                await self._create_default_permissions()
                progress.update(task3, description="✅ 默认权限已创建")
                
                # 4. 创建默认角色
                task4 = progress.add_task("创建默认角色...", total=None)
                await self._create_default_roles()
                progress.update(task4, description="✅ 默认角色已创建")
                
                # 5. 创建管理员用户
                task5 = progress.add_task("创建管理员用户...", total=None)
                admin_created = await self._create_admin_user()
                if admin_created:
                    progress.update(task5, description="✅ 管理员用户已创建")
                else:
                    progress.update(task5, description="ℹ️ 管理员用户已存在")
                
                # 6. 验证数据库
                task6 = progress.add_task("验证数据库完整性...", total=None)
                await self._verify_database()
                progress.update(task6, description="✅ 数据库验证完成")
            
            self.console.print(Panel(
                Text("🎉 数据库初始化完成！", style="bold green"),
                title="初始化成功",
                border_style="green"
            ))
            
            return True
            
        except Exception as e:
            self.console.print(Panel(
                Text(f"❌ 数据库初始化失败: {str(e)}", style="bold red"),
                title="初始化失败",
                border_style="red"
            ))
            return False
        
        finally:
            await self.db_engine.close()
    
    async def _create_tables(self):
        """创建所有数据库表"""
        # 使用 SQLAlchemy 的 metadata.create_all
        def create_tables_sync():
            Base.metadata.create_all(bind=self.db_engine.engine)
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, create_tables_sync)
    
    async def _create_default_permissions(self):
        """创建默认权限"""
        with self.db_engine.get_session() as session:
            # 检查是否已有权限
            result = session.execute(text("SELECT COUNT(*) FROM permissions"))
            count = result.scalar()
            
            if count > 0:
                return  # 权限已存在
            
            # 创建系统默认权限
            permissions = Permission.create_system_defaults()
            
            for perm in permissions:
                session.add(perm)
            
            session.commit()
    
    async def _create_default_roles(self):
        """创建默认角色"""
        with self.db_engine.get_session() as session:
            # 检查是否已有角色
            result = session.execute(text("SELECT COUNT(*) FROM roles"))
            count = result.scalar()
            
            if count > 0:
                return  # 角色已存在
            
            # 创建系统默认角色
            roles = Role.create_system_defaults()
            
            for role in roles:
                session.add(role)
            
            session.commit()
            
            # 为角色分配权限
            await self._assign_role_permissions(session)
    
    async def _assign_role_permissions(self, session):
        """为角色分配权限"""
        # 获取所有角色和权限
        roles_result = session.execute(text("SELECT role_id, name FROM roles"))
        roles = {row[1]: row[0] for row in roles_result.fetchall()}
        
        perms_result = session.execute(text("SELECT permission_id, name FROM permissions"))
        permissions = {row[1]: row[0] for row in perms_result.fetchall()}
        
        # 定义角色权限映射
        role_permission_mapping = {
            'admin': [  # 管理员拥有所有权限
                'system.admin', 'system.manage_users', 'system.manage_roles',
                'system.view_logs', 'content.create', 'content.edit', 'content.delete',
                'content.publish', 'finance.view_all', 'finance.manage',
                'finance.transfer', 'user.profile.edit', 'user.settings.edit'
            ],
            'moderator': [  # 版主权限
                'content.create', 'content.edit', 'content.delete',
                'content.publish', 'user.profile.edit'
            ],
            'user': [  # 普通用户权限
                'content.create', 'user.profile.edit', 'user.settings.edit'
            ],
            'guest': [  # 访客权限（最少）
                'user.profile.view'
            ]
        }
        
        # 插入角色权限关联
        for role_name, perm_names in role_permission_mapping.items():
            if role_name not in roles:
                continue
            
            role_id = roles[role_name]
            
            for perm_name in perm_names:
                if perm_name not in permissions:
                    continue
                
                perm_id = permissions[perm_name]
                
                # 插入关联记录
                session.execute(
                    text("INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :perm_id)"),
                    {"role_id": role_id, "perm_id": perm_id}
                )
        
        session.commit()
    
    async def _create_admin_user(self) -> bool:
        """创建管理员用户
        
        Returns:
            是否创建了新用户
        """
        with self.db_engine.get_session() as session:
            # 检查是否已有管理员用户
            result = session.execute(
                text("SELECT COUNT(*) FROM users WHERE username = 'admin'")
            )
            count = result.scalar()
            
            if count > 0:
                return False  # 管理员已存在
            
            # 创建管理员用户
            from services.auth_service import AuthService
            
            # 创建临时的认证服务实例
            auth_service = AuthService(None, None)  # 这里需要传入实际的依赖
            
            # 生成密码哈希
            password_hash = auth_service._hash_password("admin123")
            
            # 创建用户
            admin_user = User(
                username="admin",
                email="admin@chipsbattle.local",
                password_hash=password_hash,
                display_name="系统管理员",
                is_verified=True,
                is_active=True,
                level=100,
                experience=999999,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            session.add(admin_user)
            session.flush()  # 获取用户ID
            
            # 获取管理员角色ID
            role_result = session.execute(
                text("SELECT role_id FROM roles WHERE name = 'admin'")
            )
            admin_role_id = role_result.scalar()
            
            if admin_role_id:
                # 为管理员分配管理员角色
                session.execute(
                    text("INSERT INTO user_roles (user_id, role_id, assigned_at) VALUES (:user_id, :role_id, :assigned_at)"),
                    {"user_id": admin_user.user_id, "role_id": admin_role_id, "assigned_at": datetime.now()}
                )
            
            session.commit()
            
            self.console.print(f"[green]✅ 管理员用户已创建[/green]")
            self.console.print(f"[yellow]   用户名: admin[/yellow]")
            self.console.print(f"[yellow]   密码: admin123[/yellow]")
            self.console.print(f"[red]   ⚠️ 请在首次登录后立即更改密码！[/red]")
            
            return True
    
    async def _verify_database(self):
        """验证数据库完整性"""
        with self.db_engine.get_session() as session:
            # 检查表是否存在
            tables_to_check = ['users', 'roles', 'permissions', 'user_roles', 'role_permissions']
            
            for table in tables_to_check:
                result = session.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                )
                count = result.scalar()
                self.console.print(f"[dim]   {table}: {count} 条记录[/dim]")
            
            # 验证外键关系
            # 这里可以添加更多的完整性检查
    
    async def reset_database(self):
        """重置数据库（删除所有表并重新创建）"""
        self.console.print(Panel(
            Text("⚠️ 正在重置数据库...", style="bold red"),
            title="数据库重置",
            border_style="red"
        ))
        
        try:
            await self.db_engine.initialize()
            
            # 删除所有表
            def drop_tables_sync():
                Base.metadata.drop_all(bind=self.db_engine.engine)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, drop_tables_sync)
            
            self.console.print("[yellow]🗑️ 所有表已删除[/yellow]")
            
            # 重新初始化
            success = await self.initialize()
            
            if success:
                self.console.print(Panel(
                    Text("🎉 数据库重置完成！", style="bold green"),
                    title="重置成功",
                    border_style="green"
                ))
            
            return success
            
        except Exception as e:
            self.console.print(Panel(
                Text(f"❌ 数据库重置失败: {str(e)}", style="bold red"),
                title="重置失败",
                border_style="red"
            ))
            return False
        
        finally:
            await self.db_engine.close()


async def main():
    """主函数"""
    import sys
    
    initializer = DatabaseInitializer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        # 重置数据库
        success = await initializer.reset_database()
    else:
        # 正常初始化
        success = await initializer.initialize()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())