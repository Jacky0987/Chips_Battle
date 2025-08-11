# -*- coding: utf-8 -*-
"""
GUI适配器

实现图形界面模式的UI适配器，基于tkinter。
"""

import asyncio
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List, Dict, Any
from datetime import datetime
import threading

from interfaces.ui_interface import (
    GameUIInterface, UIType, MessageType, InputType, Message, InputRequest, ProgressInfo, UIAdapter
)


class TkinterUIAdapter(GameUIInterface):
    """Tkinter GUI适配器
    
    基于tkinter实现的图形界面适配器。
    提供现代化的GUI界面和交互功能。
    """
    
    def __init__(self):
        super().__init__()
        self.root: Optional[tk.Tk] = None
        self.main_frame: Optional[ttk.Frame] = None
        self.output_text: Optional[tk.Text] = None
        self.input_frame: Optional[ttk.Frame] = None
        self.input_entry: Optional[ttk.Entry] = None
        self.progress_bar: Optional[ttk.Progressbar] = None
        self.progress_label: Optional[ttk.Label] = None
        
        # 颜色映射
        self._color_map = {
            MessageType.INFO: "#0066cc",
            MessageType.SUCCESS: "#00aa00",
            MessageType.WARNING: "#ff9900",
            MessageType.ERROR: "#cc0000",
            MessageType.DEBUG: "#666666",
            MessageType.COMMAND: "#0099cc",
            MessageType.SYSTEM: "#333333"
        }
        
        # 标签映射
        self._tag_map = {}
        
        # 异步任务队列
        self._async_queue = []
        self._queue_lock = threading.Lock()
        
        # 输入回调
        self._input_callback = None
        self._input_request = None
    
    @property
    def ui_type(self) -> UIType:
        """获取UI类型
        
        Returns:
            UI类型
        """
        return UIType.GUI
    
    async def initialize(self) -> bool:
        """初始化GUI
        
        Returns:
            是否初始化成功
        """
        try:
            self.logger.info("正在初始化GUI适配器")
            
            # 创建主窗口
            self.root = tk.Tk()
            self.root.title("Chips Battle - 图形界面模式")
            self.root.geometry("800x600")
            self.root.minsize(600, 400)
            
            # 设置窗口图标（如果有的话）
            try:
                self.root.iconbitmap("data/icon.ico")
            except:
                pass
            
            # 创建主框架
            self.main_frame = ttk.Frame(self.root, padding="10")
            self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # 配置网格权重
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            self.main_frame.columnconfigure(0, weight=1)
            self.main_frame.rowconfigure(0, weight=1)
            
            # 创建输出区域
            self._create_output_area()
            
            # 创建进度条区域
            self._create_progress_area()
            
            # 创建输入区域
            self._create_input_area()
            
            # 绑定窗口关闭事件
            self.root.protocol("WM_DELETE_WINDOW", self._on_window_close)
            
            # 显示欢迎信息
            self._show_welcome_message()
            
            self._is_running = True
            self.logger.info("GUI适配器初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"GUI适配器初始化失败: {e}", exc_info=True)
            return False
    
    def _create_output_area(self):
        """创建输出区域"""
        # 创建文本框和滚动条
        output_frame = ttk.Frame(self.main_frame)
        output_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(output_frame)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 创建文本框
        self.output_text = tk.Text(
            output_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            bg="#1e1e1e",
            fg="#d4d4d4",
            font=("Consolas", 10)
        )
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.config(command=self.output_text.yview)
        
        # 配置文本标签
        self._configure_text_tags()
        
        # 设置文本框为只读
        self.output_text.config(state=tk.DISABLED)
    
    def _configure_text_tags(self):
        """配置文本标签"""
        for msg_type, color in self._color_map.items():
            tag_name = msg_type.value
            self.output_text.tag_config(tag_name, foreground=color)
            self._tag_map[msg_type] = tag_name
    
    def _create_progress_area(self):
        """创建进度条区域"""
        progress_frame = ttk.Frame(self.main_frame)
        progress_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        # 进度条标签
        self.progress_label = ttk.Label(progress_frame, text="")
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            length=400
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 默认隐藏
        progress_frame.grid_remove()
    
    def _create_input_area(self):
        """创建输入区域"""
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        self.input_frame.columnconfigure(0, weight=1)
        
        # 输入标签
        input_label = ttk.Label(self.input_frame, text="输入:")
        input_label.grid(row=0, column=0, sticky=tk.W)
        
        # 输入框
        self.input_entry = ttk.Entry(self.input_frame)
        self.input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # 绑定回车键
        self.input_entry.bind('<Return>', self._on_input_submit)
        
        # 设置焦点
        self.input_entry.focus_set()
    
    def _show_welcome_message(self):
        """显示欢迎信息"""
        welcome_text = """╭─────────────────────────────────── 🎮 ───────────────────────────────────╮
│                                                                          │
│  欢迎来到 Chips Battle                                                   │
│  CHIPS BATTLE REMAKE v3.0 Alpha                                          │
│  命令驱动的金融模拟游戏                                                  │
│                                                                          │
╰──────────────────────────────────────────────────────────────────────────╯
"""
        
        self.display_message(Message(welcome_text, MessageType.SYSTEM, timestamp=False))
        self.display_info("图形界面模式已启动，请在下方输入框中输入命令。")
    
    async def cleanup(self):
        """清理GUI资源"""
        try:
            self.logger.info("正在清理GUI适配器")
            
            if self.root:
                self.root.quit()
                self.root.destroy()
                self.root = None
            
            self._is_running = False
            self.logger.info("GUI适配器清理完成")
            
        except Exception as e:
            self.logger.error(f"GUI适配器清理失败: {e}", exc_info=True)
    
    def display_message(self, message: Message):
        """显示消息
        
        Args:
            message: 消息内容
        """
        if not self.output_text:
            return
        
        try:
            # 在主线程中执行UI操作
            def _display():
                self.output_text.config(state=tk.NORMAL)
                
                # 构建消息文本
                text_parts = []
                
                # 添加时间戳
                if message.timestamp:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    text_parts.append(f"[{timestamp}]")
                
                # 添加消息内容
                text_parts.append(message.content)
                
                # 组合并插入
                message_text = " ".join(text_parts) + "\n"
                
                # 获取标签
                tag = self._tag_map.get(message.type, "info")
                
                # 插入文本
                self.output_text.insert(tk.END, message_text, tag)
                
                # 滚动到底部
                self.output_text.see(tk.END)
                
                self.output_text.config(state=tk.DISABLED)
            
            # 在主线程中执行
            if self.root:
                self.root.after(0, _display)
                
        except Exception as e:
            self.logger.error(f"显示消息失败: {e}", exc_info=True)
    
    async def get_input(self, request: InputRequest) -> str:
        """获取用户输入
        
        Args:
            request: 输入请求
            
        Returns:
            用户输入的值
        """
        if not self.root:
            return ""
        
        try:
            # 创建事件对象来等待输入
            input_event = asyncio.Event()
            result_container = {"value": ""}
            
            def _get_input():
                try:
                    if request.input_type == InputType.TEXT:
                        result = simpledialog.askstring(
                            "输入",
                            request.prompt,
                            initialvalue=request.default or ""
                        )
                    elif request.input_type == InputType.PASSWORD:
                        result = simpledialog.askstring(
                            "输入",
                            request.prompt,
                            show='*'
                        )
                    elif request.input_type == InputType.NUMBER:
                        result = simpledialog.askinteger(
                            "输入",
                            request.prompt,
                            initialvalue=int(request.default) if request.default else 0
                        )
                        result = str(result) if result is not None else ""
                    elif request.input_type == InputType.CHOICE:
                        # 创建选择对话框
                        dialog = tk.Toplevel(self.root)
                        dialog.title("选择")
                        dialog.geometry("300x200")
                        
                        result_container["value"] = ""
                        
                        ttk.Label(dialog, text=request.prompt).pack(pady=10)
                        
                        var = tk.StringVar()
                        for choice in request.choices:
                            ttk.Radiobutton(
                                dialog,
                                text=choice,
                                variable=var,
                                value=choice
                            ).pack()
                        
                        def on_ok():
                            result_container["value"] = var.get()
                            dialog.destroy()
                        
                        ttk.Button(dialog, text="确定", command=on_ok).pack(pady=10)
                        
                        dialog.wait_window()
                        result = result_container["value"]
                    elif request.input_type == InputType.CONFIRM:
                        result = messagebox.askyesno(
                            "确认",
                            request.prompt
                        )
                        result = 'y' if result else 'n'
                    else:
                        result = ""
                    
                    result_container["value"] = result or ""
                    
                except Exception as e:
                    self.logger.error(f"获取输入失败: {e}", exc_info=True)
                    result_container["value"] = ""
                finally:
                    # 设置事件，表示输入完成
                    input_event.set()
            
            # 在主线程中执行
            self.root.after(0, _get_input)
            
            # 等待输入完成
            await input_event.wait()
            
            return result_container["value"]
            
        except Exception as e:
            self.logger.error(f"获取用户输入失败: {e}", exc_info=True)
            return ""
    
    def show_progress(self, progress: ProgressInfo):
        """显示进度
        
        Args:
            progress: 进度信息
        """
        if not self.progress_bar or not self.progress_label:
            return
        
        try:
            def _show_progress():
                # 显示进度条框架
                self.progress_bar.master.grid()
                
                # 设置进度条
                self.progress_bar['maximum'] = progress.total
                self.progress_bar['value'] = progress.current
                
                # 设置标签
                percentage = progress.percentage
                self.progress_label.config(
                    text=f"{progress.description}: {progress.current}/{progress.total} ({percentage:.1f}%)"
                )
            
            # 在主线程中执行
            if self.root:
                self.root.after(0, _show_progress)
                
        except Exception as e:
            self.logger.error(f"显示进度失败: {e}", exc_info=True)
    
    def hide_progress(self):
        """隐藏进度条"""
        if not self.progress_bar:
            return
        
        try:
            def _hide_progress():
                self.progress_bar.master.grid_remove()
            
            # 在主线程中执行
            if self.root:
                self.root.after(0, _hide_progress)
                
        except Exception as e:
            self.logger.error(f"隐藏进度条失败: {e}", exc_info=True)
    
    def update_progress(self, current: int, total: int = None):
        """更新进度
        
        Args:
            current: 当前进度
            total: 总进度（可选）
        """
        if not self.progress_bar or not self.progress_label:
            return
        
        try:
            def _update_progress():
                if total is not None:
                    self.progress_bar['maximum'] = total
                
                self.progress_bar['value'] = current
                
                # 更新标签
                max_value = self.progress_bar['maximum']
                percentage = (current / max_value * 100) if max_value > 0 else 0
                current_text = self.progress_label.cget("text")
                description = current_text.split(":")[0] if ":" in current_text else "进度"
                
                self.progress_label.config(
                    text=f"{description}: {current}/{max_value} ({percentage:.1f}%)"
                )
            
            # 在主线程中执行
            if self.root:
                self.root.after(0, _update_progress)
                
        except Exception as e:
            self.logger.error(f"更新进度失败: {e}", exc_info=True)
    
    def clear_screen(self):
        """清空屏幕"""
        if not self.output_text:
            return
        
        try:
            def _clear_screen():
                self.output_text.config(state=tk.NORMAL)
                self.output_text.delete(1.0, tk.END)
                self.output_text.config(state=tk.DISABLED)
            
            # 在主线程中执行
            if self.root:
                self.root.after(0, _clear_screen)
                
        except Exception as e:
            self.logger.error(f"清空屏幕失败: {e}", exc_info=True)
    
    async def run_main_loop(self):
        """运行主循环"""
        if not self.root:
            return
        
        try:
            self._is_running = True
            self.logger.info("GUI主循环开始")
            
            # 触发主循环开始事件
            self.emit_event("main_loop_started")
            
            # 运行tkinter主循环
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"GUI主循环失败: {e}", exc_info=True)
        finally:
            self._is_running = False
            self.logger.info("GUI主循环停止")
            
            # 触发主循环停止事件
            self.emit_event("main_loop_stopped")
    
    def stop_main_loop(self):
        """停止主循环"""
        if self.root:
            self.root.quit()
    
    def _on_window_close(self):
        """窗口关闭事件处理"""
        try:
            # 触发窗口关闭事件
            self.emit_event("window_closing")
            
            # 停止主循环
            self.stop_main_loop()
            
        except Exception as e:
            self.logger.error(f"窗口关闭事件处理失败: {e}", exc_info=True)
    
    def _on_input_submit(self, event):
        """输入提交事件处理
        
        Args:
            event: 事件对象
        """
        try:
            if self.input_entry and self._input_callback:
                input_text = self.input_entry.get()
                self.input_entry.delete(0, tk.END)
                
                # 调用回调函数
                if asyncio.iscoroutinefunction(self._input_callback):
                    # 如果是异步函数，创建任务
                    asyncio.create_task(self._input_callback(input_text))
                else:
                    # 如果是同步函数，直接调用
                    self._input_callback(input_text)
                    
        except Exception as e:
            self.logger.error(f"输入提交事件处理失败: {e}", exc_info=True)
    
    def set_input_callback(self, callback):
        """设置输入回调函数
        
        Args:
            callback: 回调函数
        """
        self._input_callback = callback
    
    def set_input_prompt(self, prompt: str):
        """设置输入提示
        
        Args:
            prompt: 提示文本
        """
        if self.input_frame:
            # 更新输入标签
            for widget in self.input_frame.winfo_children():
                if isinstance(widget, ttk.Label):
                    widget.config(text=prompt)
                    break


