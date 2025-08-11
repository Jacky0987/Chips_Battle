# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - 状态栏
显示系统状态、连接状态、时间等信息
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
import threading
import time
from typing import Dict, Any, Optional

class StatusBar:
    """状态栏类"""
    
    def __init__(self, parent: tk.Frame, main_app):
        self.parent = parent
        self.main_app = main_app
        self.theme_manager = main_app.theme_manager
        
        # 状态信息
        self.status_info = {
            'connection': 'disconnected',
            'market_status': 'closed',
            'user_status': 'offline',
            'last_update': None,
            'notifications': 0
        }
        
        # 时间更新线程
        self.time_thread = None
        self.time_running = False
        
        # 创建界面
        self._create_ui()
        
        # 延迟启动时间更新，确保在tkinter主循环启动后进行
        self.main_frame.after(100, self._start_time_update)
        
        # 添加主循环状态标志
        self.mainloop_started = False
        
    def _create_ui(self):
        """创建用户界面"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 主容器
        self.main_frame = tk.Frame(
            self.parent,
            bg=colors['bg_secondary'],
            height=25
        )
        self.main_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.main_frame.pack_propagate(False)
        
        # 左侧状态区域
        self._create_left_status()
        
        # 中间信息区域
        self._create_center_info()
        
        # 右侧时间区域
        self._create_right_time()
        
    def _create_left_status(self):
        """创建左侧状态区域"""
        colors = self.theme_manager.get_theme()['colors']
        
        left_frame = tk.Frame(self.main_frame, bg=colors['bg_secondary'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
        
        # 连接状态
        self.connection_frame = tk.Frame(left_frame, bg=colors['bg_secondary'])
        self.connection_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.connection_indicator = tk.Label(
            self.connection_frame,
            text="🔴",
            bg=colors['bg_secondary'],
            fg=colors['error'],
            font=('Segoe UI Symbol', 8)
        )
        self.connection_indicator.pack(side=tk.LEFT, pady=3)
        
        self.connection_label = tk.Label(
            self.connection_frame,
            text="离线",
            bg=colors['bg_secondary'],
            fg=colors['fg_muted'],
            font=('Consolas', 8)
        )
        self.connection_label.pack(side=tk.LEFT, padx=(2, 0), pady=3)
        
        # 市场状态
        self.market_frame = tk.Frame(left_frame, bg=colors['bg_secondary'])
        self.market_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        self.market_indicator = tk.Label(
            self.market_frame,
            text="📊",
            bg=colors['bg_secondary'],
            font=('Segoe UI Symbol', 8)
        )
        self.market_indicator.pack(side=tk.LEFT, pady=3)
        
        self.market_label = tk.Label(
            self.market_frame,
            text="休市",
            bg=colors['bg_secondary'],
            fg=colors['fg_muted'],
            font=('Consolas', 8)
        )
        self.market_label.pack(side=tk.LEFT, padx=(2, 0), pady=3)
        
        # 用户状态
        self.user_frame = tk.Frame(left_frame, bg=colors['bg_secondary'])
        self.user_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        self.user_indicator = tk.Label(
            self.user_frame,
            text="👤",
            bg=colors['bg_secondary'],
            font=('Segoe UI Symbol', 8)
        )
        self.user_indicator.pack(side=tk.LEFT, pady=3)
        
        self.user_label = tk.Label(
            self.user_frame,
            text="未登录",
            bg=colors['bg_secondary'],
            fg=colors['fg_muted'],
            font=('Consolas', 8)
        )
        self.user_label.pack(side=tk.LEFT, padx=(2, 0), pady=3)
        
        # 绑定点击事件
        self._bind_status_clicks()
        
    def _create_center_info(self):
        """创建中间信息区域"""
        colors = self.theme_manager.get_theme()['colors']
        
        center_frame = tk.Frame(self.main_frame, bg=colors['bg_secondary'])
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 系统信息
        self.system_info_label = tk.Label(
            center_frame,
            text="系统就绪 | CPU: 0% | 内存: 0MB",
            bg=colors['bg_secondary'],
            fg=colors['fg_muted'],
            font=('Consolas', 8)
        )
        self.system_info_label.pack(side=tk.LEFT, pady=3, padx=10)
        
        # 通知区域
        self.notification_frame = tk.Frame(center_frame, bg=colors['bg_secondary'])
        self.notification_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        
        self.notification_indicator = tk.Label(
            self.notification_frame,
            text="🔔",
            bg=colors['bg_secondary'],
            font=('Segoe UI Symbol', 8)
        )
        self.notification_indicator.pack(side=tk.LEFT, pady=3)
        
        self.notification_label = tk.Label(
            self.notification_frame,
            text="0",
            bg=colors['bg_secondary'],
            fg=colors['fg_muted'],
            font=('Consolas', 8)
        )
        self.notification_label.pack(side=tk.LEFT, padx=(2, 0), pady=3)
        
        # 绑定通知点击事件
        self.notification_frame.bind('<Button-1>', self._on_notification_click)
        self.notification_indicator.bind('<Button-1>', self._on_notification_click)
        self.notification_label.bind('<Button-1>', self._on_notification_click)
        
    def _create_right_time(self):
        """创建右侧时间区域"""
        colors = self.theme_manager.get_theme()['colors']
        
        right_frame = tk.Frame(self.main_frame, bg=colors['bg_secondary'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5))
        
        # 时间显示
        self.time_label = tk.Label(
            right_frame,
            text="00:00:00",
            bg=colors['bg_secondary'],
            fg=colors['fg_primary'],
            font=('Consolas', 8, 'bold')
        )
        self.time_label.pack(side=tk.RIGHT, pady=3, padx=(10, 0))
        
        # 日期显示
        self.date_label = tk.Label(
            right_frame,
            text="2024-01-01",
            bg=colors['bg_secondary'],
            fg=colors['fg_muted'],
            font=('Consolas', 8)
        )
        self.date_label.pack(side=tk.RIGHT, pady=3)
        
    def _bind_status_clicks(self):
        """绑定状态点击事件"""
        # 连接状态点击
        self.connection_frame.bind('<Button-1>', self._on_connection_click)
        self.connection_indicator.bind('<Button-1>', self._on_connection_click)
        self.connection_label.bind('<Button-1>', self._on_connection_click)
        
        # 市场状态点击
        self.market_frame.bind('<Button-1>', self._on_market_click)
        self.market_indicator.bind('<Button-1>', self._on_market_click)
        self.market_label.bind('<Button-1>', self._on_market_click)
        
        # 用户状态点击
        self.user_frame.bind('<Button-1>', self._on_user_click)
        self.user_indicator.bind('<Button-1>', self._on_user_click)
        self.user_label.bind('<Button-1>', self._on_user_click)
        
    def _start_time_update(self):
        """启动时间更新线程"""
        import threading
        print(f"[DEBUG] _start_time_update called, thread: {threading.current_thread().name}, main thread: {threading.main_thread().name}")
        # 使用after方法确保在主循环启动后再启动线程
        self.main_frame.after(200, self._start_time_thread)
        
    def _start_time_thread(self):
        """实际启动时间更新线程"""
        import threading
        
        # 检查主循环是否已启动
        if not self.mainloop_started:
            print(f"[DEBUG] Mainloop not started yet, delaying thread start")
            # 如果主循环未启动，延迟启动
            self.main_frame.after(500, self._start_time_thread)
            return
            
        print(f"[DEBUG] Starting time update thread")
        self.time_running = True
        self.time_thread = threading.Thread(target=self._time_update_loop, daemon=True)
        self.time_thread.start()
        
    def set_mainloop_started(self):
        """设置主循环已启动标志"""
        import threading
        print(f"[DEBUG] set_mainloop_started called, thread: {threading.current_thread().name}")
        self.mainloop_started = True
        
    def _time_update_loop(self):
        """时间更新循环"""
        print(f"[DEBUG] Time update loop started")
        while self.time_running:
            try:
                current_time = datetime.now()
                time_str = current_time.strftime("%H:%M:%S")
                date_str = current_time.strftime("%Y-%m-%d")
                
                # 在主线程中更新UI，使用默认参数确保捕获正确的值
                self.main_frame.after(0, lambda t=time_str, d=date_str: self._update_time_display(t, d))
                
                time.sleep(1)
                
            except Exception as e:
                import traceback
                print(f"[DEBUG] Exception in time update loop: {e}")
                print(f"时间更新错误: {e}")
                
    def _update_time_display(self, time_str: str, date_str: str):
        """更新时间显示"""
        try:
            self.time_label.configure(text=time_str)
            self.date_label.configure(text=date_str)
        except tk.TclError as e:
            print(f"[DEBUG] TclError in time display update: {e}")
            # 窗口已关闭
            self.time_running = False
        except Exception as e:
            import traceback
            print(f"[DEBUG] Exception in time display update: {e}")
            
    def update_connection_status(self, status: str, details: str = ""):
        """更新连接状态"""
        colors = self.theme_manager.get_theme()['colors']
        
        self.status_info['connection'] = status
        
        if status == 'connected':
            self.connection_indicator.configure(text="🟢", fg=colors['success'])
            self.connection_label.configure(text="在线", fg=colors['success'])
        elif status == 'connecting':
            self.connection_indicator.configure(text="🟡", fg=colors['warning'])
            self.connection_label.configure(text="连接中", fg=colors['warning'])
        else:
            self.connection_indicator.configure(text="🔴", fg=colors['error'])
            self.connection_label.configure(text="离线", fg=colors['error'])
            
        if details:
            self._create_tooltip(self.connection_frame, details)
            
    def update_market_status(self, status: str, details: str = ""):
        """更新市场状态"""
        colors = self.theme_manager.get_theme()['colors']
        
        self.status_info['market_status'] = status
        
        if status == 'open':
            self.market_label.configure(text="开盘", fg=colors['success'])
        elif status == 'pre_market':
            self.market_label.configure(text="盘前", fg=colors['warning'])
        elif status == 'after_market':
            self.market_label.configure(text="盘后", fg=colors['warning'])
        else:
            self.market_label.configure(text="休市", fg=colors['fg_muted'])
            
        if details:
            self._create_tooltip(self.market_frame, details)
            
    def update_user_status(self, username: str = None, status: str = "offline"):
        """更新用户状态"""
        colors = self.theme_manager.get_theme()['colors']
        
        self.status_info['user_status'] = status
        
        if username and status == 'online':
            self.user_label.configure(text=username[:8], fg=colors['success'])
        else:
            self.user_label.configure(text="未登录", fg=colors['fg_muted'])
            
    def update_system_info(self, cpu_usage: float = 0, memory_usage: float = 0, additional_info: str = ""):
        """更新系统信息"""
        info_text = f"系统就绪 | CPU: {cpu_usage:.1f}% | 内存: {memory_usage:.0f}MB"
        
        if additional_info:
            info_text += f" | {additional_info}"
            
        self.system_info_label.configure(text=info_text)
        
    def update_notifications(self, count: int):
        """更新通知数量"""
        colors = self.theme_manager.get_theme()['colors']
        
        self.status_info['notifications'] = count
        self.notification_label.configure(text=str(count))
        
        if count > 0:
            self.notification_label.configure(fg=colors['warning'])
            self.notification_indicator.configure(text="🔔")
        else:
            self.notification_label.configure(fg=colors['fg_muted'])
            self.notification_indicator.configure(text="🔕")
            
    def add_notification(self, message: str, level: str = "info"):
        """添加通知"""
        current_count = self.status_info['notifications']
        self.update_notifications(current_count + 1)
        
        # 在终端显示通知
        if hasattr(self.main_app, 'terminal_panel'):
            tag = 'system'
            if level == 'warning':
                tag = 'warning'
            elif level == 'error':
                tag = 'error'
            elif level == 'success':
                tag = 'success'
                
            self.main_app.terminal_panel.append_output(
                f"📢 通知: {message}",
                tag
            )
            
    def clear_notifications(self):
        """清空通知"""
        self.update_notifications(0)
        
    def _create_tooltip(self, widget: tk.Widget, text: str):
        """创建工具提示"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root - 30}")
            
            colors = self.theme_manager.get_theme()['colors']
            
            label = tk.Label(
                tooltip,
                text=text,
                bg=colors['bg_tertiary'],
                fg=colors['fg_primary'],
                font=('Consolas', 8),
                relief=tk.SOLID,
                borderwidth=1,
                padx=8,
                pady=4
            )
            label.pack()
            
            tooltip.after(3000, tooltip.destroy)
            
        # 移除之前的绑定
        widget.unbind('<Enter>')
        widget.bind('<Enter>', show_tooltip)
        
    def _on_connection_click(self, event):
        """处理连接状态点击"""
        if self.status_info['connection'] == 'disconnected':
            self.add_notification("尝试重新连接服务器...", "info")
            # 这里可以调用重连逻辑
            if hasattr(self.main_app, 'reconnect'):
                self.main_app.reconnect()
        else:
            self.add_notification("连接状态正常", "success")
            
    def _on_market_click(self, event):
        """处理市场状态点击"""
        # 显示市场详细信息
        if hasattr(self.main_app, 'terminal_panel'):
            self.main_app.terminal_panel.append_output(
                "查询市场状态...",
                'system'
            )
            self.main_app.execute_command("market status")
            
    def _on_user_click(self, event):
        """处理用户状态点击"""
        if self.status_info['user_status'] == 'offline':
            self.add_notification("请先登录系统", "warning")
        else:
            # 显示用户信息
            if hasattr(self.main_app, 'terminal_panel'):
                self.main_app.terminal_panel.append_output(
                    "查询用户信息...",
                    'system'
                )
                self.main_app.execute_command("user info")
                
    def _on_notification_click(self, event):
        """处理通知点击"""
        if self.status_info['notifications'] > 0:
            self.clear_notifications()
            self.add_notification("通知已清空", "success")
        else:
            self.add_notification("暂无新通知", "info")
            
    def show_status_message(self, message: str, duration: int = 3000):
        """显示临时状态消息"""
        # 保存原始文本
        original_text = self.system_info_label.cget('text')
        
        # 显示新消息
        colors = self.theme_manager.get_theme()['colors']
        self.system_info_label.configure(text=message, fg=colors['accent_primary'])
        
        # 定时恢复
        def restore_text():
            try:
                self.system_info_label.configure(text=original_text, fg=colors['fg_muted'])
            except tk.TclError:
                pass
                
        self.main_frame.after(duration, restore_text)
        
    def stop_time_update(self):
        """停止时间更新"""
        self.time_running = False
        if self.time_thread and self.time_thread.is_alive():
            self.time_thread.join(timeout=1)
            
    def get_status_info(self) -> Dict[str, Any]:
        """获取状态信息"""
        return self.status_info.copy()
        
    def set_theme(self, theme_name: str):
        """设置主题"""
        self.theme_manager.set_theme(theme_name)
        colors = self.theme_manager.get_theme()['colors']
        
        # 更新所有组件的颜色
        self.main_frame.configure(bg=colors['bg_secondary'])
        
        # 更新各个标签的颜色
        for widget in [self.connection_label, self.market_label, self.user_label,
                      self.system_info_label, self.notification_label, self.date_label]:
            widget.configure(bg=colors['bg_secondary'])
            
        self.time_label.configure(bg=colors['bg_secondary'], fg=colors['fg_primary'])
        
        # 重新应用状态颜色
        self.update_connection_status(self.status_info['connection'])
        self.update_market_status(self.status_info['market_status'])
        self.update_user_status()
        self.update_notifications(self.status_info['notifications'])