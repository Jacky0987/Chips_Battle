# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - 布局管理器
VSCode风格的响应式布局系统
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Tuple

class VSCodeLayoutManager:
    """VSCode风格布局管理器"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        
        # 布局配置
        self.sidebar_width = 60
        self.panel_width = 300
        self.header_height = 40
        self.footer_height = 30
        self.min_terminal_width = 400
        
        # 存储各个区域的Frame
        self.frames: Dict[str, tk.Frame] = {}
        
        # 布局状态
        self.sidebar_visible = True
        self.panel_visible = True
        
    def create_layout(self):
        """创建主要布局结构"""
        # 创建主容器
        self.main_container = tk.Frame(self.root, bg='#1e1e1e')
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建顶部区域（Header）
        self.frames['header'] = tk.Frame(
            self.main_container, 
            height=self.header_height,
            bg='#2d2d30'
        )
        self.frames['header'].pack(side=tk.TOP, fill=tk.X)
        self.frames['header'].pack_propagate(False)
        
        # 创建中间容器（包含sidebar, terminal, panel）
        self.middle_container = tk.Frame(self.main_container, bg='#1e1e1e')
        self.middle_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 创建左侧边栏（Sidebar）
        self.frames['sidebar'] = tk.Frame(
            self.middle_container,
            width=self.sidebar_width,
            bg='#333333'
        )
        self.frames['sidebar'].pack(side=tk.LEFT, fill=tk.Y)
        self.frames['sidebar'].pack_propagate(False)
        
        # 创建右侧面板（Panel）
        self.frames['panel'] = tk.Frame(
            self.middle_container,
            width=self.panel_width,
            bg='#252526'
        )
        self.frames['panel'].pack(side=tk.RIGHT, fill=tk.Y)
        self.frames['panel'].pack_propagate(False)
        
        # 创建中央终端区域（Terminal）
        self.frames['terminal'] = tk.Frame(
            self.middle_container,
            bg='#1e1e1e'
        )
        self.frames['terminal'].pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 创建底部状态栏（Footer）
        self.frames['footer'] = tk.Frame(
            self.main_container,
            height=self.footer_height,
            bg='#007acc'
        )
        self.frames['footer'].pack(side=tk.BOTTOM, fill=tk.X)
        self.frames['footer'].pack_propagate(False)
        
    def get_frame(self, area: str) -> tk.Frame:
        """获取指定区域的Frame"""
        return self.frames.get(area)
        
    def calculate_layout(self, screen_width: int, screen_height: int) -> Dict[str, Tuple[int, int, int, int]]:
        """计算各区域的布局尺寸"""
        # 计算可用的中间区域高度
        middle_height = screen_height - self.header_height - self.footer_height
        
        # 计算终端区域宽度
        terminal_width = screen_width - (self.sidebar_width if self.sidebar_visible else 0) - (self.panel_width if self.panel_visible else 0)
        
        # 如果终端区域太小，隐藏右侧面板
        if terminal_width < self.min_terminal_width and self.panel_visible:
            self.panel_visible = False
            terminal_width = screen_width - (self.sidebar_width if self.sidebar_visible else 0)
            
        return {
            'header': (0, 0, screen_width, self.header_height),
            'sidebar': (0, self.header_height, self.sidebar_width if self.sidebar_visible else 0, middle_height),
            'terminal': (
                self.sidebar_width if self.sidebar_visible else 0, 
                self.header_height, 
                terminal_width, 
                middle_height
            ),
            'panel': (
                screen_width - (self.panel_width if self.panel_visible else 0), 
                self.header_height, 
                self.panel_width if self.panel_visible else 0, 
                middle_height
            ),
            'footer': (0, screen_height - self.footer_height, screen_width, self.footer_height)
        }
        
    def update_layout(self):
        """更新布局（响应窗口大小变化）"""
        # 获取当前窗口尺寸
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # 重新计算布局
        layout = self.calculate_layout(width, height)
        
        # 更新各个区域的可见性
        self._update_visibility()
        
    def toggle_sidebar(self):
        """切换侧边栏显示状态"""
        self.sidebar_visible = not self.sidebar_visible
        self._update_visibility()
        
    def toggle_panel(self):
        """切换右侧面板显示状态"""
        self.panel_visible = not self.panel_visible
        self._update_visibility()
        
    def _update_visibility(self):
        """更新各区域的可见性"""
        # 更新侧边栏
        if self.sidebar_visible:
            self.frames['sidebar'].pack(side=tk.LEFT, fill=tk.Y, before=self.frames['terminal'])
            self.frames['sidebar'].configure(width=self.sidebar_width)
        else:
            self.frames['sidebar'].pack_forget()
            
        # 更新右侧面板
        if self.panel_visible:
            self.frames['panel'].pack(side=tk.RIGHT, fill=tk.Y, after=self.frames['terminal'])
            self.frames['panel'].configure(width=self.panel_width)
        else:
            self.frames['panel'].pack_forget()
            
    def set_sidebar_width(self, width: int):
        """设置侧边栏宽度"""
        self.sidebar_width = width
        if self.sidebar_visible:
            self.frames['sidebar'].configure(width=width)
            
    def set_panel_width(self, width: int):
        """设置右侧面板宽度"""
        self.panel_width = width
        if self.panel_visible:
            self.frames['panel'].configure(width=width)
            
    def get_layout_info(self) -> Dict[str, any]:
        """获取当前布局信息"""
        return {
            'sidebar_width': self.sidebar_width,
            'panel_width': self.panel_width,
            'header_height': self.header_height,
            'footer_height': self.footer_height,
            'sidebar_visible': self.sidebar_visible,
            'panel_visible': self.panel_visible
        }