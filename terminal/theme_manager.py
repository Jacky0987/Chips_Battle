# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - 主题管理器
专业交易员风格配色方案
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

class ThemeManager:
    """主题管理器"""
    
    def __init__(self):
        self.themes = {
            'professional': {
                'name': '专业交易员',
                'colors': {
                    # 背景色
                    'bg_primary': '#1e1e1e',      # 主背景（深灰）
                    'bg_secondary': '#252526',     # 次要背景
                    'bg_tertiary': '#2d2d30',      # 第三背景
                    'bg_sidebar': '#333333',       # 侧边栏背景
                    'bg_panel': '#252526',         # 面板背景
                    'bg_terminal': '#1e1e1e',      # 终端背景
                    'bg_header': '#2d2d30',        # 顶部栏背景
                    'bg_footer': '#007acc',        # 底部栏背景
                    
                    # 前景色
                    'fg_primary': '#d4d4d4',       # 主文字（浅灰）
                    'fg_secondary': '#cccccc',     # 次要文字
                    'fg_muted': '#969696',         # 弱化文字
                    'fg_bright': '#ffffff',        # 亮文字
                    
                    # 强调色
                    'accent_primary': '#007acc',   # 主强调色（蓝色）
                    'accent_secondary': '#0e639c', # 次强调色
                    
                    # 状态色
                    'success': '#4caf50',          # 成功（绿色）
                    'warning': '#ff9800',          # 警告（橙色）
                    'error': '#f44336',            # 错误（红色）
                    'info': '#2196f3',             # 信息（蓝色）
                    
                    # 边框色
                    'border_primary': '#404040',   # 主边框（中灰）
                    'border_secondary': '#2d2d30', # 次边框
                    'border_focus': '#007acc',     # 聚焦边框
                    
                    # 按钮色
                    'btn_primary': '#0e639c',      # 主按钮
                    'btn_secondary': '#3c3c3c',    # 次按钮
                    'btn_hover': '#1177bb',        # 悬停
                    'btn_active': '#005a9e',       # 激活
                    
                    # 输入框色
                    'input_bg': '#3c3c3c',         # 输入框背景
                    'input_fg': '#cccccc',         # 输入框文字
                    'input_border': '#404040',     # 输入框边框
                    'input_focus': '#007acc',      # 输入框聚焦
                    
                    # 滚动条色
                    'scrollbar_bg': '#2d2d30',     # 滚动条背景
                    'scrollbar_thumb': '#424242',  # 滚动条滑块
                    'scrollbar_hover': '#4e4e4e',  # 滚动条悬停
                }
            },
            'gaming': {
                'name': '游戏化界面',
                'colors': {
                    # 渐变色系（简化为单色）
                    'bg_primary': '#0f0f23',
                    'bg_secondary': '#1a1a2e',
                    'bg_tertiary': '#16213e',
                    'bg_sidebar': '#0f3460',
                    'bg_panel': '#1a1a2e',
                    'bg_terminal': '#0f0f23',
                    'bg_header': '#16213e',
                    'bg_footer': '#667eea',
                    
                    'fg_primary': '#ffffff',
                    'fg_secondary': '#e0e0e0',
                    'fg_muted': '#a0a0a0',
                    'fg_bright': '#ffffff',
                    
                    'accent_primary': '#667eea',
                    'accent_secondary': '#764ba2',
                    
                    'success': '#4facfe',
                    'warning': '#ffecd2',
                    'error': '#f5576c',
                    'info': '#00f2fe',
                    
                    'border_primary': '#667eea',
                    'border_secondary': '#764ba2',
                    'border_focus': '#4facfe',
                    
                    'btn_primary': '#667eea',
                    'btn_secondary': '#764ba2',
                    'btn_hover': '#4facfe',
                    'btn_active': '#5a6fd8',
                    
                    'input_bg': '#1a1a2e',
                    'input_fg': '#ffffff',
                    'input_border': '#667eea',
                    'input_focus': '#4facfe',
                    
                    'scrollbar_bg': '#1a1a2e',
                    'scrollbar_thumb': '#667eea',
                    'scrollbar_hover': '#4facfe',
                }
            }
        }
        
        self.current_theme = 'professional'
        
    def get_theme(self, theme_name: str = None) -> Dict[str, Any]:
        """获取主题配置"""
        if theme_name is None:
            theme_name = self.current_theme
        return self.themes.get(theme_name, self.themes['professional'])
        
    def get_color(self, color_name: str, theme_name: str = None) -> str:
        """获取指定颜色"""
        theme = self.get_theme(theme_name)
        return theme['colors'].get(color_name, '#ffffff')
        
    def apply_theme(self, widget: tk.Widget, theme_name: str = None):
        """应用主题到指定组件"""
        if theme_name:
            self.current_theme = theme_name
            
        theme = self.get_theme()
        colors = theme['colors']
        
        # 配置根窗口
        if isinstance(widget, tk.Tk):
            widget.configure(bg=colors['bg_primary'])
            
            # 配置ttk样式
            self._configure_ttk_styles(colors)
            
    def _configure_ttk_styles(self, colors: Dict[str, str]):
        """配置ttk组件样式"""
        style = ttk.Style()
        
        # 配置Frame样式
        style.configure('VSCode.TFrame', 
                       background=colors['bg_primary'],
                       borderwidth=0)
                       
        style.configure('Sidebar.TFrame',
                       background=colors['bg_sidebar'],
                       borderwidth=0)
                       
        style.configure('Panel.TFrame',
                       background=colors['bg_panel'],
                       borderwidth=0)
                       
        style.configure('Header.TFrame',
                       background=colors['bg_header'],
                       borderwidth=0)
                       
        style.configure('Footer.TFrame',
                       background=colors['bg_footer'],
                       borderwidth=0)
        
        # 配置Label样式
        style.configure('VSCode.TLabel',
                       background=colors['bg_primary'],
                       foreground=colors['fg_primary'],
                       font=('Consolas', 9))
                       
        style.configure('Header.TLabel',
                       background=colors['bg_header'],
                       foreground=colors['fg_primary'],
                       font=('Consolas', 9, 'bold'))
                       
        style.configure('Footer.TLabel',
                       background=colors['bg_footer'],
                       foreground=colors['fg_bright'],
                       font=('Consolas', 8))
                       
        style.configure('Sidebar.TLabel',
                       background=colors['bg_sidebar'],
                       foreground=colors['fg_secondary'],
                       font=('Consolas', 8))
        
        # 配置Button样式
        style.configure('VSCode.TButton',
                       background=colors['btn_primary'],
                       foreground=colors['fg_bright'],
                       borderwidth=1,
                       focuscolor='none',
                       font=('Consolas', 9))
                       
        style.map('VSCode.TButton',
                 background=[('active', colors['btn_hover']),
                           ('pressed', colors['btn_active'])])
                           
        style.configure('Sidebar.TButton',
                       background=colors['bg_sidebar'],
                       foreground=colors['fg_secondary'],
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI Symbol', 12))
                       
        style.map('Sidebar.TButton',
                 background=[('active', colors['accent_primary']),
                           ('pressed', colors['accent_secondary'])],
                 foreground=[('active', colors['fg_bright'])])
        
        # 配置Entry样式
        style.configure('VSCode.TEntry',
                       fieldbackground=colors['input_bg'],
                       foreground=colors['input_fg'],
                       borderwidth=1,
                       insertcolor=colors['fg_primary'],
                       font=('Consolas', 10))
                       
        style.map('VSCode.TEntry',
                 focuscolor=[('focus', colors['input_focus'])])
        
        # 配置Text样式（通过标签）
        style.configure('Terminal.TFrame',
                       background=colors['bg_terminal'])
        
        # 配置Scrollbar样式
        style.configure('VSCode.Vertical.TScrollbar',
                       background=colors['scrollbar_bg'],
                       troughcolor=colors['scrollbar_bg'],
                       borderwidth=0,
                       arrowcolor=colors['scrollbar_thumb'],
                       darkcolor=colors['scrollbar_bg'],
                       lightcolor=colors['scrollbar_bg'])
                       
        style.map('VSCode.Vertical.TScrollbar',
                 background=[('active', colors['scrollbar_hover'])])
        
    def create_styled_widget(self, widget_type: str, parent: tk.Widget, style_name: str = None, **kwargs):
        """创建带样式的组件"""
        colors = self.get_theme()['colors']
        
        if widget_type == 'Frame':
            if style_name:
                return ttk.Frame(parent, style=f'{style_name}.TFrame', **kwargs)
            else:
                return tk.Frame(parent, bg=colors['bg_primary'], **kwargs)
                
        elif widget_type == 'Label':
            if style_name:
                return ttk.Label(parent, style=f'{style_name}.TLabel', **kwargs)
            else:
                # 避免font参数重复
                label_kwargs = {
                    'bg': colors['bg_primary'],
                    'fg': colors['fg_primary'],
                    'font': ('Consolas', 9)
                }
                label_kwargs.update(kwargs)
                return tk.Label(parent, **label_kwargs)
                              
        elif widget_type == 'Button':
            if style_name:
                return ttk.Button(parent, style=f'{style_name}.TButton', **kwargs)
            else:
                # 避免参数重复
                button_kwargs = {
                    'bg': colors['btn_primary'],
                    'fg': colors['fg_bright'],
                    'activebackground': colors['btn_hover'],
                    'activeforeground': colors['fg_bright'],
                    'borderwidth': 1,
                    'font': ('Consolas', 9)
                }
                button_kwargs.update(kwargs)
                return tk.Button(parent, **button_kwargs)
                               
        elif widget_type == 'Entry':
            if style_name:
                return ttk.Entry(parent, style=f'{style_name}.TEntry', **kwargs)
            else:
                return tk.Entry(parent,
                              bg=colors['input_bg'],
                              fg=colors['input_fg'],
                              insertbackground=colors['fg_primary'],
                              font=('Consolas', 10),
                              **kwargs)
                              
        elif widget_type == 'Text':
            return tk.Text(parent,
                          bg=colors['bg_terminal'],
                          fg=colors['fg_primary'],
                          insertbackground=colors['fg_primary'],
                          selectbackground=colors['accent_primary'],
                          selectforeground=colors['fg_bright'],
                          font=('Consolas', 10),
                          **kwargs)
                          
        else:
            # 默认返回Frame
            return tk.Frame(parent, bg=colors['bg_primary'], **kwargs)
            
    def switch_theme(self, theme_name: str):
        """切换主题"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            return True
        return False
        
    def get_available_themes(self) -> Dict[str, str]:
        """获取可用主题列表"""
        return {name: theme['name'] for name, theme in self.themes.items()}