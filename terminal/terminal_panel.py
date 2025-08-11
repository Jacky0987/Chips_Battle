# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - 中央终端面板
实现命令行界面的GUI版本
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import List, Optional
import re
from datetime import datetime

class TerminalPanel:
    """中央终端面板类"""
    
    def __init__(self, parent: tk.Frame, main_app):
        self.parent = parent
        self.main_app = main_app
        self.theme_manager = main_app.theme_manager
        
        # 命令历史
        self.command_history: List[str] = []
        self.history_index = -1
        
        # 当前命令
        self.current_command = ""
        
        # 搜索相关
        self.search_mode = False
        self.search_text = ""
        
        # 登录模式相关
        self._login_mode = False
        self._login_callback = None
        self._password_mode = False
        
        # 创建界面
        self._create_ui()
        
        # 显示欢迎信息
        self._show_welcome_message()
        
    def _create_ui(self):
        """创建用户界面"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 主容器
        self.main_frame = tk.Frame(
            self.parent,
            bg=colors['bg_terminal']
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部工具栏
        self._create_toolbar()
        
        # 输出区域
        self._create_output_area()
        
        # 输入区域
        self._create_input_area()
        
    def _create_toolbar(self):
        """创建顶部工具栏"""
        colors = self.theme_manager.get_theme()['colors']
        
        self.toolbar_frame = tk.Frame(
            self.main_frame,
            bg=colors['bg_secondary'],
            height=35
        )
        self.toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        self.toolbar_frame.pack_propagate(False)
        
        # 左侧：终端标题
        left_frame = tk.Frame(self.toolbar_frame, bg=colors['bg_secondary'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        
        title_label = tk.Label(
            left_frame,
            text="🖥️ TERMINAL 主控制台",
            bg=colors['bg_secondary'],
            fg=colors['fg_primary'],
            font=('Consolas', 10, 'bold')
        )
        title_label.pack(side=tk.LEFT, pady=8)
        
        # 右侧：工具按钮
        right_frame = tk.Frame(self.toolbar_frame, bg=colors['bg_secondary'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 10))
        
        # 清空按钮
        clear_btn = tk.Button(
            right_frame,
            text="🔄",
            bg=colors['btn_secondary'],
            fg=colors['fg_primary'],
            activebackground=colors['btn_hover'],
            font=('Segoe UI Symbol', 10),
            borderwidth=0,
            relief=tk.FLAT,
            width=3,
            command=self.clear_output,
            cursor='hand2'
        )
        clear_btn.pack(side=tk.RIGHT, pady=6, padx=2)
        
        # 搜索按钮
        search_btn = tk.Button(
            right_frame,
            text="🔍",
            bg=colors['btn_secondary'],
            fg=colors['fg_primary'],
            activebackground=colors['btn_hover'],
            font=('Segoe UI Symbol', 10),
            borderwidth=0,
            relief=tk.FLAT,
            width=3,
            command=self.toggle_search,
            cursor='hand2'
        )
        search_btn.pack(side=tk.RIGHT, pady=6, padx=2)
        
        # 创建工具提示
        self._create_button_tooltip(clear_btn, "清空终端")
        self._create_button_tooltip(search_btn, "搜索内容")
        
    def _create_output_area(self):
        """创建输出区域"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 输出区域容器
        output_frame = tk.Frame(self.main_frame, bg=colors['bg_terminal'])
        output_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))
        
        # 创建文本区域和滚动条
        self.output_text = tk.Text(
            output_frame,
            bg=colors['bg_terminal'],
            fg=colors['fg_primary'],
            insertbackground=colors['fg_primary'],
            selectbackground=colors['accent_primary'],
            selectforeground=colors['fg_bright'],
            font=('Consolas', 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            borderwidth=0,
            highlightthickness=0
        )
        
        # 滚动条
        scrollbar = ttk.Scrollbar(
            output_frame,
            orient=tk.VERTICAL,
            command=self.output_text.yview,
            style='VSCode.Vertical.TScrollbar'
        )
        
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置文本标签样式
        self._configure_text_tags()
        
        # 绑定事件
        self.output_text.bind('<Button-1>', self._on_output_click)
        
    def _create_input_area(self):
        """创建输入区域"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 输入区域容器
        input_frame = tk.Frame(
            self.main_frame,
            bg=colors['bg_secondary'],
            height=40
        )
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)
        input_frame.pack_propagate(False)
        
        # 提示符
        prompt_label = tk.Label(
            input_frame,
            text="$ ",
            bg=colors['bg_secondary'],
            fg=colors['success'],
            font=('Consolas', 12, 'bold')
        )
        prompt_label.pack(side=tk.LEFT, pady=8, padx=(10, 5))
        
        # 输入框
        self.input_entry = tk.Entry(
            input_frame,
            bg=colors['input_bg'],
            fg=colors['input_fg'],
            insertbackground=colors['fg_primary'],
            font=('Consolas', 11),
            borderwidth=1,
            relief=tk.SOLID,
            highlightthickness=1,
            highlightcolor=colors['input_focus']
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8, padx=(0, 10))
        
        # 执行按钮
        execute_btn = tk.Button(
            input_frame,
            text="🚀 执行",
            bg=colors['btn_primary'],
            fg=colors['fg_bright'],
            activebackground=colors['btn_hover'],
            font=('Consolas', 9, 'bold'),
            borderwidth=0,
            relief=tk.FLAT,
            command=self._execute_command,
            cursor='hand2'
        )
        execute_btn.pack(side=tk.RIGHT, pady=6, padx=(5, 10))
        
        # 绑定事件
        self.input_entry.bind('<Return>', lambda e: self._execute_command())
        self.input_entry.bind('<Up>', self._handle_history_up)
        self.input_entry.bind('<Down>', self._handle_history_down)
        self.input_entry.bind('<Tab>', self._handle_tab_completion)
        self.input_entry.bind('<Control-c>', self._handle_interrupt)
        
        # 聚焦输入框
        self.input_entry.focus_set()
        
    def _configure_text_tags(self):
        """配置文本标签样式"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 系统消息
        self.output_text.tag_configure(
            'system',
            foreground=colors['info'],
            font=('Consolas', 10, 'bold')
        )
        
        # 成功消息
        self.output_text.tag_configure(
            'success',
            foreground=colors['success'],
            font=('Consolas', 10)
        )
        
        # 错误消息
        self.output_text.tag_configure(
            'error',
            foreground=colors['error'],
            font=('Consolas', 10, 'bold')
        )
        
        # 警告消息
        self.output_text.tag_configure(
            'warning',
            foreground=colors['warning'],
            font=('Consolas', 10)
        )
        
        # 命令
        self.output_text.tag_configure(
            'command',
            foreground=colors['accent_primary'],
            font=('Consolas', 10, 'bold')
        )
        
        # 高亮
        self.output_text.tag_configure(
            'highlight',
            background=colors['accent_primary'],
            foreground=colors['fg_bright']
        )
        
        # 时间戳
        self.output_text.tag_configure(
            'timestamp',
            foreground=colors['fg_muted'],
            font=('Consolas', 8)
        )
        
    def _create_button_tooltip(self, widget: tk.Widget, text: str):
        """创建按钮工具提示"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root - 20}")
            
            colors = self.theme_manager.get_theme()['colors']
            
            label = tk.Label(
                tooltip,
                text=text,
                bg=colors['bg_tertiary'],
                fg=colors['fg_primary'],
                font=('Consolas', 8),
                relief=tk.SOLID,
                borderwidth=1,
                padx=6,
                pady=3
            )
            label.pack()
            
            # 自动销毁
            tooltip.after(2000, tooltip.destroy)
            
        widget.bind('<Enter>', show_tooltip)
        
    def _show_welcome_message(self):
        self.append_output("")
        
    def append_output(self, text: str, tag: str = None, timestamp: bool = True):
        """添加输出文本"""
        self.output_text.configure(state=tk.NORMAL)
        
        # 添加时间戳
        if timestamp and text.strip():
            current_time = datetime.now().strftime("%H:%M:%S")
            self.output_text.insert(tk.END, f"[{current_time}] ", 'timestamp')
            
        # 添加文本
        if tag:
            self.output_text.insert(tk.END, text + "\n", tag)
        else:
            self.output_text.insert(tk.END, text + "\n")
            
        self.output_text.configure(state=tk.DISABLED)
        
        # 自动滚动到底部
        self.output_text.see(tk.END)
        
    def clear_output(self):
        """清空输出"""
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.output_text.configure(state=tk.DISABLED)
        
        # 重新显示欢迎信息
        self._show_welcome_message()
        
    def _execute_command(self):
        """执行命令"""
        command = self.input_entry.get().strip()
        
        if not command:
            return
            
        # 添加到历史
        if command not in self.command_history:
            self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        # 清空输入框
        self.input_entry.delete(0, tk.END)
        
        # 显示命令
        self.append_output(f"$ {command}", 'command', timestamp=False)
        
        # 执行命令
        self.main_app.execute_command(command)
        
    def _handle_history_up(self, event):
        """处理历史命令向上"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            command = self.command_history[self.history_index]
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, command)
        return 'break'
        
    def _handle_history_down(self, event):
        """处理历史命令向下"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            command = self.command_history[self.history_index]
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, command)
        elif self.history_index >= len(self.command_history) - 1:
            self.history_index = len(self.command_history)
            self.input_entry.delete(0, tk.END)
        return 'break'
        
    def _handle_tab_completion(self, event):
        """处理Tab自动补全"""
        current_text = self.input_entry.get()
        
        # 简单的命令补全
        commands = [
            'help', 'portfolio', 'market', 'news', 'bank', 'app', 'stock',
            'buy', 'sell', 'balance', 'status', 'quit', 'clear', 'history'
        ]
        
        matches = [cmd for cmd in commands if cmd.startswith(current_text)]
        
        if len(matches) == 1:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, matches[0] + ' ')
        elif len(matches) > 1:
            self.append_output(f"可能的命令: {', '.join(matches)}", 'system')
            
        return 'break'
        
    def _handle_interrupt(self, event):
        """处理Ctrl+C中断"""
        self.input_entry.delete(0, tk.END)
        self.append_output("^C", 'warning')
        return 'break'
        
    def _on_output_click(self, event):
        """处理输出区域点击"""
        # 点击输出区域时聚焦输入框
        self.input_entry.focus_set()
        
    def toggle_search(self):
        """切换搜索模式"""
        self.search_mode = not self.search_mode
        
        if self.search_mode:
            self._show_search_bar()
        else:
            self._hide_search_bar()
            
    def _show_search_bar(self):
        """显示搜索栏"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 创建搜索栏
        self.search_frame = tk.Frame(
            self.main_frame,
            bg=colors['bg_secondary'],
            height=35
        )
        self.search_frame.pack(side=tk.BOTTOM, fill=tk.X, before=self.input_entry.master)
        self.search_frame.pack_propagate(False)
        
        # 搜索标签
        search_label = tk.Label(
            self.search_frame,
            text="🔍 搜索:",
            bg=colors['bg_secondary'],
            fg=colors['fg_primary'],
            font=('Consolas', 9)
        )
        search_label.pack(side=tk.LEFT, pady=8, padx=(10, 5))
        
        # 搜索输入框
        self.search_entry = tk.Entry(
            self.search_frame,
            bg=colors['input_bg'],
            fg=colors['input_fg'],
            font=('Consolas', 9),
            borderwidth=1,
            relief=tk.SOLID
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=8, padx=(0, 5))
        
        # 搜索按钮
        search_btn = tk.Button(
            self.search_frame,
            text="搜索",
            bg=colors['btn_primary'],
            fg=colors['fg_bright'],
            font=('Consolas', 8),
            borderwidth=0,
            command=self._perform_search,
            cursor='hand2'
        )
        search_btn.pack(side=tk.LEFT, pady=6, padx=2)
        
        # 关闭按钮
        close_btn = tk.Button(
            self.search_frame,
            text="✕",
            bg=colors['error'],
            fg=colors['fg_bright'],
            font=('Consolas', 8),
            borderwidth=0,
            command=self.toggle_search,
            cursor='hand2'
        )
        close_btn.pack(side=tk.LEFT, pady=6, padx=(2, 10))
        
        # 绑定回车键
        self.search_entry.bind('<Return>', lambda e: self._perform_search())
        self.search_entry.focus_set()
        
    def _hide_search_bar(self):
        """隐藏搜索栏"""
        if hasattr(self, 'search_frame'):
            self.search_frame.destroy()
            delattr(self, 'search_frame')
            
        # 清除高亮
        self.output_text.tag_remove('highlight', 1.0, tk.END)
        
        # 重新聚焦输入框
        self.input_entry.focus_set()
        
    def _perform_search(self):
        """执行搜索"""
        if not hasattr(self, 'search_entry'):
            return
            
        search_text = self.search_entry.get().strip()
        if not search_text:
            return
            
        # 清除之前的高亮
        self.output_text.tag_remove('highlight', 1.0, tk.END)
        
        # 搜索文本
        content = self.output_text.get(1.0, tk.END)
        matches = []
        
        start = 1.0
        while True:
            pos = self.output_text.search(search_text, start, tk.END, nocase=True)
            if not pos:
                break
                
            # 计算结束位置
            end_pos = f"{pos}+{len(search_text)}c"
            
            # 高亮匹配文本
            self.output_text.tag_add('highlight', pos, end_pos)
            
            matches.append(pos)
            start = end_pos
            
        # 显示搜索结果
        if matches:
            self.append_output(f"找到 {len(matches)} 个匹配项", 'success')
            # 滚动到第一个匹配项
            self.output_text.see(matches[0])
        else:
            self.append_output(f"未找到 '{search_text}'", 'warning')
            
    def focus(self):
        """聚焦终端"""
        self.input_entry.focus_set()
        
    def focus_search(self):
        """聚焦搜索功能"""
        if not self.search_mode:
            self.toggle_search()
        else:
            if hasattr(self, 'search_entry'):
                self.search_entry.focus_set()
                
    def toggle_visibility(self):
        """切换终端可见性"""
        if self.main_frame.winfo_viewable():
            self.main_frame.pack_forget()
        else:
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
    def get_command_history(self) -> List[str]:
        """获取命令历史"""
        return self.command_history.copy()
        
    def set_prompt(self, prompt: str):
        """设置命令提示符"""
        # 这里可以动态更改提示符
        pass
        
    def simulate_typing(self, text: str, delay: int = 50):
        """模拟打字效果"""
        def type_char(index=0):
            if index < len(text):
                self.append_output(text[index], timestamp=False)
                self.main_frame.after(delay, lambda: type_char(index + 1))
                
        type_char()
        
    def set_login_mode(self, enabled: bool, password_mode: bool = False, callback=None):
        """设置登录模式"""
        self._login_mode = enabled
        self._password_mode = password_mode
        self._login_callback = callback
        
        if enabled:
            # 设置密码模式（显示*号）
            if password_mode:
                self.input_entry.configure(show="*")
            else:
                self.input_entry.configure(show="")
            
            # 聚焦输入框
            self.input_entry.focus_set()
            
            # 更新提示符
            self._update_prompt_for_login()
        else:
            # 恢复正常模式
            self.input_entry.configure(show="")
            self._login_callback = None
            self._password_mode = False
            
            # 恢复正常提示符
            self._update_prompt_normal()
            
    def _update_prompt_for_login(self):
        """更新登录模式的提示符"""
        # 这里可以更改提示符样式来表示登录模式
        pass
        
    def _update_prompt_normal(self):
        """恢复正常的提示符"""
        # 恢复正常提示符
        pass