class GUIAdapter(UIAdapter):
    """GUI适配器
    
    为图形界面模式提供便捷的适配器类。
    """
    
    def __init__(self):
        ui_interface = TkinterUIAdapter()
        super().__init__(ui_interface)
    
    def set_command_callback(self, callback):
        """设置命令回调函数
        
        Args:
            callback: 命令回调函数
        """
        self.ui.set_input_callback(callback)
    
    def set_command_prompt(self, username: str):
        """设置命令提示符
        
        Args:
            username: 用户名
        """
        prompt = f"{username}@ChipsBattle$ "
        self.ui.set_input_prompt(prompt)
    
    def show_login_dialog(self) -> str:
        """显示登录对话框
        
        Returns:
            用户选择的结果
        """
        # 这里需要在主线程中执行，简化实现
        return "1"  # 默认选择登录现有账户
    
    def show_error_dialog(self, title: str, message: str):
        """显示错误对话框
        
        Args:
            title: 对话框标题
            message: 错误消息
        """
        if self.ui.root:
            self.ui.root.after(0, lambda: messagebox.showerror(title, message))
    
    def show_info_dialog(self, title: str, message: str):
        """显示信息对话框
        
        Args:
            title: 对话框标题
            message: 信息消息
        """
        if self.ui.root:
            self.ui.root.after(0, lambda: messagebox.showinfo(title, message))
    
    def show_warning_dialog(self, title: str, message: str):
        """显示警告对话框
        
        Args:
            title: 对话框标题
            message: 警告消息
        """
        if self.ui.root:
            self.ui.root.after(0, lambda: messagebox.showwarning(title, message))
    
    def add_menu_item(self, menu_name: str, item_name: str, callback):
        """添加菜单项
        
        Args:
            menu_name: 菜单名称
            item_name: 菜单项名称
            callback: 回调函数
        """
        # 这里可以实现菜单功能，简化实现
        pass
    
    def add_toolbar_button(self, button_name: str, callback, icon=None):
        """添加工具栏按钮
        
        Args:
            button_name: 按钮名称
            callback: 回调函数
            icon: 图标（可选）
        """
        # 这里可以实现工具栏功能，简化实现
        pass
    
    def update_status_bar(self, text: str):
        """更新状态栏
        
        Args:
            text: 状态文本
        """
        # 这里可以实现状态栏功能，简化实现
        pass