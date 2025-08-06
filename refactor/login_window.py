import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from datetime import datetime

class LoginWindow:
    def __init__(self, user_manager, callback):
        self.user_manager = user_manager
        self.callback = callback
        self.window = None
        
    def start_bash_login(self, main_gui):
        """在主界面中启动bash样式登录"""
        self.main_gui = main_gui
        self.login_attempts = 0
        self.max_attempts = 10
        self.current_mode = "login"  # login, register, forgot_password
        self.is_login_active = True  # 标记登录状态
        
        # 清屏并显示登录界面
        self.main_gui.clear_screen()
        self.show_login_prompt()

        # 先解绑可能存在的事件，然后绑定新事件
        try:
            self.main_gui.command_entry.unbind('<Return>')
        except:
            pass
        self.main_gui.command_entry.bind('<Return>', self.handle_login_input)
        
    def show_login_prompt(self):
        """显示bash样式的登录提示"""
        login_banner = f"""
══════════════════════════════════════════════════════════════════════════════════════════
                          🏦 JackyCoin 股票交易模拟系统 🏦                               
                                 登录到您的交易账户                                       
══════════════════════════════════════════════════════════════════════════════════════════

欢迎使用 JackyCoin 交易系统！

登录命令格式:
  login <用户名> <密码>        # 登录账户
  register <用户名> <密码>     # 注册新账户
  exit                        # 退出系统

当前尝试次数: {self.login_attempts}/{self.max_attempts}
"""
        
        self.main_gui.print_to_output(login_banner, '#00FFAA')
        self.main_gui.print_to_output("JackyCoin-Login> ", '#FFFF00', end='')
        
    def handle_login_input(self, event):
        """处理登录输入"""
        # 检查登录是否仍然活跃
        if not hasattr(self, 'is_login_active') or not self.is_login_active:
            return "break"
            
        command = self.main_gui.get_command_input().strip()
        self.main_gui.clear_command_input()
        
        if not command:
            self.main_gui.print_to_output("JackyCoin-Login> ", '#FFFF00', end='')
            return "break"
            
        # 显示用户输入的命令
        self.main_gui.print_to_output(command, '#FFFFFF')
        
        parts = command.split()
        if not parts:
            self.show_error("请输入有效命令")
            return

        cmd = parts[0].lower()
        
        if cmd == "login":
            if len(parts) != 3:
                self.show_error("格式错误！使用: login <用户名> <密码>")
                return
            self.attempt_login(parts[1], parts[2])
            
        elif cmd == "register":
            if len(parts) != 3:
                self.show_error("格式错误！使用: register <用户名> <密码>")
                return
            self.attempt_register(parts[1], parts[2])
            
        elif cmd == "guest":
            self.login_as_guest()
            
        elif cmd == "exit":
            self.main_gui.root.quit()
            
        elif cmd == "help":
            self.show_login_help()
            
        else:
            self.show_error(f"未知命令: {cmd}")
            
    def attempt_login(self, username, password):
        """尝试登录"""
        self.main_gui.print_to_output(f"🔐 正在验证用户 '{username}'...", '#FFAA00')
        
        success, message = self.user_manager.login_user(username, password)
        if success:
            self.main_gui.print_to_output(f"✅ 登录成功！欢迎回来，{username}！", '#00FF00')
            self.main_gui.print_to_output("🔄 正在加载用户数据...", '#00FFAA')
            
            # 标记登录结束并解绑事件处理器
            self.is_login_active = False
            try:
                self.main_gui.command_entry.unbind('<Return>')
            except:
                pass
            
            # 调用登录成功回调
            self.callback()
        else:
            self.login_attempts += 1
            remaining = self.max_attempts - self.login_attempts
            
            if remaining > 0:
                self.main_gui.print_to_output(f"❌ 登录失败！{message}。剩余尝试次数: {remaining}", '#FF6600')
                self.main_gui.print_to_output("JackyCoin-Login> ", '#FFFF00', end='')
            else:
                self.main_gui.print_to_output("🚫 登录尝试次数过多，系统即将退出...", '#FF0000')
                self.main_gui.root.after(3000, self.main_gui.root.quit)
                
    def attempt_register(self, username, password):
        """尝试注册"""
        self.main_gui.print_to_output(f"📝 正在注册用户 '{username}'...", '#FFAA00')
        
        # 验证用户名和密码
        if len(username) < 3:
            self.show_error("用户名至少需要3个字符")
            return

        if len(password) < 6:
            self.show_error("密码至少需要6个字符")
            return

        success, message = self.user_manager.register_user(username, password)
        
        if success:
            self.main_gui.print_to_output(f"✅ {message}", '#00FF00')
            self.main_gui.print_to_output("📊 正在初始化交易账户...", '#00FFAA')
            self.main_gui.print_to_output(f"💰 初始资金: J$100,000", '#FFFF00')
            
            # 自动登录新注册的用户
            login_success, login_message = self.user_manager.login_user(username, password)
            if login_success:
                self.is_login_active = False
                try:
                    self.main_gui.command_entry.unbind('<Return>')
                except:
                    pass
                self.callback()
            else:
                self.show_error(f"自动登录失败: {login_message}")
        else:
            self.show_error(message)
            
    def login_as_guest(self):
        """游客模式登录"""
        self.main_gui.print_to_output("👤 正在以游客模式登录...", '#FFAA00')
        self.main_gui.print_to_output("⚠️  游客模式功能受限，无法保存数据", '#FF6600')
        
        # 创建临时游客账户
        import uuid
        guest_id = f"guest_{str(uuid.uuid4())[:8]}"
        
        register_success, register_message = self.user_manager.register_user(guest_id, "guest123", email="guest@temp.com")
        if register_success:
            login_success, login_message = self.user_manager.login_user(guest_id, "guest123")
            if login_success:
                self.is_login_active = False
                try:
                    self.main_gui.command_entry.unbind('<Return>')
                except:
                    pass
                self.callback()
            else:
                self.show_error(f"游客模式登录失败: {login_message}")
        else:
            self.show_error(f"游客模式创建失败: {register_message}")
            
    def show_error(self, message):
        """显示错误信息"""
        self.main_gui.print_to_output(f"❌ {message}", '#FF0000')
        self.main_gui.print_to_output("JackyCoin-Login> ", '#FFFF00', end='')
        
    def show_login_help(self):
        """显示登录帮助"""
        help_text = """
📚 JackyCoin 登录系统帮助

可用命令:
  login <用户名> <密码>     登录到现有账户
  register <用户名> <密码>  注册新的交易账户
  guest                    以游客模式登录 (数据不保存)
  help                     显示此帮助信息
  exit                     退出系统

示例:
  login trader123 mypassword
  register newuser password123
  
📝 注册要求:
  • 用户名至少3个字符
  • 密码至少6个字符
  • 每个用户名只能注册一次

💡 提示:
  • 忘记密码请联系管理员
  • 游客模式下无法保存交易数据
  • 系统支持中文用户名
"""
        self.main_gui.print_to_output(help_text, '#AAFFFF')
        self.main_gui.print_to_output("JackyCoin-Login> ", '#FFFF00', end='')

