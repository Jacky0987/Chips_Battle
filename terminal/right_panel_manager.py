# -*- coding: utf-8 -*-
"""
Chips Battle Remake v3.0 Alpha - 右侧面板管理器
管理各种功能面板的显示和切换
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Any
from datetime import datetime
import threading
import time

class RightPanelManager:
    """右侧面板管理器"""
    
    def __init__(self, parent: tk.Frame, main_app):
        self.parent = parent
        self.main_app = main_app
        self.theme_manager = main_app.theme_manager
        
        # 面板字典
        self.panels: Dict[str, tk.Frame] = {}
        self.current_panel: Optional[str] = None
        
        # 数据更新线程
        self.update_thread = None
        self.update_running = False
        
        # 添加主循环状态标志
        self.mainloop_started = False
        
        # 创建界面
        self._create_ui()
        
        # 默认显示市场面板
        self.show_panel('market')
        
        # 启动数据更新
        self._start_data_update()
        
    def _create_ui(self):
        """创建用户界面"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 主容器
        self.main_frame = tk.Frame(
            self.parent,
            bg=colors['bg_primary']
        )
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 顶部标签栏
        self._create_tab_bar()
        
        # 内容区域
        self.content_frame = tk.Frame(
            self.main_frame,
            bg=colors['bg_primary']
        )
        self.content_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 创建各个面板
        self._create_market_panel()
        self._create_portfolio_panel()
        self._create_news_panel()
        self._create_analysis_panel()
        
    def _create_tab_bar(self):
        """创建标签栏"""
        colors = self.theme_manager.get_theme()['colors']
        
        self.tab_frame = tk.Frame(
            self.main_frame,
            bg=colors['bg_secondary'],
            height=40
        )
        self.tab_frame.pack(side=tk.TOP, fill=tk.X)
        self.tab_frame.pack_propagate(False)
        
        # 标签按钮
        tabs = [
            ('market', '📈 市场', '实时市场数据'),
            ('portfolio', '💼 投资组合', '我的持仓'),
            ('news', '📰 新闻', '财经新闻'),
            ('analysis', '📊 分析', '技术分析')
        ]
        
        self.tab_buttons = {}
        
        for tab_id, tab_text, tooltip in tabs:
            btn = tk.Button(
                self.tab_frame,
                text=tab_text,
                bg=colors['btn_secondary'],
                fg=colors['fg_primary'],
                activebackground=colors['btn_hover'],
                font=('Consolas', 9, 'bold'),
                borderwidth=0,
                relief=tk.FLAT,
                command=lambda t=tab_id: self.show_panel(t),
                cursor='hand2'
            )
            btn.pack(side=tk.LEFT, padx=2, pady=5, fill=tk.Y)
            
            self.tab_buttons[tab_id] = btn
            self._create_tooltip(btn, tooltip)
            
    def _create_market_panel(self):
        """创建市场面板"""
        colors = self.theme_manager.get_theme()['colors']
        
        panel = tk.Frame(self.content_frame, bg=colors['bg_primary'])
        
        # 标题
        title_frame = tk.Frame(panel, bg=colors['bg_secondary'], height=35)
        title_frame.pack(side=tk.TOP, fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="📈 实时市场数据",
            bg=colors['bg_secondary'],
            fg=colors['fg_primary'],
            font=('Consolas', 11, 'bold')
        )
        title_label.pack(side=tk.LEFT, pady=8, padx=10)
        
        # 刷新按钮
        refresh_btn = tk.Button(
            title_frame,
            text="🔄",
            bg=colors['btn_secondary'],
            fg=colors['fg_primary'],
            font=('Segoe UI Symbol', 10),
            borderwidth=0,
            relief=tk.FLAT,
            width=3,
            command=self._refresh_market_data,
            cursor='hand2'
        )
        refresh_btn.pack(side=tk.RIGHT, pady=6, padx=10)
        
        # 滚动区域
        canvas = tk.Canvas(panel, bg=colors['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(panel, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=colors['bg_primary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")
        
        # 市场数据表格
        self.market_frame = scrollable_frame
        self._create_market_table()
        
        self.panels['market'] = panel
        
    def _create_portfolio_panel(self):
        """创建投资组合面板"""
        colors = self.theme_manager.get_theme()['colors']
        
        panel = tk.Frame(self.content_frame, bg=colors['bg_primary'])
        
        # 标题
        title_frame = tk.Frame(panel, bg=colors['bg_secondary'], height=35)
        title_frame.pack(side=tk.TOP, fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="💼 我的投资组合",
            bg=colors['bg_secondary'],
            fg=colors['fg_primary'],
            font=('Consolas', 11, 'bold')
        )
        title_label.pack(side=tk.LEFT, pady=8, padx=10)
        
        # 总览区域
        overview_frame = tk.Frame(panel, bg=colors['bg_tertiary'])
        overview_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # 总资产
        self.total_assets_label = tk.Label(
            overview_frame,
            text="总资产: ¥0.00",
            bg=colors['bg_tertiary'],
            fg=colors['fg_primary'],
            font=('Consolas', 12, 'bold')
        )
        self.total_assets_label.pack(pady=10)
        
        # 今日盈亏
        self.daily_pnl_label = tk.Label(
            overview_frame,
            text="今日盈亏: ¥0.00 (0.00%)",
            bg=colors['bg_tertiary'],
            fg=colors['fg_primary'],
            font=('Consolas', 10)
        )
        self.daily_pnl_label.pack(pady=(0, 10))
        
        # 持仓列表
        holdings_frame = tk.Frame(panel, bg=colors['bg_primary'])
        holdings_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 表头
        header_frame = tk.Frame(holdings_frame, bg=colors['bg_secondary'], height=30)
        header_frame.pack(side=tk.TOP, fill=tk.X)
        header_frame.pack_propagate(False)
        
        headers = ['股票代码', '持仓', '成本', '现价', '盈亏']
        for i, header in enumerate(headers):
            label = tk.Label(
                header_frame,
                text=header,
                bg=colors['bg_secondary'],
                fg=colors['fg_primary'],
                font=('Consolas', 9, 'bold')
            )
            label.place(relx=i/5, rely=0.5, anchor='w', x=10)
            
        # 持仓数据区域
        self.holdings_frame = tk.Frame(holdings_frame, bg=colors['bg_primary'])
        self.holdings_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.panels['portfolio'] = panel
        
    def _create_news_panel(self):
        """创建新闻面板"""
        colors = self.theme_manager.get_theme()['colors']
        
        panel = tk.Frame(self.content_frame, bg=colors['bg_primary'])
        
        # 标题
        title_frame = tk.Frame(panel, bg=colors['bg_secondary'], height=35)
        title_frame.pack(side=tk.TOP, fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="📰 财经新闻",
            bg=colors['bg_secondary'],
            fg=colors['fg_primary'],
            font=('Consolas', 11, 'bold')
        )
        title_label.pack(side=tk.LEFT, pady=8, padx=10)
        
        # 新闻列表
        news_frame = tk.Frame(panel, bg=colors['bg_primary'])
        news_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 滚动文本区域
        self.news_text = tk.Text(
            news_frame,
            bg=colors['bg_primary'],
            fg=colors['fg_primary'],
            font=('Consolas', 9),
            wrap=tk.WORD,
            state=tk.DISABLED,
            borderwidth=0,
            highlightthickness=0
        )
        
        news_scrollbar = ttk.Scrollbar(
            news_frame,
            orient=tk.VERTICAL,
            command=self.news_text.yview
        )
        
        self.news_text.configure(yscrollcommand=news_scrollbar.set)
        
        self.news_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        news_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 配置新闻文本样式
        self.news_text.tag_configure(
            'title',
            foreground=colors['accent_primary'],
            font=('Consolas', 10, 'bold')
        )
        
        self.news_text.tag_configure(
            'time',
            foreground=colors['fg_muted'],
            font=('Consolas', 8)
        )
        
        self.panels['news'] = panel
        
    def _create_analysis_panel(self):
        """创建分析面板"""
        colors = self.theme_manager.get_theme()['colors']
        
        panel = tk.Frame(self.content_frame, bg=colors['bg_primary'])
        
        # 标题
        title_frame = tk.Frame(panel, bg=colors['bg_secondary'], height=35)
        title_frame.pack(side=tk.TOP, fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="📊 技术分析",
            bg=colors['bg_secondary'],
            fg=colors['fg_primary'],
            font=('Consolas', 11, 'bold')
        )
        title_label.pack(side=tk.LEFT, pady=8, padx=10)
        
        # 分析内容
        analysis_frame = tk.Frame(panel, bg=colors['bg_primary'])
        analysis_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 占位文本
        placeholder_label = tk.Label(
            analysis_frame,
            text="📊 技术分析功能开发中...\n\n将包含:\n• K线图表\n• 技术指标\n• 趋势分析\n• 交易信号",
            bg=colors['bg_primary'],
            fg=colors['fg_muted'],
            font=('Consolas', 10),
            justify=tk.LEFT
        )
        placeholder_label.pack(expand=True)
        
        self.panels['analysis'] = panel
        
    def _create_market_table(self):
        """创建市场数据表格"""
        colors = self.theme_manager.get_theme()['colors']
        
        # 清空现有内容
        for widget in self.market_frame.winfo_children():
            widget.destroy()
            
        # 表头
        header_frame = tk.Frame(self.market_frame, bg=colors['bg_secondary'], height=30)
        header_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 5))
        header_frame.pack_propagate(False)
        
        headers = ['代码', '名称', '现价', '涨跌', '涨跌幅']
        for i, header in enumerate(headers):
            label = tk.Label(
                header_frame,
                text=header,
                bg=colors['bg_secondary'],
                fg=colors['fg_primary'],
                font=('Consolas', 9, 'bold')
            )
            label.place(relx=i/5, rely=0.5, anchor='w', x=5)
            
        # 模拟市场数据
        market_data = [
            ('000001', '平安银行', '12.34', '+0.56', '+4.76%'),
            ('000002', '万科A', '23.45', '-0.23', '-0.97%'),
            ('600000', '浦发银行', '8.76', '+0.12', '+1.39%'),
            ('600036', '招商银行', '45.67', '+1.23', '+2.77%'),
            ('000858', '五粮液', '178.90', '-2.34', '-1.29%'),
            ('600519', '贵州茅台', '1876.54', '+23.45', '+1.27%'),
            ('000725', '京东方A', '4.32', '+0.08', '+1.89%'),
            ('002415', '海康威视', '34.56', '-0.67', '-1.90%')
        ]
        
        self.market_rows = []
        
        for i, (code, name, price, change, change_pct) in enumerate(market_data):
            row_frame = tk.Frame(
                self.market_frame,
                bg=colors['bg_tertiary'] if i % 2 == 0 else colors['bg_primary'],
                height=25
            )
            row_frame.pack(side=tk.TOP, fill=tk.X, pady=1)
            row_frame.pack_propagate(False)
            
            # 确定颜色
            if change.startswith('+'):
                change_color = colors['success']
            elif change.startswith('-'):
                change_color = colors['error']
            else:
                change_color = colors['fg_primary']
                
            # 数据列
            data = [code, name, price, change, change_pct]
            for j, value in enumerate(data):
                color = change_color if j >= 3 else colors['fg_primary']
                
                label = tk.Label(
                    row_frame,
                    text=value,
                    bg=row_frame['bg'],
                    fg=color,
                    font=('Consolas', 8)
                )
                label.place(relx=j/5, rely=0.5, anchor='w', x=5)
                
            self.market_rows.append(row_frame)
            
            # 绑定点击事件
            row_frame.bind('<Button-1>', lambda e, c=code: self._on_stock_click(c))
            for child in row_frame.winfo_children():
                child.bind('<Button-1>', lambda e, c=code: self._on_stock_click(c))
                
    def _create_tooltip(self, widget: tk.Widget, text: str):
        """创建工具提示"""
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
            
            tooltip.after(2000, tooltip.destroy)
            
        widget.bind('<Enter>', show_tooltip)
        
    def show_panel(self, panel_id: str):
        """显示指定面板"""
        if panel_id not in self.panels:
            return
            
        # 隐藏当前面板
        if self.current_panel and self.current_panel in self.panels:
            self.panels[self.current_panel].pack_forget()
            
        # 显示新面板
        self.panels[panel_id].pack(fill=tk.BOTH, expand=True)
        self.current_panel = panel_id
        
        # 更新标签按钮状态
        self._update_tab_buttons(panel_id)
        
        # 刷新面板数据
        self._refresh_panel_data(panel_id)
        
    def _update_tab_buttons(self, active_tab: str):
        """更新标签按钮状态"""
        colors = self.theme_manager.get_theme()['colors']
        
        for tab_id, button in self.tab_buttons.items():
            if tab_id == active_tab:
                button.configure(
                    bg=colors['accent_primary'],
                    fg=colors['fg_bright']
                )
            else:
                button.configure(
                    bg=colors['btn_secondary'],
                    fg=colors['fg_primary']
                )
                
    def _refresh_panel_data(self, panel_id: str):
        """刷新面板数据"""
        if panel_id == 'market':
            self._refresh_market_data()
        elif panel_id == 'portfolio':
            self._refresh_portfolio_data()
        elif panel_id == 'news':
            self._refresh_news_data()
            
    def _refresh_market_data(self):
        """刷新市场数据"""
        # 这里应该调用实际的市场数据API
        # 目前使用模拟数据
        self._create_market_table()
        
    def _refresh_portfolio_data(self):
        """刷新投资组合数据"""
        # 这里应该调用实际的投资组合API
        colors = self.theme_manager.get_theme()['colors']
        
        # 更新总资产
        self.total_assets_label.configure(text="总资产: ¥125,678.90")
        
        # 更新今日盈亏
        self.daily_pnl_label.configure(
            text="今日盈亏: +¥2,345.67 (+1.90%)",
            fg=colors['success']
        )
        
        # 清空持仓列表
        for widget in self.holdings_frame.winfo_children():
            widget.destroy()
            
        # 模拟持仓数据
        holdings = [
            ('000001', '1000', '11.50', '12.34', '+840'),
            ('600036', '500', '42.30', '45.67', '+1685'),
            ('000858', '100', '185.20', '178.90', '-630')
        ]
        
        for i, (code, shares, cost, current, pnl) in enumerate(holdings):
            row_frame = tk.Frame(
                self.holdings_frame,
                bg=colors['bg_tertiary'] if i % 2 == 0 else colors['bg_primary'],
                height=25
            )
            row_frame.pack(side=tk.TOP, fill=tk.X, pady=1)
            row_frame.pack_propagate(False)
            
            # 盈亏颜色
            pnl_color = colors['success'] if pnl.startswith('+') else colors['error']
            
            data = [code, shares, cost, current, pnl]
            for j, value in enumerate(data):
                color = pnl_color if j == 4 else colors['fg_primary']
                
                label = tk.Label(
                    row_frame,
                    text=value,
                    bg=row_frame['bg'],
                    fg=color,
                    font=('Consolas', 8)
                )
                label.place(relx=j/5, rely=0.5, anchor='w', x=10)
                
    def _refresh_news_data(self):
        """刷新新闻数据"""
        # 这里应该调用实际的新闻API
        self.news_text.configure(state=tk.NORMAL)
        self.news_text.delete(1.0, tk.END)
        
        # 模拟新闻数据
        news_items = [
            ("A股三大指数集体收涨", "14:30", "今日A股市场表现强劲，上证指数涨1.2%，深证成指涨1.5%，创业板指涨2.1%。"),
            ("央行降准释放流动性", "13:45", "央行宣布下调存款准备金率0.25个百分点，释放长期资金约5000亿元。"),
            ("科技股领涨市场", "12:30", "科技板块今日表现亮眼，多只科技股涨停，市场情绪高涨。"),
            ("外资持续流入A股", "11:15", "北向资金今日净流入超50亿元，显示外资对A股市场信心增强。")
        ]
        
        for title, time_str, content in news_items:
            self.news_text.insert(tk.END, f"📰 {title}\n", 'title')
            self.news_text.insert(tk.END, f"⏰ {time_str}\n", 'time')
            self.news_text.insert(tk.END, f"{content}\n\n")
            
        self.news_text.configure(state=tk.DISABLED)
        
    def _on_stock_click(self, stock_code: str):
        """处理股票点击事件"""
        # 在终端中显示股票信息
        if hasattr(self.main_app, 'terminal_panel'):
            self.main_app.terminal_panel.append_output(
                f"查询股票: {stock_code}",
                'system'
            )
            # 这里可以调用实际的股票查询命令
            self.main_app.execute_command(f"stock {stock_code}")
            
    def _start_data_update(self):
        """启动数据更新线程"""
        self.update_running = True
        self.update_thread = threading.Thread(target=self._data_update_loop, daemon=True)
        self.update_thread.start()
        
    def _data_update_loop(self):
        """数据更新循环"""
        while self.update_running:
            try:
                # 每30秒更新一次数据
                time.sleep(30)
                
                if self.current_panel and self.update_running:
                    # 检查主循环是否已启动
                    if self.mainloop_started:
                        # 在主线程中更新UI
                        self.main_frame.after(0, lambda: self._refresh_panel_data(self.current_panel))
                    else:
                        # 主循环未启动，跳过更新
                        print("[DEBUG] Mainloop not started, skipping panel data update")
                    
            except Exception as e:
                print(f"数据更新错误: {e}")
                
    def stop_data_update(self):
        """停止数据更新"""
        self.update_running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1)
            
    def set_mainloop_started(self):
        """设置主循环已启动标志"""
        self.mainloop_started = True
        print("[DEBUG] RightPanelManager mainloop started")
        
    def toggle_visibility(self):
        """切换面板可见性"""
        if self.main_frame.winfo_viewable():
            self.main_frame.pack_forget()
        else:
            self.main_frame.pack(fill=tk.BOTH, expand=True)
            
    def get_current_panel(self) -> Optional[str]:
        """获取当前面板ID"""
        return self.current_panel
        
    def add_custom_panel(self, panel_id: str, panel_frame: tk.Frame, tab_text: str):
        """添加自定义面板"""
        self.panels[panel_id] = panel_frame
        
        # 添加标签按钮
        colors = self.theme_manager.get_theme()['colors']
        
        btn = tk.Button(
            self.tab_frame,
            text=tab_text,
            bg=colors['btn_secondary'],
            fg=colors['fg_primary'],
            activebackground=colors['btn_hover'],
            font=('Consolas', 9, 'bold'),
            borderwidth=0,
            relief=tk.FLAT,
            command=lambda: self.show_panel(panel_id),
            cursor='hand2'
        )
        btn.pack(side=tk.LEFT, padx=2, pady=5, fill=tk.Y)
        
        self.tab_buttons[panel_id] = btn