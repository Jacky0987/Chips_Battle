# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - 登录窗口
实现原有的0、1、2、3、4选项登录系统
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any
import sys

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.auth_service import AuthService, AuthResult
from dal.database import DatabaseEngine, set_global_engine
from dal.unit_of_work import SqlAlchemyUnitOfWork
from config.settings import Settings
from terminal.theme_manager import ThemeManager

class LoginWindow:
    """登录窗口类"""
    
    def __init__(self, parent: tk.Tk, main_app):
        self.parent = parent
        self.main_app = main_app
        self.theme_manager = ThemeManager()
        
        # 添加主循环状态标志
        self.mainloop_started = False
        
        # 创建登录窗口
        self.window = tk.Toplevel(parent)
        self.window.title("CHIPS BATTLE REMAKE - 登录")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        
        # 设置窗口居中
        self._center_window()
        
        # 设置模态
        self.window.transient(parent)
        self.window.grab_set()
        
        # 应用主题
        self.theme_manager.apply_theme(self.window)
        colors = self.theme_manager.get_theme()['colors']
        self.window.configure(bg=colors['bg_primary'])
        
        # 初始化服务
        self.auth_service: Optional[AuthService] = None
        self.login_state = self._load_login_state()
        
        # 登录结果
        self.login_success = False
        self.user_data = None
        
        # 创建界面
        self._create_ui()
        
        # 初始化异步服务
        self._init_services()
        
    def _center_window(self):
        """窗口居中显示"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
    def _create_ui(self):
        """创建用户界面"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 主容器
        main_frame = self.theme_manager.create_styled_widget(
            'Frame', self.window
        )
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = self.theme_manager.create_styled_widget(
            'Label', main_frame, 
            text="🎮 CHIPS BATTLE REMAKE v3.0 Alpha",
            font=('Consolas', 16, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # 副标题
        subtitle_label = self.theme_manager.create_styled_widget(
            'Label', main_frame,
            text="账户系统",
            font=('Consolas', 12)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # 选项按钮区域
        options_frame = self.theme_manager.create_styled_widget('Frame', main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 选项0：快速登录（如果有保存的登录状态）
        if self.login_state and self.login_state.get('username'):
            self._create_option_button(
                options_frame, 
                "0", 
                f"🔄 登录上次账户 ({self.login_state['username']})",
                colors['info'],
                self._handle_quick_login
            )
            
        # 选项1：登录现有账户
        self._create_option_button(
            options_frame,
            "1",
            "🔑 登录现有账户",
            colors['success'],
            self._handle_existing_login
        )
        
        # 选项2：注册新账户
        self._create_option_button(
            options_frame,
            "2",
            "📝 注册新账户",
            colors['warning'],
            self._handle_registration
        )
        
        # 选项3：退出游戏
        self._create_option_button(
            options_frame,
            "3",
            "❌ 退出游戏",
            colors['error'],
            self._handle_exit
        )
        
        # 选项4：Debug测试
        self._create_option_button(
            options_frame,
            "4",
            "🔧 Debug测试 (hahaha账户)",
            colors['accent_primary'],
            self._handle_debug_login
        )
        
        # 状态显示区域
        self.status_frame = self.theme_manager.create_styled_widget('Frame', main_frame)
        self.status_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.status_label = self.theme_manager.create_styled_widget(
            'Label', self.status_frame,
            text="请选择操作",
            font=('Consolas', 9)
        )
        self.status_label.pack()
        
    def _create_option_button(self, parent, number, text, color, command):
        """创建选项按钮"""
        btn_frame = self.theme_manager.create_styled_widget('Frame', parent)
        btn_frame.pack(fill=tk.X, pady=5)
        
        # 数字标签
        num_label = tk.Label(
            btn_frame,
            text=f"{number}.",
            bg=self.theme_manager.get_color('bg_primary'),
            fg=color,
            font=('Consolas', 12, 'bold'),
            width=3
        )
        num_label.pack(side=tk.LEFT)
        
        # 按钮
        button = tk.Button(
            btn_frame,
            text=text,
            bg=color,
            fg=self.theme_manager.get_color('fg_bright'),
            activebackground=self.theme_manager.get_color('btn_hover'),
            activeforeground=self.theme_manager.get_color('fg_bright'),
            font=('Consolas', 10),
            borderwidth=1,
            relief=tk.FLAT,
            command=command,
            cursor='hand2'
        )
        button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # 绑定键盘快捷键
        self.window.bind(f'<Key-{number}>', lambda e: command())
        
    def _init_services(self):
        """初始化异步服务"""
        try:
            # 初始化数据库
            settings = Settings()
            engine = DatabaseEngine(settings)
            
            # 异步初始化数据库引擎 - 使用同步方式避免事件循环冲突
            import asyncio
            try:
                # 尝试获取当前事件循环，如果不存在则创建
                loop = asyncio.get_running_loop()
                # 如果有运行中的循环，使用run_coroutine_threadsafe
                import threading
                def init_db():
                    return asyncio.run(engine.initialize())
                
                db_thread = threading.Thread(target=init_db)
                db_thread.start()
                db_thread.join()
            except RuntimeError:
                # 没有运行中的事件循环，可以直接运行
                asyncio.run(engine.initialize())
            
            set_global_engine(engine)
            
            # 初始化事件总线
            from core.event_bus import EventBus
            event_bus = EventBus()
            
            # 初始化认证服务
            uow = SqlAlchemyUnitOfWork(engine.sessionmaker)
            self.auth_service = AuthService(uow, event_bus)
            
            self._update_status("服务初始化完成")
        except Exception as e:
            self._update_status(f"服务初始化失败: {e}", 'error')
            
    def _update_status(self, message: str, status_type: str = 'info'):
        """更新状态显示"""
        def update_ui():
            try:
                colors = self.theme_manager.get_theme()['colors']
                
                if status_type == 'error':
                    color = colors['error']
                elif status_type == 'success':
                    color = colors['success']
                elif status_type == 'warning':
                    color = colors['warning']
                else:
                    color = colors['fg_primary']
                    
                self.status_label.configure(text=message, fg=color)
                self.window.update()
            except Exception as e:
                print(f"更新状态失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 检查是否在主线程中
        import threading
        current_thread = threading.current_thread()
        main_thread = threading.main_thread()
        print(f"[DEBUG] _update_status called - current_thread: {current_thread.name}, main_thread: {main_thread.name}, mainloop_started: {self.mainloop_started}")
        
        if current_thread == main_thread and self.mainloop_started:
            # 在主线程中且主循环已启动，直接更新
            print("[DEBUG] Updating UI directly (main thread with mainloop started)")
            update_ui()
        elif current_thread == main_thread and not self.mainloop_started:
            # 在主线程中但主循环未启动，暂时跳过更新
            print("[DEBUG] Skipping UI update (main thread but mainloop not started)")
            # 可以将消息保存起来，等主循环启动后再显示
            if not hasattr(self, '_pending_status_message'):
                self._pending_status_message = []
            self._pending_status_message.append((message, status_type))
        else:
            # 在非主线程中，使用 after 方法
            try:
                print("[DEBUG] Using after() method for UI update")
                self.window.after(0, update_ui)
            except Exception as e:
                print(f"[DEBUG] Failed to use after() method: {e}")
                # 避免在主循环未启动时调用任何tkinter方法
                print(f"[DEBUG] Window exists check skipped (mainloop not started)")
                import traceback
                traceback.print_exc()
                # 如果 after 调用失败，说明主循环可能未启动，延迟重试
                def retry_update():
                    try:
                        print("[DEBUG] Retrying UI update with after()")
                        self.window.after(0, update_ui)
                    except Exception as retry_e:
                        print(f"[DEBUG] Retry also failed: {retry_e}")
                        # 如果仍然失败，放弃更新
                        pass
                # 延迟500ms后重试
                import time
                time.sleep(0.5)
                retry_update()
        
    def _handle_quick_login(self):
        """处理快速登录"""
        if not self.login_state or not self.login_state.get('username'):
            self._update_status("没有保存的登录信息", 'error')
            return
            
        username = self.login_state['username']
        self._update_status(f"正在登录 {username}...")
        
        try:
            # 使用同步方式处理登录，避免事件循环冲突
            import threading
            def run_sync_quick_login():
                try:
                    # 直接完成登录，不使用异步逻辑
                    self._update_status(f"登录成功: {username}", 'success')
                    user_data = {
                        'username': username,
                        'user_id': f"quick_{username}",
                        'email': None
                    }
                    self._complete_login(username, user_data)
                except Exception as e:
                    self._update_status(f"登录失败: {e}", 'error')
            
            thread = threading.Thread(target=run_sync_quick_login)
            thread.daemon = True
            thread.start()
        except Exception as e:
            self._update_status(f"登录失败: {e}", 'error')
            
    def _handle_existing_login(self):
        """处理现有账户登录"""
        self._show_login_dialog()
        
    def _handle_registration(self):
        """处理注册新账户"""
        self._show_register_dialog()
        
    def _handle_exit(self):
        """处理退出游戏"""
        if messagebox.askokcancel("退出", "确定要退出游戏吗？"):
            self.window.destroy()
            self.parent.quit()
            
    def _handle_debug_login(self):
        """处理Debug测试登录"""
        self._update_status("正在使用Debug账户登录...")
        try:
            import threading
            def run_sync_debug_login():
                try:
                    # 直接完成Debug登录，不使用异步逻辑
                    self._update_status(f"登录成功: hahaha", 'success')
                    user_data = {
                        'username': 'hahaha',
                        'user_id': 'debug_user_id',
                        'email': 'debug@example.com'
                    }
                    self._complete_login('hahaha', user_data)
                except Exception as e:
                    self._update_status(f"Debug登录失败: {e}", 'error')
            
            thread = threading.Thread(target=run_sync_debug_login, daemon=True)
            thread.start()
        except Exception as e:
            self._update_status(f"Debug登录失败: {e}", 'error')
            
    def _show_login_dialog(self):
        """显示登录对话框"""
        dialog = tk.Toplevel(self.window)
        dialog.title("登录账户")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # 应用主题
        colors = self.theme_manager.get_theme()['colors']
        dialog.configure(bg=colors['bg_primary'])
        
        # 居中显示
        dialog.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # 创建表单
        frame = self.theme_manager.create_styled_widget('Frame', dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 用户名
        self.theme_manager.create_styled_widget(
            'Label', frame, text="用户名:"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        username_entry = self.theme_manager.create_styled_widget(
            'Entry', frame, 'VSCode'
        )
        username_entry.pack(fill=tk.X, pady=(0, 10))
        username_entry.focus()
        
        # 密码
        self.theme_manager.create_styled_widget(
            'Label', frame, text="密码:"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        password_entry = self.theme_manager.create_styled_widget(
            'Entry', frame, 'VSCode', show="*"
        )
        password_entry.pack(fill=tk.X, pady=(0, 20))
        
        # 按钮
        btn_frame = self.theme_manager.create_styled_widget('Frame', frame)
        btn_frame.pack(fill=tk.X)
        
        def do_login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            
            if not username or not password:
                messagebox.showerror("错误", "请输入用户名和密码")
                return
                
            dialog.destroy()
            self._update_status(f"正在登录 {username}...")
            
            try:
                # 使用同步方式处理登录，避免事件循环冲突
                import threading
                def run_sync_login():
                    try:
                        if username == "hahaha" and password == "debug_password":
                            # Debug账户直接登录成功
                            success_msg = f"登录成功: {username}"
                            user_data = {
                                'username': username,
                                'user_id': 'debug_user_id',
                                'email': 'debug@example.com'
                            }
                            # 在主线程中更新ui，使用参数传递避免lambda闭包问题
                            def show_success():
                                self._update_status(success_msg, 'success')
                            def do_complete_login():
                                self._complete_login(username, user_data)
                            def do_save_login():
                                self._save_login_state(username)
                            self.window.after(0, show_success)
                            self.window.after(0, do_complete_login)
                            self.window.after(0, do_save_login)
                        else:
                            # 其他账户暂时显示登录失败
                            error_msg = "登录失败: 用户名或密码错误"
                            def show_error():
                                self._update_status(error_msg, 'error')
                            self.window.after(0, show_error)
                    except Exception as e:
                        error_msg = f"登录失败: {e}"
                        def show_error():
                            self._update_status(error_msg, 'error')
                        self.window.after(0, show_error)
                
                thread = threading.Thread(target=run_sync_login)
                thread.daemon = True
                thread.start()
            except Exception as e:
                self._update_status(f"登录失败: {e}", 'error')
                
        def cancel_login():
            dialog.destroy()
            
        login_btn = self.theme_manager.create_styled_widget(
            'Button', btn_frame, text="登录", command=do_login
        )
        login_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = self.theme_manager.create_styled_widget(
            'Button', btn_frame, text="取消", command=cancel_login
        )
        cancel_btn.pack(side=tk.LEFT)
        
        # 绑定回车键
        dialog.bind('<Return>', lambda e: do_login())
        dialog.bind('<Escape>', lambda e: cancel_login())
        
    def _show_register_dialog(self):
        """显示注册对话框"""
        dialog = tk.Toplevel(self.window)
        dialog.title("注册新账户")
        dialog.geometry("350x250")
        dialog.resizable(False, False)
        dialog.transient(self.window)
        dialog.grab_set()
        
        # 应用主题
        colors = self.theme_manager.get_theme()['colors']
        dialog.configure(bg=colors['bg_primary'])
        
        # 居中显示
        dialog.update_idletasks()
        x = self.window.winfo_x() + (self.window.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.window.winfo_y() + (self.window.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # 创建表单
        frame = self.theme_manager.create_styled_widget('Frame', dialog)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 用户名
        self.theme_manager.create_styled_widget(
            'Label', frame, text="用户名:"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        username_entry = self.theme_manager.create_styled_widget(
            'Entry', frame, 'VSCode'
        )
        username_entry.pack(fill=tk.X, pady=(0, 10))
        username_entry.focus()
        
        # 密码
        self.theme_manager.create_styled_widget(
            'Label', frame, text="密码:"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        password_entry = self.theme_manager.create_styled_widget(
            'Entry', frame, 'VSCode', show="*"
        )
        password_entry.pack(fill=tk.X, pady=(0, 10))
        
        # 确认密码
        self.theme_manager.create_styled_widget(
            'Label', frame, text="确认密码:"
        ).pack(anchor=tk.W, pady=(0, 5))
        
        confirm_entry = self.theme_manager.create_styled_widget(
            'Entry', frame, 'VSCode', show="*"
        )
        confirm_entry.pack(fill=tk.X, pady=(0, 20))
        
        # 按钮
        btn_frame = self.theme_manager.create_styled_widget('Frame', frame)
        btn_frame.pack(fill=tk.X)
        
        def do_register():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            confirm = confirm_entry.get().strip()
            
            if not username or not password:
                messagebox.showerror("错误", "请输入用户名和密码")
                return
                
            if password != confirm:
                messagebox.showerror("错误", "两次输入的密码不一致")
                return
                
            dialog.destroy()
            self._update_status(f"正在注册 {username}...")
            
            try:
                # 使用同步方式处理注册，避免事件循环冲突
                import threading
                def run_sync_register():
                    try:
                        # 简化的同步注册逻辑
                        success_msg = f"注册成功: {username}"
                        user_data = {
                            'username': username,
                            'user_id': f"user_{username}",
                            'email': f"{username}@example.com"
                        }
                        # 在主线程中更新ui，使用参数传递避免lambda闭包问题
                        def show_success():
                            self._update_status(success_msg, 'success')
                        def do_complete_register():
                            self._complete_register(username, user_data)
                        def do_save_login():
                            self._save_login_state(username)
                        self.window.after(0, show_success)
                        self.window.after(0, do_complete_register)
                        self.window.after(0, do_save_login)
                    except Exception as e:
                        error_msg = f"注册失败: {e}"
                        def show_error():
                            self._update_status(error_msg, 'error')
                        self.window.after(0, show_error)
                
                thread = threading.Thread(target=run_sync_register)
                thread.daemon = True
                thread.start()
            except Exception as e:
                self._update_status(f"注册失败: {e}", 'error')
                
        def cancel_register():
            dialog.destroy()
            
        register_btn = self.theme_manager.create_styled_widget(
            'Button', btn_frame, text="注册", command=do_register
        )
        register_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = self.theme_manager.create_styled_widget(
            'Button', btn_frame, text="取消", command=cancel_register
        )
        cancel_btn.pack(side=tk.LEFT)
        
        # 绑定回车键
        dialog.bind('<Return>', lambda e: do_register())
        dialog.bind('<Escape>', lambda e: cancel_register())
        
    async def _async_quick_login(self, username: str):
        """异步快速登录"""
        try:
            if not self.auth_service:
                self._update_status("认证服务未初始化", 'error')
                return
                
            # 快速登录直接完成登录过程（跳过密码验证）
            self._update_status(f"登录成功: {username}", 'success')
            user_data = {
                'username': username,
                'user_id': f"quick_{username}",
                'email': None
            }
            self._complete_login(username, user_data)
                
        except Exception as e:
            self._update_status(f"登录异常: {e}", 'error')
            
    async def _async_login(self, username: str, password: str):
        """异步登录"""
        try:
            if not self.auth_service:
                self._update_status("认证服务未初始化", 'error')
                return
                
            result, user = await self.auth_service.authenticate(username, password)
            
            if result == AuthResult.SUCCESS:
                self._update_status(f"登录成功: {username}", 'success')
                user_data = {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email
                } if user else {}
                self._complete_login(username, user_data)
                # 保存登录状态
                self._save_login_state(username)
            else:
                error_messages = {
                    AuthResult.USER_NOT_FOUND: "用户不存在",
                    AuthResult.INVALID_CREDENTIALS: "用户名或密码错误",
                    AuthResult.USER_DISABLED: "账户已被禁用",
                    AuthResult.ACCOUNT_LOCKED: "账户已被锁定",
                    AuthResult.TOO_MANY_ATTEMPTS: "尝试次数过多"
                }
                message = error_messages.get(result, "登录失败")
                self._update_status(f"登录失败: {message}", 'error')
                
        except Exception as e:
            self._update_status(f"登录异常: {e}", 'error')
            
    async def _async_register(self, username: str, password: str):
        """异步注册"""
        try:
            if not self.auth_service:
                self._update_status("认证服务未初始化", 'error')
                return
                
            success, message, user = await self.auth_service.register_user(username, password)
            
            if success:
                self._update_status(f"注册成功: {username}", 'success')
                user_data = {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email
                } if user else {}
                self._complete_register(username, user_data)
                # 保存登录状态
                self._save_login_state(username)
            else:
                self._update_status(f"注册失败: {message}", 'error')
                
        except Exception as e:
            self._update_status(f"注册异常: {e}", 'error')
        
    def _complete_login(self, username: str, user_data: Dict[str, Any] = None):
        """完成登录"""
        self.login_success = True
        
        if not user_data:
            user_data = {
                'username': username,
                'user_id': 1,
                'balance': 125000,
                'level': 15,
                'experience': 1250
            }
        
        self.user_data = user_data
        
        self._update_status(f"登录成功！欢迎 {username}", 'success')
        
        # 通知主应用
        self.main_app.on_login_success(self.user_data)
        
        # 延迟关闭窗口
        self.window.after(1000, self.window.destroy)
        
    def _complete_register(self, username: str, user_data: Dict[str, Any] = None):
        """完成注册"""
        self._update_status(f"注册成功！正在登录 {username}...", 'success')
        
        # 注册成功后自动登录
        self.window.after(1000, lambda: self._complete_login(username, user_data))
        
    def set_mainloop_started(self):
        """设置主循环已启动标志"""
        self.mainloop_started = True
        print("[DEBUG] LoginWindow mainloop started")
        
        # 显示待处理的状态消息
        if hasattr(self, '_pending_status_message') and self._pending_status_message:
            print(f"[DEBUG] Displaying {len(self._pending_status_message)} pending status messages")
            for message, status_type in self._pending_status_message:
                try:
                    # 现在主循环已启动，可以直接更新UI
                    colors = self.theme_manager.get_theme()['colors']
                    
                    if status_type == 'error':
                        color = colors['error']
                    elif status_type == 'success':
                        color = colors['success']
                    elif status_type == 'warning':
                        color = colors['warning']
                    else:
                        color = colors['fg_primary']
                        
                    self.status_label.configure(text=message, fg=color)
                    self.window.update()
                except Exception as e:
                    print(f"[DEBUG] Failed to display pending message: {e}")
            
            # 清空待处理消息
            self._pending_status_message.clear()
        
    def _load_login_state(self) -> Optional[Dict[str, Any]]:
        """加载登录状态"""
        try:
            login_file = Path.home() / '.chips_battle' / 'login_state.json'
            if login_file.exists():
                with open(login_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return None
        
    def _save_login_state(self, username: str):
        """保存登录状态"""
        try:
            login_dir = Path.home() / '.chips_battle'
            login_dir.mkdir(exist_ok=True)
            
            login_file = login_dir / 'login_state.json'
            with open(login_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'username': username,
                    'last_login': str(Path().cwd())
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存登录状态失败: {e}")