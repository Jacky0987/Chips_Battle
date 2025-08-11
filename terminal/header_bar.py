# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - 顶部状态栏
显示用户信息、余额、时间等关键信息
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Dict, Any, Optional

class HeaderBar:
    """顶部状态栏类"""
    
    def __init__(self, parent: tk.Frame, main_app):
        self.parent = parent
        self.main_app = main_app
        self.theme_manager = main_app.theme_manager
        
        # 用户信息
        self.user_data: Optional[Dict[str, Any]] = None
        
        # 创建界面
        self._create_ui()
        
        # 延迟启动时间更新，确保在tkinter主循环启动后进行
        self.main_frame.after(100, self._start_time_update)
        
    def _create_ui(self):
        """创建用户界面"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 主容器
        self.main_frame = tk.Frame(
            self.parent,
            bg=colors['bg_header'],
            height=40
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.pack_propagate(False)
        
        # 左侧：游戏标题和版本
        self.left_frame = tk.Frame(self.main_frame, bg=colors['bg_header'])
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        
        self.title_label = tk.Label(
            self.left_frame,
            text="🎮 CHIPS BATTLE REMAKE v3.0 Alpha",
            bg=colors['bg_header'],
            fg=colors['fg_bright'],
            font=('Consolas', 10, 'bold')
        )
        self.title_label.pack(side=tk.LEFT, pady=8)
        
        # 右侧：用户信息、余额、时间
        self.right_frame = tk.Frame(self.main_frame, bg=colors['bg_header'])
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        
        # 时间显示
        self.time_label = tk.Label(
            self.right_frame,
            text="🕐 [加载中...]",
            bg=colors['bg_header'],
            fg=colors['fg_primary'],
            font=('Consolas', 9)
        )
        self.time_label.pack(side=tk.RIGHT, pady=8, padx=(10, 0))
        
        # 余额显示
        self.balance_label = tk.Label(
            self.right_frame,
            text="💰 余额: [未登录]",
            bg=colors['bg_header'],
            fg=colors['fg_primary'],
            font=('Consolas', 9)
        )
        self.balance_label.pack(side=tk.RIGHT, pady=8, padx=(10, 0))
        
        # 用户信息显示
        self.user_label = tk.Label(
            self.right_frame,
            text="👤 玩家: [未登录]",
            bg=colors['bg_header'],
            fg=colors['fg_primary'],
            font=('Consolas', 9)
        )
        self.user_label.pack(side=tk.RIGHT, pady=8, padx=(10, 0))
        
        # 中间：状态指示器
        self.center_frame = tk.Frame(self.main_frame, bg=colors['bg_header'])
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 连接状态
        self.status_frame = tk.Frame(self.center_frame, bg=colors['bg_header'])
        self.status_frame.pack(expand=True)
        
        self.connection_label = tk.Label(
            self.status_frame,
            text="🟢 在线",
            bg=colors['bg_header'],
            fg=colors['success'],
            font=('Consolas', 8)
        )
        self.connection_label.pack(side=tk.LEFT, pady=10, padx=5)
        
        # 游戏状态
        self.game_status_label = tk.Label(
            self.status_frame,
            text="⚡ 就绪",
            bg=colors['bg_header'],
            fg=colors['info'],
            font=('Consolas', 8)
        )
        self.game_status_label.pack(side=tk.LEFT, pady=10, padx=5)
        
    def update_user_info(self, user_data: Dict[str, Any]):
        """更新用户信息显示"""
        self.user_data = user_data
        
        # 更新用户名
        username = user_data.get('username', '未知用户')
        self.user_label.configure(text=f"👤 玩家: {username}")
        
        # 更新余额
        balance = user_data.get('balance', 0)
        self.balance_label.configure(text=f"💰 余额: ${balance:,}")
        
        # 如果有等级信息，显示等级
        if 'level' in user_data:
            level = user_data['level']
            experience = user_data.get('experience', 0)
            level_text = f"🏆 等级: {level}  🌟 经验: {experience}"
            
            # 创建等级标签（如果不存在）
            if not hasattr(self, 'level_label'):
                self.level_label = tk.Label(
                    self.right_frame,
                    text=level_text,
                    bg=self.theme_manager.get_color('bg_header'),
                    fg=self.theme_manager.get_color('warning'),
                    font=('Consolas', 9)
                )
                self.level_label.pack(side=tk.RIGHT, pady=8, padx=(10, 0), before=self.time_label)
            else:
                self.level_label.configure(text=level_text)
                
    def update_balance(self, new_balance: float):
        """更新余额显示"""
        if self.user_data:
            self.user_data['balance'] = new_balance
            self.balance_label.configure(text=f"💰 余额: ${new_balance:,}")
            
    def update_connection_status(self, is_connected: bool):
        """更新连接状态"""
        colors = self.theme_manager.get_theme()['colors']
        
        if is_connected:
            self.connection_label.configure(
                text="🟢 在线",
                fg=colors['success']
            )
        else:
            self.connection_label.configure(
                text="🔴 离线",
                fg=colors['error']
            )
            
    def update_game_status(self, status: str, status_type: str = 'info'):
        """更新游戏状态"""
        colors = self.theme_manager.get_theme()['colors']
        
        status_colors = {
            'info': colors['info'],
            'success': colors['success'],
            'warning': colors['warning'],
            'error': colors['error']
        }
        
        status_icons = {
            'info': '⚡',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌'
        }
        
        icon = status_icons.get(status_type, '⚡')
        color = status_colors.get(status_type, colors['info'])
        
        self.game_status_label.configure(
            text=f"{icon} {status}",
            fg=color
        )
        
    def _start_time_update(self):
        """启动时间更新循环"""
        self._update_time()
        
    def _update_time(self):
        """更新时间显示"""
        try:
            # 获取当前时间
            current_time = datetime.now()
            time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # 更新显示
            self.time_label.configure(text=f"🕐 {time_str}")
            
            # 每秒更新一次
            self.main_frame.after(1000, self._update_time)
            
        except Exception as e:
            print(f"Header时间更新错误: {e}")
            # 出错时也要继续更新
            self.main_frame.after(1000, self._update_time)
            
    def show_notification(self, message: str, duration: int = 3000):
        """显示临时通知"""
        # 保存原始状态
        original_text = self.game_status_label.cget('text')
        original_color = self.game_status_label.cget('fg')
        
        # 显示通知
        colors = self.theme_manager.get_theme()['colors']
        self.game_status_label.configure(
            text=f"📢 {message}",
            fg=colors['warning']
        )
        
        # 定时恢复
        def restore_status():
            self.game_status_label.configure(
                text=original_text,
                fg=original_color
            )
            
        self.main_frame.after(duration, restore_status)
        
    def add_custom_widget(self, widget: tk.Widget, position: str = 'center'):
        """添加自定义组件"""
        if position == 'left':
            widget.pack(in_=self.left_frame, side=tk.LEFT, pady=8, padx=5)
        elif position == 'right':
            widget.pack(in_=self.right_frame, side=tk.RIGHT, pady=8, padx=5)
        else:  # center
            widget.pack(in_=self.center_frame, side=tk.LEFT, pady=8, padx=5)
            
    def get_user_data(self) -> Optional[Dict[str, Any]]:
        """获取当前用户数据"""
        return self.user_data
        
    def reset(self):
        """重置状态栏（用户登出时）"""
        self.user_data = None
        
        # 重置显示
        self.user_label.configure(text="👤 玩家: [未登录]")
        self.balance_label.configure(text="💰 余额: [未登录]")
        
        # 移除等级标签
        if hasattr(self, 'level_label'):
            self.level_label.destroy()
            delattr(self, 'level_label')
            
        # 重置状态
        self.update_connection_status(False)
        self.update_game_status("未登录", 'warning')