import tkinter as tk
from tkinter import ttk, font
from datetime import datetime
import threading
import time

class ProfessionalTerminal:
    """
    💻 JackyCoin 专业金融终端界面
    保持CLI核心理念，增强专业金融特色
    """

    def __init__(self, main_app):
        self.app = main_app
        self.root = main_app.root
        self.setup_colors()
        self.setup_fonts()
        self.setup_terminal_ui()
        self.start_live_updates()

    def setup_colors(self):
        """🎨 专业金融终端配色方案"""
        self.colors = {
            'bg_primary': '#0A0A0A',      # 主背景 - 深黑
            'bg_secondary': '#1A1A1A',    # 次要背景 - 暗灰
            'bg_accent': '#2A2A2A',       # 强调背景
            'text_primary': '#00FF41',    # 主文本 - 矩阵绿
            'text_secondary': '#FFFFFF',   # 次要文本 - 白色
            'text_warning': '#FFA500',    # 警告文本 - 橙色
            'text_error': '#FF4444',      # 错误文本 - 红色
            'text_info': '#4AAFE7',       # 信息文本 - 蓝色
            'accent_gold': '#FFD700',     # 金色强调
            'accent_cyan': '#00FFFF',     # 青色强调
            'border': '#333333',          # 边框颜色
            'positive': '#00FF00',        # 上涨绿
            'negative': '#FF0000',        # 下跌红
            'neutral': '#FFFF00'          # 中性黄
        }

    def setup_fonts(self):
        """🔤 设置专业字体"""
        self.fonts = {
            'mono_large': font.Font(family="Consolas", size=12, weight="bold"),
            'mono_medium': font.Font(family="Consolas", size=10),
            'mono_small': font.Font(family="Consolas", size=9),
            'header': font.Font(family="Consolas", size=14, weight="bold"),
            'ticker': font.Font(family="Consolas", size=11, weight="bold")
        }

    def setup_terminal_ui(self):
        """🖥️ 设置专业终端界面"""
        # 清空根窗口
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 设置窗口
        self.root.configure(bg=self.colors['bg_primary'])
        self.root.title("JackyCoin Professional Trading Terminal v2.0")
        
        # 创建主容器
        self.main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # 创建顶部工具栏
        self.create_toolbar()
        
        # 创建主要布局
        self.create_main_layout()
        
        # 创建状态栏
        self.create_status_bar()

    def create_toolbar(self):
        """📊 创建专业工具栏"""
        toolbar = tk.Frame(self.main_container, bg=self.colors['bg_secondary'], height=40)
        toolbar.pack(fill=tk.X, pady=(0, 2))
        toolbar.pack_propagate(False)
        
        # 左侧：系统标识和连接状态
        left_toolbar = tk.Frame(toolbar, bg=self.colors['bg_secondary'])
        left_toolbar.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # 系统标识
        system_label = tk.Label(left_toolbar, 
                               text="📈 JACKY TERMINAL", 
                               font=self.fonts['header'],
                               fg=self.colors['accent_gold'], 
                               bg=self.colors['bg_secondary'])
        system_label.pack(side=tk.LEFT, pady=8)
        
        # 连接状态指示器
        self.connection_indicator = tk.Label(left_toolbar, 
                                           text="● LIVE", 
                                           font=self.fonts['mono_medium'],
                                           fg=self.colors['positive'], 
                                           bg=self.colors['bg_secondary'])
        self.connection_indicator.pack(side=tk.LEFT, padx=(20, 0), pady=8)
        
        # 中间：快速导航按钮
        nav_frame = tk.Frame(toolbar, bg=self.colors['bg_secondary'])
        nav_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=20)
        
        nav_buttons = [
            ("MARKET", "market"),
            ("PORTFOLIO", "portfolio"),
            ("ANALYSIS", "sector"),
            ("BANK", "bank"),
            ("NEWS", "news")
        ]
        
        for i, (text, cmd) in enumerate(nav_buttons):
            btn = tk.Button(nav_frame, text=text,
                           font=self.fonts['mono_small'],
                           fg=self.colors['text_info'],
                           bg=self.colors['bg_accent'],
                           activebackground=self.colors['border'],
                           activeforeground=self.colors['accent_cyan'],
                           relief=tk.FLAT,
                           command=lambda c=cmd: self.execute_command(c),
                           width=8)
            btn.pack(side=tk.LEFT, padx=2, pady=5)
        
        # 右侧：用户信息和时钟
        right_toolbar = tk.Frame(toolbar, bg=self.colors['bg_secondary'])
        right_toolbar.pack(side=tk.RIGHT, fill=tk.Y, padx=10)
        
        # 用户信息
        self.user_label = tk.Label(right_toolbar, 
                                  text="USER: LOADING...", 
                                  font=self.fonts['mono_small'],
                                  fg=self.colors['text_secondary'], 
                                  bg=self.colors['bg_secondary'])
        self.user_label.pack(side=tk.RIGHT, pady=8)
        
        # 时钟
        self.clock_label = tk.Label(right_toolbar, 
                                   text="", 
                                   font=self.fonts['mono_medium'],
                                   fg=self.colors['accent_cyan'], 
                                   bg=self.colors['bg_secondary'])
        self.clock_label.pack(side=tk.RIGHT, padx=(0, 20), pady=8)

    def create_main_layout(self):
        """🏗️ 创建主要布局"""
        # 创建主窗格
        main_paned = tk.PanedWindow(self.main_container, orient=tk.HORIZONTAL, 
                                   bg=self.colors['bg_primary'], sashwidth=3,
                                   sashrelief=tk.RAISED)
        main_paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：终端区域 (占60%)
        self.create_terminal_area(main_paned)
        
        # 右侧：信息面板区域 (占40%)
        self.create_info_panels(main_paned)

    def create_terminal_area(self, parent):
        """💻 创建终端区域"""
        terminal_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        parent.add(terminal_frame, width=800, minsize=600)
        
        # 终端标题栏
        terminal_header = tk.Frame(terminal_frame, bg=self.colors['bg_secondary'], height=30)
        terminal_header.pack(fill=tk.X, pady=(0, 2))
        terminal_header.pack_propagate(False)
        
        terminal_title = tk.Label(terminal_header, 
                                 text="💻 COMMAND TERMINAL", 
                                 font=self.fonts['mono_medium'],
                                 fg=self.colors['accent_gold'], 
                                 bg=self.colors['bg_secondary'])
        terminal_title.pack(side=tk.LEFT, padx=10, pady=5)
        
        # 终端输出区域
        output_frame = tk.Frame(terminal_frame, bg=self.colors['bg_primary'])
        output_frame.pack(fill=tk.BOTH, expand=True, padx=2)
        
        # 滚动条
        scrollbar = tk.Scrollbar(output_frame, bg=self.colors['bg_accent'], 
                                troughcolor=self.colors['bg_primary'],
                                activebackground=self.colors['border'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 输出文本区域
        self.output_text = tk.Text(output_frame,
                                  font=self.fonts['mono_medium'],
                                  bg=self.colors['bg_primary'],
                                  fg=self.colors['text_primary'],
                                  insertbackground=self.colors['accent_cyan'],
                                  selectbackground=self.colors['bg_accent'],
                                  selectforeground=self.colors['text_secondary'],
                                  yscrollcommand=scrollbar.set,
                                  wrap=tk.WORD,
                                  state=tk.DISABLED,
                                  relief=tk.FLAT,
                                  bd=1)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.output_text.yview)
        
        # 命令输入区域
        self.create_command_input(terminal_frame)

    def create_command_input(self, parent):
        """⌨️ 创建命令输入区域"""
        input_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=35)
        input_frame.pack(fill=tk.X, pady=(2, 0))
        input_frame.pack_propagate(False)
        
        # 提示符
        prompt_label = tk.Label(input_frame, 
                               text="jacky@terminal:~$ ",
                               font=self.fonts['mono_medium'],
                               fg=self.colors['accent_gold'], 
                               bg=self.colors['bg_secondary'])
        prompt_label.pack(side=tk.LEFT, padx=(10, 5), pady=7)
        
        # 命令输入框
        self.command_entry = tk.Entry(input_frame,
                                     font=self.fonts['mono_medium'],
                                     bg=self.colors['bg_primary'],
                                     fg=self.colors['text_primary'],
                                     insertbackground=self.colors['accent_cyan'],
                                     selectbackground=self.colors['bg_accent'],
                                     selectforeground=self.colors['text_secondary'],
                                     relief=tk.FLAT,
                                     bd=1)
        self.command_entry.pack(fill=tk.X, expand=True, padx=(0, 10), pady=7)
        self.command_entry.focus()
        
        # 初始化命令历史
        self.command_history = []
        self.history_index = -1
        
        # 绑定命令历史快捷键
        self.command_entry.bind('<Up>', self.history_up)
        self.command_entry.bind('<Down>', self.history_down)
        self.command_entry.bind('<Return>', self.handle_command_input)

    def create_info_panels(self, parent):
        """📋 创建信息面板区域"""
        info_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        parent.add(info_frame, width=500, minsize=400)
        
        # 创建垂直分割的面板
        info_paned = tk.PanedWindow(info_frame, orient=tk.VERTICAL, 
                                   bg=self.colors['bg_primary'], sashwidth=3)
        info_paned.pack(fill=tk.BOTH, expand=True)
        
        # 上部：实时数据面板
        self.create_realtime_panel(info_paned)
        
        # 中部：投资组合面板
        self.create_portfolio_panel(info_paned)
        
        # 下部：市场动态面板
        self.create_market_events_panel(info_paned)

    def create_realtime_panel(self, parent):
        """📊 创建实时数据面板"""
        realtime_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        parent.add(realtime_frame, height=200, minsize=150)
        
        # 面板标题
        header = tk.Frame(realtime_frame, bg=self.colors['bg_secondary'], height=25)
        header.pack(fill=tk.X, pady=(0, 2))
        header.pack_propagate(False)
        
        title = tk.Label(header, text="📊 REAL-TIME DATA", 
                        font=self.fonts['mono_medium'],
                        fg=self.colors['accent_cyan'], 
                        bg=self.colors['bg_secondary'])
        title.pack(side=tk.LEFT, padx=10, pady=3)
        
        # 实时数据显示区域
        self.realtime_text = tk.Text(realtime_frame,
                                    font=self.fonts['mono_small'],
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_secondary'],
                                    state=tk.DISABLED,
                                    relief=tk.FLAT,
                                    wrap=tk.WORD)
        self.realtime_text.pack(fill=tk.BOTH, expand=True, padx=2)

    def create_portfolio_panel(self, parent):
        """💼 创建投资组合面板"""
        portfolio_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        parent.add(portfolio_frame, height=200, minsize=150)
        
        # 面板标题
        header = tk.Frame(portfolio_frame, bg=self.colors['bg_secondary'], height=25)
        header.pack(fill=tk.X, pady=(0, 2))
        header.pack_propagate(False)
        
        title = tk.Label(header, text="💼 PORTFOLIO STATUS", 
                        font=self.fonts['mono_medium'],
                        fg=self.colors['accent_gold'], 
                        bg=self.colors['bg_secondary'])
        title.pack(side=tk.LEFT, padx=10, pady=3)
        
        # 投资组合显示区域
        self.portfolio_text = tk.Text(portfolio_frame,
                                    font=self.fonts['mono_small'],
                                    bg=self.colors['bg_secondary'],
                                    fg=self.colors['text_secondary'],
                                    state=tk.DISABLED,
                                    relief=tk.FLAT,
                                    wrap=tk.WORD)
        self.portfolio_text.pack(fill=tk.BOTH, expand=True, padx=2)

    def create_market_events_panel(self, parent):
        """🔥 创建市场动态面板"""
        events_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        parent.add(events_frame, height=150, minsize=100)
        
        # 面板标题
        header = tk.Frame(events_frame, bg=self.colors['bg_secondary'], height=25)
        header.pack(fill=tk.X, pady=(0, 2))
        header.pack_propagate(False)
        
        title = tk.Label(header, text="🔥 MARKET PULSE", 
                        font=self.fonts['mono_medium'],
                        fg=self.colors['text_warning'], 
                        bg=self.colors['bg_secondary'])
        title.pack(side=tk.LEFT, padx=10, pady=3)
        
        # 市场动态显示区域
        self.events_text = tk.Text(events_frame,
                                  font=self.fonts['mono_small'],
                                  bg=self.colors['bg_secondary'],
                                  fg=self.colors['text_warning'],
                                  state=tk.DISABLED,
                                  relief=tk.FLAT,
                                  wrap=tk.WORD)
        self.events_text.pack(fill=tk.BOTH, expand=True, padx=2)

    def start_live_updates(self):
        """🔄 启动实时更新"""
        self.update_clock()
        self.update_live_data()

    def update_clock(self):
        """🕒 更新时钟"""
        current_time = datetime.now().strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        if hasattr(self, 'clock_label'):
            self.clock_label.config(text=f"{current_date} {current_time}")
        
        # 每秒更新
        self.root.after(1000, self.update_clock)

    def update_live_data(self):
        """📈 更新实时数据"""
        if hasattr(self.app, 'user_manager') and hasattr(self.app.user_manager, 'current_user') and self.app.user_manager.current_user:
            # 更新用户信息
            user = self.app.user_manager.current_user
            self.user_label.config(text=f"USER: {user.upper()}")
            
            # 更新实时数据面板
            self.update_realtime_data()
            
            # 更新投资组合面板
            self.update_portfolio_data()

        # 每5秒更新一次
        self.root.after(5000, self.update_live_data)

    def update_realtime_data(self):
        """📊 更新实时数据显示"""
        if not hasattr(self, 'realtime_text'):
            return
            
        data = self.get_market_summary()
        
        self.realtime_text.config(state=tk.NORMAL)
        self.realtime_text.delete(1.0, tk.END)
        self.realtime_text.insert(tk.END, data)
        self.realtime_text.config(state=tk.DISABLED)

    def update_portfolio_data(self):
        """更新投资组合面板数据"""
        try:
            portfolio_summary = self.get_portfolio_summary()
            
            # 更新投资组合面板文本
            if hasattr(self, 'portfolio_text'):
                # 临时设置为可编辑状态
                self.portfolio_text.config(state=tk.NORMAL)
                
                # 清空并插入新内容
                self.portfolio_text.delete(1.0, tk.END)
                self.portfolio_text.insert(1.0, portfolio_summary)
                
                # 设置为只读状态，防止用户编辑
                self.portfolio_text.config(state=tk.DISABLED)
                
                # 确保滚动到顶部显示最新内容
                self.portfolio_text.see(1.0)
                
        except Exception as e:
            print(f"Update portfolio data error: {e}")

    def get_market_summary(self):
        """📊 获取市场摘要"""
        try:
            # 获取真实的市场数据
            market_data = ""
            
            # 从应用获取市场数据
            if hasattr(self.app, 'market_data') and hasattr(self.app.market_data, 'stocks'):
                stocks = self.app.market_data.stocks
                
                # 计算涨跌统计
                gainers = []
                losers = []
                
                for symbol, data in stocks.items():
                    # 计算百分比变化
                    change_abs = data.get('change', 0.0)
                    current_price = data.get('price', 0.0)
                    if current_price > 0 and change_abs != 0:
                        change_pct = (change_abs / (current_price - change_abs)) * 100
                        if change_pct > 0:
                            gainers.append((symbol, change_pct))
                        elif change_pct < 0:
                            losers.append((symbol, change_pct))
                
                # 排序获取Top5
                gainers.sort(key=lambda x: x[1], reverse=True)
                losers.sort(key=lambda x: x[1])
                
                # 构建市场摘要
                market_data = "═══ MARKET STATUS ═════\n"
                market_data += f" 📊 Total Stocks: {len(stocks)}\n"
                market_data += f" 📈 Gainers: {len(gainers)}\n"
                market_data += f" 📉 Losers: {len(losers)}\n"
                
                market_data += "═══ TOP MOVERS ════════\n"
                
                # 显示前3涨幅
                for i, (symbol, change) in enumerate(gainers[:3]):
                    market_data += f" 📈 {symbol:<6} {change:+.1f}%\n"
                
                # 显示前2跌幅
                for i, (symbol, change) in enumerate(losers[:2]):
                    market_data += f" 📉 {symbol:<6} {change:+.1f}%\n"
                
                # 获取行业统计
                sectors = {}
                for symbol, data in stocks.items():
                    sector = data.get('sector', '其他')
                    if sector not in sectors:
                        sectors[sector] = {'count': 0, 'total_change': 0}
                    sectors[sector]['count'] += 1
                    
                    # 计算百分比变化
                    change_abs = data.get('change', 0.0)
                    current_price = data.get('price', 0.0)
                    if current_price > 0 and change_abs != 0:
                        change_pct = (change_abs / (current_price - change_abs)) * 100
                        sectors[sector]['total_change'] += change_pct
                
                market_data += "═══ SECTORS ═══════════\n"
                for sector, info in list(sectors.items())[:3]:
                    avg_change = info['total_change'] / info['count'] if info['count'] > 0 else 0
                    icon = "🔥" if avg_change > 0 else "❄️" if avg_change < 0 else "💼"
                    market_data += f" {icon} {sector[:8]:<8} {avg_change:+.1f}%\n"
                
                market_data += "═══════════════════════"
                
                return market_data
            
        except Exception as e:
            print(f"Market summary error: {e}")
        
        # 如果无法获取真实数据，返回默认摘要
        return """═══ MARKET STATUS ═════
 📊 Loading market data...
 🔄 Please wait...
═══════════════════════"""

    def get_portfolio_summary(self):
        """💼 获取投资组合摘要"""
        try:
            if hasattr(self.app, 'user_manager') and self.app.user_manager.current_user:
                user_data = self.app.user_manager.get_user_data()
                if user_data and 'portfolio' in user_data:
                    portfolio = user_data['portfolio']
                    total_value = self.app.cash
                    holdings_count = 0
                    
                    # 计算持仓价值
                    for symbol, position in portfolio.items():
                        if symbol != 'pending_orders' and isinstance(position, dict):
                            quantity = position.get('quantity', 0)
                            if quantity > 0:
                                if symbol in self.app.market_data.stocks:
                                    current_price = self.app.market_data.stocks[symbol]['price']
                                    total_value += current_price * quantity
                                    holdings_count += 1
                    
                    # 计算大宗商品持仓价值
                    commodity_holdings = 0
                    if hasattr(self.app, 'commodity_trading'):
                        commodity_positions = self.app.commodity_trading.commodity_manager.get_user_positions(self.app.user_manager.current_user)
                        for position in commodity_positions:
                            holdings_count += 1
                            commodity_holdings += 1
                    
                    # 获取最近交易记录
                    recent_trades = ""
                    if 'transaction_history' in user_data and user_data['transaction_history']:
                        # 获取最近5笔交易
                        history = user_data['transaction_history'][-5:]
                        for trade in reversed(history):  # 最新的在前
                            action = trade.get('type', trade.get('action', ''))
                            symbol = trade.get('symbol', '')
                            quantity = trade.get('quantity', 0)
                            price = trade.get('price', 0.0)
                            timestamp = trade.get('time', trade.get('timestamp', ''))
                            
                            # 格式化时间
                            if timestamp:
                                try:
                                    from datetime import datetime
                                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                    time_str = dt.strftime("%m-%d %H:%M")
                                except:
                                    time_str = timestamp[:10]
                            else:
                                time_str = "未知"
                            
                            # 操作图标
                            if action.upper() in ['BUY', 'BOUGHT']:
                                icon = "📈"
                                color_indicator = "+"
                            elif action.upper() in ['SELL', 'SOLD']:
                                icon = "📉" 
                                color_indicator = "-"
                            elif action.upper() in ['SHORT', 'SHORT_SELL']:
                                icon = "🔻"
                                color_indicator = "↓"
                            elif action.upper() in ['COVER', 'COVER_SHORT']:
                                icon = "🔺"
                                color_indicator = "↑"
                            else:
                                icon = "💼"
                                color_indicator = ""
                            
                            recent_trades += f"\n {icon} {symbol} {quantity} @${price:.2f} {time_str}"
                    
                    if not recent_trades:
                        recent_trades = "\n 暂无交易记录"
                    
                    holdings_text = f"{holdings_count-commodity_holdings} stocks"
                    if commodity_holdings > 0:
                        holdings_text += f" + {commodity_holdings} commodities"
                    
                    return f"""═══ ACCOUNT STATUS ════
 💰 Balance: J${self.app.cash:,.2f}     
 📊 Total:   J${total_value:,.2f}     
 🏢 Holdings: {holdings_text}  
 📈 P&L:     J${total_value-100000:+,.2f}    
═══ RECENT TRADES ═════{recent_trades}
═══════════════════════"""
                    
        except Exception as e:
            print(f"Portfolio summary error: {e}")
            
        return """═══ ACCOUNT STATUS ════
 Loading portfolio...   
═══════════════════════"""

    def execute_command(self, command):
        """⚡ 执行命令"""
        if hasattr(self.app, 'command_processor') and self.app.command_processor is not None:
            self.app.command_processor.process_command(command)
        else:
            # Handle the case where command_processor is not yet initialized
            self.print_to_output("❌ 系统尚未完全初始化，请先登录", '#FF0000')
    
    def handle_command_input(self, event):
        """🎯 处理命令输入"""
        command = self.get_command_input().strip()
        if command:
            # 添加到历史记录
            if not self.command_history or self.command_history[-1] != command:
                self.command_history.append(command)
                # 限制历史记录数量
                if len(self.command_history) > 100:
                    self.command_history.pop(0)
            
            # 重置历史索引
            self.history_index = -1
            
            # 清空输入框
            self.clear_command_input()
            
            # 执行命令
            self.execute_command(command)
        
        return "break"  # 防止默认处理
    
    def history_up(self, event):
        """⬆️ 上翻命令历史"""
        if self.command_history:
            if self.history_index == -1:
                self.history_index = len(self.command_history) - 1
            elif self.history_index > 0:
                self.history_index -= 1
            
            if 0 <= self.history_index < len(self.command_history):
                self.command_entry.delete(0, tk.END)
                self.command_entry.insert(0, self.command_history[self.history_index])
        
        return "break"
    
    def history_down(self, event):
        """⬇️ 下翻命令历史"""
        if self.command_history and self.history_index != -1:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.command_entry.delete(0, tk.END)
                self.command_entry.insert(0, self.command_history[self.history_index])
            else:
                self.history_index = -1
                self.command_entry.delete(0, tk.END)
        
        return "break"

    # 为了兼容现有代码，提供一些方法
    def print_to_output(self, text, color='#00FF41', end='\n'):
        """📤 输出文本到终端"""
        if hasattr(self, 'output_text'):
            self.output_text.config(state=tk.NORMAL)
            
            # 根据颜色类型设置标签
            tag_name = f"color_{color.replace('#', '')}"
            self.output_text.tag_configure(tag_name, foreground=color)
            
            self.output_text.insert(tk.END, text + end, tag_name)
            self.output_text.see(tk.END)
            self.output_text.config(state=tk.DISABLED)

    def clear_screen(self):
        """🧹 清屏"""
        if hasattr(self, 'output_text'):
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.config(state=tk.DISABLED)

    def get_command_input(self):
        """📥 获取命令输入"""
        if hasattr(self, 'command_entry'):
            return self.command_entry.get()
        return ""

    def clear_command_input(self):
        """🧹 清空命令输入"""
        if hasattr(self, 'command_entry'):
            self.command_entry.delete(0, tk.END)

    def update_title(self):
        """🏷️ 更新标题"""
        # 专业终端的标题在工具栏中，这里可以留空或更新状态
        pass

    def display_market_event(self, event):
        """📢 显示市场事件"""
        if hasattr(self, 'events_text'):
            self.events_text.config(state=tk.NORMAL)
            timestamp = datetime.now().strftime("%H:%M:%S")
            event_text = f"[{timestamp}] {event.get('title', 'Market Event')}\n"
            self.events_text.insert(tk.END, event_text)
            self.events_text.see(tk.END)
            self.events_text.config(state=tk.DISABLED) 