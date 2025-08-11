# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - 左侧活动栏
VSCode风格的功能导航栏
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional

class SidebarPanel:
    """左侧活动栏类"""
    
    def __init__(self, parent: tk.Frame, main_app):
        self.parent = parent
        self.main_app = main_app
        self.theme_manager = main_app.theme_manager
        
        # 当前激活的按钮
        self.active_button: Optional[tk.Button] = None
        
        # 按钮列表
        self.buttons: Dict[str, tk.Button] = {}
        
        # 创建界面
        self._create_ui()
        
    def _create_ui(self):
        """创建用户界面"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 主容器
        self.main_frame = tk.Frame(
            self.parent,
            bg=colors['bg_sidebar'],
            width=60
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.pack_propagate(False)
        
        # 顶部按钮区域
        self.top_frame = tk.Frame(self.main_frame, bg=colors['bg_sidebar'])
        self.top_frame.pack(side=tk.TOP, fill=tk.X, pady=(5, 0))
        
        # 创建功能按钮
        self._create_function_buttons()
        
        # 底部按钮区域
        self.bottom_frame = tk.Frame(self.main_frame, bg=colors['bg_sidebar'])
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 5))
        
        # 创建底部按钮
        self._create_bottom_buttons()
        
    def _create_function_buttons(self):
        """创建功能按钮"""
        # 按钮配置：(id, icon, tooltip, command)
        button_configs = [
            ('home', '🏠', '主页 - 返回主界面', self._handle_home),
            ('market', '📊', '市场 - 股票市场和实时行情', self._handle_market),
            ('portfolio', '💰', '投资 - 投资组合和交易历史', self._handle_portfolio),
            ('news', '📰', '新闻 - 财经新闻和市场分析', self._handle_news),
            ('apps', '📱', '应用 - 应用市场和工具集', self._handle_apps),
            ('bank', '🏦', '银行 - 银行服务和贷款', self._handle_bank),
            ('search', '🔍', '搜索 - 全局搜索和查询', self._handle_search),
            ('settings', '⚙️', '设置 - 系统设置和配置', self._handle_settings),
        ]
        
        for btn_id, icon, tooltip, command in button_configs:
            self._create_sidebar_button(btn_id, icon, tooltip, command)
            
    def _create_bottom_buttons(self):
        """创建底部按钮"""
        # 帮助按钮
        self._create_sidebar_button(
            'help', '❓', '帮助 - 帮助文档和教程', 
            self._handle_help, parent=self.bottom_frame
        )
        
    def _create_sidebar_button(self, btn_id: str, icon: str, tooltip: str, 
                              command: Callable, parent: tk.Frame = None):
        """创建侧边栏按钮"""
        if parent is None:
            parent = self.top_frame
            
        colors = self.theme_manager.get_theme()['colors']
        
        button = tk.Button(
            parent,
            text=icon,
            bg=colors['bg_sidebar'],
            fg=colors['fg_secondary'],
            activebackground=colors['accent_primary'],
            activeforeground=colors['fg_bright'],
            font=('Segoe UI Symbol', 14),
            borderwidth=0,
            relief=tk.FLAT,
            width=4,
            height=2,
            command=lambda: self._on_button_click(btn_id, command),
            cursor='hand2'
        )
        
        button.pack(pady=2, padx=5)
        
        # 保存按钮引用
        self.buttons[btn_id] = button
        
        # 绑定悬停效果
        self._bind_hover_effects(button)
        
        # 创建工具提示
        self._create_tooltip(button, tooltip)
        
    def _bind_hover_effects(self, button: tk.Button):
        """绑定悬停效果"""
        colors = self.theme_manager.get_theme()['colors']
        
        def on_enter(event):
            if button != self.active_button:
                button.configure(
                    bg=colors['accent_secondary'],
                    fg=colors['fg_bright']
                )
                
        def on_leave(event):
            if button != self.active_button:
                button.configure(
                    bg=colors['bg_sidebar'],
                    fg=colors['fg_secondary']
                )
                
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
    def _create_tooltip(self, widget: tk.Widget, text: str):
        """创建工具提示"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            
            colors = self.theme_manager.get_theme()['colors']
            
            label = tk.Label(
                tooltip,
                text=text,
                bg=colors['bg_tertiary'],
                fg=colors['fg_primary'],
                font=('Consolas', 9),
                relief=tk.SOLID,
                borderwidth=1,
                padx=8,
                pady=4
            )
            label.pack()
            
            # 自动销毁
            tooltip.after(3000, tooltip.destroy)
            
            # 鼠标离开时销毁
            def hide_tooltip(event):
                tooltip.destroy()
                
            widget.bind('<Leave>', hide_tooltip, add='+')
            
        widget.bind('<Enter>', show_tooltip, add='+')
        
    def _on_button_click(self, btn_id: str, command: Callable):
        """处理按钮点击"""
        # 更新激活状态
        self._set_active_button(btn_id)
        
        # 执行命令
        try:
            command()
        except Exception as e:
            print(f"侧边栏按钮 {btn_id} 执行错误: {e}")
            
    def _set_active_button(self, btn_id: str):
        """设置激活按钮"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 重置所有按钮
        for button in self.buttons.values():
            button.configure(
                bg=colors['bg_sidebar'],
                fg=colors['fg_secondary']
            )
            
        # 设置激活按钮
        if btn_id in self.buttons:
            self.active_button = self.buttons[btn_id]
            self.active_button.configure(
                bg=colors['accent_primary'],
                fg=colors['fg_bright']
            )
            
    # 按钮处理函数
    def _handle_home(self):
        """处理主页按钮"""
        self.main_app.terminal_panel.clear_output()
        self.main_app.terminal_panel.append_output("🏠 欢迎来到CHIPS BATTLE REMAKE!")
        self.main_app.terminal_panel.append_output("📊 当前市场状态: 🟢 开盘交易中")
        
        if self.main_app.current_user:
            balance = self.main_app.current_user.get('balance', 0)
            self.main_app.terminal_panel.append_output(f"💰 您的总资产: ${balance:,}")
            
        self.main_app.terminal_panel.append_output("💡 提示: 使用 'help' 命令查看可用操作")
        
        # 显示相关右侧面板
        self.main_app.right_panel_manager.show_panel('overview')
        
    def _handle_market(self):
        """处理市场按钮"""
        self.main_app.execute_command("market --overview")
        self.main_app.right_panel_manager.show_panel('stock')
        
    def _handle_portfolio(self):
        """处理投资组合按钮"""
        self.main_app.execute_command("portfolio --summary")
        self.main_app.right_panel_manager.show_panel('portfolio')
        
    def _handle_news(self):
        """处理新闻按钮"""
        self.main_app.execute_command("news --latest")
        self.main_app.right_panel_manager.show_panel('news')
        
    def _handle_apps(self):
        """处理应用按钮"""
        self.main_app.execute_command("app list")
        self.main_app.right_panel_manager.show_panel('apps')
        
    def _handle_bank(self):
        """处理银行按钮"""
        self.main_app.execute_command("bank status")
        self.main_app.right_panel_manager.show_panel('bank')
        
    def _handle_search(self):
        """处理搜索按钮"""
        # 聚焦到终端的搜索功能
        self.main_app.terminal_panel.focus_search()
        
    def _handle_settings(self):
        """处理设置按钮"""
        self._show_settings_dialog()
        
    def _handle_help(self):
        """处理帮助按钮"""
        self.main_app.show_help()
        
    def _show_settings_dialog(self):
        """显示设置对话框"""
        dialog = tk.Toplevel(self.main_app.root)
        dialog.title("设置")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.main_app.root)
        dialog.grab_set()
        
        # 应用主题
        colors = self.theme_manager.get_theme()['colors']
        dialog.configure(bg=colors['bg_primary'])
        
        # 居中显示
        dialog.update_idletasks()
        x = self.main_app.root.winfo_x() + (self.main_app.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.main_app.root.winfo_y() + (self.main_app.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # 创建设置界面
        main_frame = self.theme_manager.create_styled_widget('Frame', dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = self.theme_manager.create_styled_widget(
            'Label', main_frame,
            text="⚙️ 系统设置",
            font=('Consolas', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # 主题选择
        theme_frame = self.theme_manager.create_styled_widget('Frame', main_frame)
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.theme_manager.create_styled_widget(
            'Label', theme_frame,
            text="界面主题:"
        ).pack(side=tk.LEFT)
        
        theme_var = tk.StringVar(value=self.theme_manager.current_theme)
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=theme_var,
            values=list(self.theme_manager.get_available_themes().values()),
            state='readonly',
            width=15
        )
        theme_combo.pack(side=tk.RIGHT)
        
        # 自动保存设置
        auto_save_frame = self.theme_manager.create_styled_widget('Frame', main_frame)
        auto_save_frame.pack(fill=tk.X, pady=(0, 15))
        
        auto_save_var = tk.BooleanVar(value=True)
        auto_save_check = tk.Checkbutton(
            auto_save_frame,
            text="自动保存游戏进度",
            variable=auto_save_var,
            bg=colors['bg_primary'],
            fg=colors['fg_primary'],
            selectcolor=colors['bg_secondary'],
            activebackground=colors['bg_primary'],
            activeforeground=colors['fg_primary']
        )
        auto_save_check.pack(anchor=tk.W)
        
        # 音效设置
        sound_frame = self.theme_manager.create_styled_widget('Frame', main_frame)
        sound_frame.pack(fill=tk.X, pady=(0, 15))
        
        sound_var = tk.BooleanVar(value=False)
        sound_check = tk.Checkbutton(
            sound_frame,
            text="启用音效",
            variable=sound_var,
            bg=colors['bg_primary'],
            fg=colors['fg_primary'],
            selectcolor=colors['bg_secondary'],
            activebackground=colors['bg_primary'],
            activeforeground=colors['fg_primary']
        )
        sound_check.pack(anchor=tk.W)
        
        # 按钮区域
        btn_frame = self.theme_manager.create_styled_widget('Frame', main_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        def apply_settings():
            # 应用主题
            selected_theme = theme_var.get()
            for theme_id, theme_name in self.theme_manager.get_available_themes().items():
                if theme_name == selected_theme:
                    if self.theme_manager.switch_theme(theme_id):
                        self.theme_manager.apply_theme(self.main_app.root)
                    break
                    
            dialog.destroy()
            
        def cancel_settings():
            dialog.destroy()
            
        apply_btn = self.theme_manager.create_styled_widget(
            'Button', btn_frame,
            text="应用",
            command=apply_settings
        )
        apply_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = self.theme_manager.create_styled_widget(
            'Button', btn_frame,
            text="取消",
            command=cancel_settings
        )
        cancel_btn.pack(side=tk.LEFT)
        
    def focus(self):
        """聚焦侧边栏"""
        if self.active_button:
            self.active_button.focus_set()
        elif self.buttons:
            # 聚焦第一个按钮
            first_button = next(iter(self.buttons.values()))
            first_button.focus_set()
            
    def toggle_visibility(self):
        """切换侧边栏可见性"""
        self.main_app.layout_manager.toggle_sidebar()
        
    def get_active_button_id(self) -> Optional[str]:
        """获取当前激活的按钮ID"""
        for btn_id, button in self.buttons.items():
            if button == self.active_button:
                return btn_id
        return None