class AdminLogin:
    """管理员bash样式验证"""
    
    def __init__(self, main_gui):
        self.main_gui = main_gui
        self.admin_password = "admin"
        self.attempts = 0
        self.max_attempts = 3
        
    def start_admin_verification(self, callback):
        """启动管理员验证"""
        self.callback = callback
        self.attempts = 0
        
        self.main_gui.print_to_output("""
══════════════════════════════════════════════════════════════════════════════════════════
                             🔐 管理员权限验证 🔐                                          
                         请输入管理员密码以继续操作                                        
══════════════════════════════════════════════════════════════════════════════════════════

⚠️  警告: 管理员操作可能影响系统稳定性和用户数据
🔒 系统将记录所有管理员操作日志

请输入管理员密码:""", '#FF6600')
        
        self.main_gui.print_to_output("Admin-Verify> ", '#FF0000', end='')
        self.main_gui.command_entry.bind('<Return>', self.handle_admin_input)
        
    def handle_admin_input(self, event):
        """处理管理员密码输入"""
        password = self.main_gui.get_command_input().strip()
        self.main_gui.clear_command_input()
        
        if not password:
            self.main_gui.print_to_output("Admin-Verify> ", '#FF0000', end='')
            return
            
        # 显示加密的密码
        self.main_gui.print_to_output("*" * len(password), '#FFFF00')
        
        if password == self.admin_password:
            self.main_gui.print_to_output("✅ 管理员验证成功！", '#00FF00')
            self.main_gui.print_to_output("🔓 已获得管理员权限，请谨慎操作", '#FFAA00')
            
            # 记录管理员登录
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.main_gui.print_to_output(f"📝 管理员登录时间: {timestamp}", '#AAAAAA')
            
            # 解绑当前的admin验证事件处理器
            try:
                self.main_gui.command_entry.unbind('<Return>')
            except:
                pass
            
            # 调用成功回调
            self.callback()
            
            # 重新绑定正常的命令处理事件
            self.main_gui.command_entry.bind('<Return>', self.main_gui.app.process_command)
        else:
            self.attempts += 1
            remaining = self.max_attempts - self.attempts
            
            if remaining > 0:
                self.main_gui.print_to_output(f"❌ 密码错误！剩余尝试次数: {remaining}", '#FF0000')
                self.main_gui.print_to_output("Admin-Verify> ", '#FF0000', end='')
            else:
                self.main_gui.print_to_output("🚫 管理员验证失败次数过多，已拒绝访问", '#FF0000')
                # 验证失败，恢复正常命令处理
                try:
                    self.main_gui.command_entry.unbind('<Return>')
                except:
                    pass
                self.main_gui.command_entry.bind('<Return>', self.main_gui.app.process_command)
