"""
📈 高级图表分析工具
包含独立GUI窗口的专业级股票图表分析应用
"""

import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np
import random
from datetime import datetime, timedelta
from apps.base_app import BaseApp
import platform

# 配置matplotlib中文字体
try:
    if platform.system() == 'Windows':
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
    elif platform.system() == 'Darwin':  # macOS
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'STHeiti', 'SimHei']
    else:  # Linux
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Micro Hei', 'SimHei', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
except:
    # 如果字体配置失败，使用默认字体
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']


class AdvancedChartApp(BaseApp):
    """高级图表分析应用"""
    
    def __init__(self):
        super().__init__(
            "advanced_chart",
            "📈 高级图表分析",
            "专业级股票图表分析工具，支持K线图、技术指标、多窗口对比等功能。",
            20000,
            "分析工具"
        )
        self.chart_window = None
        
    def run(self, main_app, symbol=None, chart_type="candlestick"):
        """运行高级图表应用"""
        self.usage_count += 1
        self.main_app = main_app
        
        if not symbol:
            return self._show_chart_menu()
        
        symbol = symbol.upper()
        
        if symbol not in main_app.market_data.stocks:
            return f"❌ 股票代码 '{symbol}' 不存在"
        
        # 启动图表窗口
        self._launch_chart_window(symbol, chart_type)
        return f"✅ 已启动 {symbol} 的高级图表分析窗口"
    
    def _show_chart_menu(self):
        """显示图表应用菜单"""
        return f"""
📈 高级图表分析工具

🎯 功能特色:
  • 📊 专业K线图表
  • 📈 多种技术指标 (MA, MACD, RSI, BOLL)
  • 📉 实时价格更新
  • 🔄 多股票对比分析
  • 📱 独立GUI窗口
  • 🎨 可自定义图表样式

💰 当前余额: ${self.main_app.cash:,.2f}

📊 图表类型:
  • candlestick - K线图 (默认)
  • line - 线型图
  • volume - 成交量图
  • indicators - 技术指标图

🎮 使用方法:
  appmarket.app advanced_chart <股票代码> [图表类型]

📖 示例:
  appmarket.app advanced_chart AAPL              # 苹果公司K线图
  appmarket.app advanced_chart TSLA candlestick  # 特斯拉K线图
  appmarket.app advanced_chart MSFT line         # 微软线型图
  appmarket.app advanced_chart GOOGL indicators  # 谷歌技术指标图

💡 提示:
  • 图表窗口支持缩放、平移等交互操作
  • 可同时打开多个股票的图表窗口
  • 点击图表上的数据点查看详细信息
  • 支持导出图表为图片文件

🔧 快捷键 (在图表窗口中):
  • F5 - 刷新数据
  • Ctrl+S - 保存图表
  • Ctrl+C - 复制图表
  • ESC - 关闭窗口
"""
    
    def _launch_chart_window(self, symbol, chart_type):
        """启动图表窗口"""
        try:
            # 创建新的图表窗口
            window = ChartWindow(self.main_app, symbol, chart_type, self)
            window.show()
        except Exception as e:
            return f"❌ 启动图表窗口失败: {str(e)}"


class ChartWindow:
    """图表显示窗口"""
    
    def __init__(self, main_app, symbol, chart_type, chart_app):
        self.main_app = main_app
        self.symbol = symbol
        self.chart_type = chart_type
        self.chart_app = chart_app
        self.root = None
        self.fig = None
        self.canvas = None
        self.update_job = None
        
    def show(self):
        """显示图表窗口"""
        # 创建新窗口
        self.root = tk.Toplevel()
        self.root.title(f"📈 高级图表分析 - {self.symbol}")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1e1e1e')
        
        # 创建主框架
        self._create_main_frame()
        
        # 创建工具栏
        self._create_toolbar()
        
        # 创建图表区域
        self._create_chart_area()
        
        # 创建状态栏
        self._create_status_bar()
        
        # 绑定快捷键
        self._bind_shortcuts()
        
        # 初始化图表
        self._update_chart()
        
        # 启动自动更新
        self._start_auto_update()
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_main_frame(self):
        """创建主框架"""
        # 主容器
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧控制面板
        self.control_frame = ttk.LabelFrame(self.main_frame, text="控制面板", padding=10)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # 右侧图表区域
        self.chart_frame = ttk.Frame(self.main_frame)
        self.chart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def _create_toolbar(self):
        """创建工具栏"""
        toolbar_frame = ttk.Frame(self.control_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 股票选择
        ttk.Label(toolbar_frame, text="股票代码:").pack(anchor=tk.W)
        self.symbol_var = tk.StringVar(value=self.symbol)
        symbol_combo = ttk.Combobox(toolbar_frame, textvariable=self.symbol_var, width=15)
        symbol_combo['values'] = list(self.main_app.market_data.stocks.keys())
        symbol_combo.pack(fill=tk.X, pady=(2, 10))
        symbol_combo.bind('<<ComboboxSelected>>', self._on_symbol_change)
        
        # 图表类型选择
        ttk.Label(toolbar_frame, text="图表类型:").pack(anchor=tk.W)
        self.chart_type_var = tk.StringVar(value=self.chart_type)
        chart_type_combo = ttk.Combobox(toolbar_frame, textvariable=self.chart_type_var, width=15)
        chart_type_combo['values'] = ['candlestick', 'line', 'volume', 'indicators']
        chart_type_combo.pack(fill=tk.X, pady=(2, 10))
        chart_type_combo.bind('<<ComboboxSelected>>', self._on_chart_type_change)
        
        # 时间范围选择
        ttk.Label(toolbar_frame, text="时间范围:").pack(anchor=tk.W)
        self.timeframe_var = tk.StringVar(value="1M")
        timeframe_combo = ttk.Combobox(toolbar_frame, textvariable=self.timeframe_var, width=15)
        timeframe_combo['values'] = ['1D', '5D', '1M', '3M', '6M', '1Y']
        timeframe_combo.pack(fill=tk.X, pady=(2, 10))
        timeframe_combo.bind('<<ComboboxSelected>>', self._on_timeframe_change)
        
        # 技术指标选择
        ttk.Label(toolbar_frame, text="技术指标:").pack(anchor=tk.W)
        
        self.ma_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(toolbar_frame, text="移动平均线(MA)", variable=self.ma_var, 
                       command=self._update_chart).pack(anchor=tk.W)
        
        self.bollinger_var = tk.BooleanVar()
        ttk.Checkbutton(toolbar_frame, text="布林带(BOLL)", variable=self.bollinger_var,
                       command=self._update_chart).pack(anchor=tk.W)
        
        self.volume_var = tk.BooleanVar()
        ttk.Checkbutton(toolbar_frame, text="成交量", variable=self.volume_var,
                       command=self._update_chart).pack(anchor=tk.W)
        
        # 操作按钮
        button_frame = ttk.Frame(toolbar_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="🔄 刷新", command=self._update_chart).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="💾 保存图表", command=self._save_chart).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="📈 技术分析", command=self._show_technical_analysis).pack(fill=tk.X, pady=2)
        
        # 股票信息显示
        info_frame = ttk.LabelFrame(self.control_frame, text="股票信息", padding=10)
        info_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.info_text = tk.Text(info_frame, height=8, width=25, font=('Consolas', 9))
        info_scrollbar = ttk.Scrollbar(info_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=info_scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        info_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self._update_stock_info()
    
    def _create_chart_area(self):
        """创建图表区域"""
        # 创建matplotlib图形
        self.fig = Figure(figsize=(12, 8), dpi=100, facecolor='#2e2e2e')
        self.fig.patch.set_facecolor('#2e2e2e')
        
        # 创建画布
        self.canvas = FigureCanvasTkAgg(self.fig, self.chart_frame)
        self.canvas.draw()
        
        # 创建工具栏
        toolbar_frame = ttk.Frame(self.chart_frame)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        
        toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        toolbar.update()
        
        # 放置画布
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def _create_status_bar(self):
        """创建状态栏"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(self.status_frame, text=f"准备就绪 - {self.symbol}")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.time_label = ttk.Label(self.status_frame, text="")
        self.time_label.pack(side=tk.RIGHT, padx=5)
        
        self._update_time()
    
    def _bind_shortcuts(self):
        """绑定快捷键"""
        self.root.bind('<F5>', lambda e: self._update_chart())
        self.root.bind('<Control-s>', lambda e: self._save_chart())
        self.root.bind('<Escape>', lambda e: self._on_closing())
        
        # 鼠标事件
        self.canvas.mpl_connect('button_press_event', self._on_mouse_click)
    
    def _update_chart(self):
        """更新图表"""
        try:
            self.fig.clear()
            
            # 获取股票数据
            stock_data = self._get_stock_data()
            
            if self.chart_type_var.get() == 'candlestick':
                self._draw_candlestick_chart(stock_data)
            elif self.chart_type_var.get() == 'line':
                self._draw_line_chart(stock_data)
            elif self.chart_type_var.get() == 'volume':
                self._draw_volume_chart(stock_data)
            elif self.chart_type_var.get() == 'indicators':
                self._draw_indicators_chart(stock_data)
            
            self.canvas.draw()
            self._update_status(f"Chart updated - {self.symbol_var.get()}")
            
        except Exception as e:
            self._update_status(f"Chart update failed: {str(e)}")
    
    def _get_stock_data(self):
        """获取股票数据"""
        symbol = self.symbol_var.get()
        if symbol not in self.main_app.market_data.stocks:
            return None
        
        stock = self.main_app.market_data.stocks[symbol]
        
        # 生成历史数据
        timeframe = self.timeframe_var.get()
        days = {'1D': 1, '5D': 5, '1M': 30, '3M': 90, '6M': 180, '1Y': 365}[timeframe]
        
        current_price = stock['price']
        volatility = stock.get('volatility', 0.02)
        
        # 生成价格历史
        prices = []
        volumes = []
        dates = []
        
        base_price = current_price * 0.9  # 起始价格稍低
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            
            # 模拟价格变动
            change = random.gauss(0, volatility)
            base_price *= (1 + change)
            base_price = max(base_price, 1.0)  # 防止价格过低
            
            # 生成OHLC数据
            open_price = base_price
            high_price = open_price * (1 + abs(random.gauss(0, volatility/2)))
            low_price = open_price * (1 - abs(random.gauss(0, volatility/2)))
            close_price = open_price + random.gauss(0, volatility) * open_price
            close_price = max(min(close_price, high_price), low_price)
            
            # 最后一天使用实际价格
            if i == days - 1:
                close_price = current_price
                high_price = max(high_price, current_price)
                low_price = min(low_price, current_price)
            
            base_price = close_price
            
            prices.append({
                'date': date,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price
            })
            
            # 生成成交量
            volume = random.randint(1000000, 100000000)
            volumes.append(volume)
            dates.append(date)
        
        return {
            'symbol': symbol,
            'name': stock['name'],
            'prices': prices,
            'volumes': volumes,
            'dates': dates,
            'current_price': current_price,
            'change': stock.get('change', 0),
            'sector': stock.get('sector', 'Unknown')
        }
    
    def _draw_candlestick_chart(self, data):
        """绘制K线图"""
        if not data:
            return
        
        # 创建子图
        if self.volume_var.get():
            ax1 = self.fig.add_subplot(2, 1, 1)
            ax2 = self.fig.add_subplot(2, 1, 2)
        else:
            ax1 = self.fig.add_subplot(1, 1, 1)
            ax2 = None
        
        prices = data['prices']
        dates = [p['date'] for p in prices]
        opens = [p['open'] for p in prices]
        highs = [p['high'] for p in prices]
        lows = [p['low'] for p in prices]
        closes = [p['close'] for p in prices]
        
        # 绘制K线
        for i, (o, h, l, c) in enumerate(zip(opens, highs, lows, closes)):
            color = '#00ff00' if c >= o else '#ff0000'  # 绿涨红跌
            
            # 绘制影线
            ax1.plot([i, i], [l, h], color='#888888', linewidth=1)
            
            # 绘制实体
            height = abs(c - o)
            bottom = min(o, c)
            
            if c >= o:  # 阳线
                ax1.add_patch(plt.Rectangle((i-0.3, bottom), 0.6, height, 
                                          facecolor='none', edgecolor=color, linewidth=1))
            else:  # 阴线
                ax1.add_patch(plt.Rectangle((i-0.3, bottom), 0.6, height, 
                                          facecolor=color, edgecolor=color, linewidth=1))
        
        # 添加移动平均线
        if self.ma_var.get():
            ma5 = self._calculate_ma(closes, 5)
            ma20 = self._calculate_ma(closes, 20)
            
            ax1.plot(range(len(ma5)), ma5, color='#ffff00', linewidth=1, label='MA5', alpha=0.8)
            ax1.plot(range(len(ma20)), ma20, color='#ff00ff', linewidth=1, label='MA20', alpha=0.8)
            ax1.legend(loc='upper left')
        
        # 添加布林带
        if self.bollinger_var.get():
            upper, middle, lower = self._calculate_bollinger_bands(closes, 20)
            ax1.plot(range(len(upper)), upper, color='#00ffff', linewidth=1, alpha=0.6, label='BOLL Upper')
            ax1.plot(range(len(middle)), middle, color='#00ffff', linewidth=1, alpha=0.8, label='BOLL Middle')
            ax1.plot(range(len(lower)), lower, color='#00ffff', linewidth=1, alpha=0.6, label='BOLL Lower')
            ax1.fill_between(range(len(upper)), upper, lower, color='#00ffff', alpha=0.1)
        
        # 设置图表样式
        ax1.set_title(f"{data['symbol']} - {data['name']} Candlestick Chart", color='white', fontsize=14)
        ax1.set_facecolor('#1e1e1e')
        ax1.tick_params(colors='white')
        ax1.grid(True, alpha=0.3)
        
        # 设置X轴标签
        step = max(1, len(dates) // 10)
        ax1.set_xticks(range(0, len(dates), step))
        ax1.set_xticklabels([dates[i].strftime('%m-%d') for i in range(0, len(dates), step)], 
                           rotation=45, color='white')
        
        # 绘制成交量
        if self.volume_var.get() and ax2:
            volumes = data['volumes']
            colors = ['#00ff00' if closes[i] >= opens[i] else '#ff0000' for i in range(len(closes))]
            ax2.bar(range(len(volumes)), volumes, color=colors, alpha=0.7)
            ax2.set_title("Volume", color='white', fontsize=12)
            ax2.set_facecolor('#1e1e1e')
            ax2.tick_params(colors='white')
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
    
    def _draw_line_chart(self, data):
        """绘制线型图"""
        if not data:
            return
        
        ax = self.fig.add_subplot(1, 1, 1)
        
        prices = data['prices']
        closes = [p['close'] for p in prices]
        
        ax.plot(range(len(closes)), closes, color='#00aaff', linewidth=2, label=data['symbol'])
        
        # 添加技术指标
        if self.ma_var.get():
            ma5 = self._calculate_ma(closes, 5)
            ma20 = self._calculate_ma(closes, 20)
            ax.plot(range(len(ma5)), ma5, color='#ffff00', linewidth=1, label='MA5', alpha=0.8)
            ax.plot(range(len(ma20)), ma20, color='#ff00ff', linewidth=1, label='MA20', alpha=0.8)
        
        ax.set_title(f"{data['symbol']} - {data['name']} Price Trend", color='white', fontsize=14)
        ax.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left')
        
        plt.tight_layout()
    
    def _draw_volume_chart(self, data):
        """绘制成交量图"""
        if not data:
            return
        
        ax = self.fig.add_subplot(1, 1, 1)
        
        volumes = data['volumes']
        prices = data['prices']
        colors = ['#00ff00' if prices[i]['close'] >= prices[i]['open'] else '#ff0000' 
                 for i in range(len(prices))]
        
        bars = ax.bar(range(len(volumes)), volumes, color=colors, alpha=0.7)
        
        # 添加成交量移动平均线
        vol_ma = self._calculate_ma(volumes, 5)
        ax.plot(range(len(vol_ma)), vol_ma, color='#ffff00', linewidth=2, label='Vol MA5')
        
        ax.set_title(f"{data['symbol']} - Volume Analysis", color='white', fontsize=14)
        ax.set_facecolor('#1e1e1e')
        ax.tick_params(colors='white')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        
        plt.tight_layout()
    
    def _draw_indicators_chart(self, data):
        """绘制技术指标图"""
        if not data:
            return
        
        prices = data['prices']
        closes = [p['close'] for p in prices]
        
        # 创建4个子图
        ax1 = self.fig.add_subplot(4, 1, 1)  # 价格
        ax2 = self.fig.add_subplot(4, 1, 2)  # MACD
        ax3 = self.fig.add_subplot(4, 1, 3)  # RSI
        ax4 = self.fig.add_subplot(4, 1, 4)  # KDJ
        
        # 1. 价格图
        ax1.plot(range(len(closes)), closes, color='#00aaff', linewidth=1)
        ma5 = self._calculate_ma(closes, 5)
        ma20 = self._calculate_ma(closes, 20)
        ax1.plot(range(len(ma5)), ma5, color='#ffff00', linewidth=1, label='MA5')
        ax1.plot(range(len(ma20)), ma20, color='#ff00ff', linewidth=1, label='MA20')
        ax1.set_title(f"{data['symbol']} Technical Indicators", color='white', fontsize=12)
        ax1.legend(loc='upper left', fontsize=8)
        
        # 2. MACD
        macd_line, signal_line, histogram = self._calculate_macd(closes)
        ax2.plot(range(len(macd_line)), macd_line, color='#00ff00', linewidth=1, label='MACD')
        ax2.plot(range(len(signal_line)), signal_line, color='#ff0000', linewidth=1, label='Signal')
        ax2.bar(range(len(histogram)), histogram, color='#888888', alpha=0.6, label='Histogram')
        ax2.axhline(y=0, color='white', linewidth=0.5, alpha=0.5)
        ax2.set_title("MACD", color='white', fontsize=10)
        ax2.legend(loc='upper left', fontsize=8)
        
        # 3. RSI
        rsi = self._calculate_rsi(closes)
        ax3.plot(range(len(rsi)), rsi, color='#ffaa00', linewidth=1)
        ax3.axhline(y=70, color='#ff0000', linewidth=0.5, alpha=0.7, linestyle='--')
        ax3.axhline(y=30, color='#00ff00', linewidth=0.5, alpha=0.7, linestyle='--')
        ax3.axhline(y=50, color='white', linewidth=0.5, alpha=0.5)
        ax3.set_title("RSI", color='white', fontsize=10)
        ax3.set_ylim(0, 100)
        
        # 4. KDJ
        k, d, j = self._calculate_kdj(prices)
        ax4.plot(range(len(k)), k, color='#00ff00', linewidth=1, label='K')
        ax4.plot(range(len(d)), d, color='#ff0000', linewidth=1, label='D')
        ax4.plot(range(len(j)), j, color='#ffff00', linewidth=1, label='J')
        ax4.axhline(y=80, color='#ff0000', linewidth=0.5, alpha=0.7, linestyle='--')
        ax4.axhline(y=20, color='#00ff00', linewidth=0.5, alpha=0.7, linestyle='--')
        ax4.set_title("KDJ", color='white', fontsize=10)
        ax4.legend(loc='upper left', fontsize=8)
        ax4.set_ylim(0, 100)
        
        # 设置所有子图样式
        for ax in [ax1, ax2, ax3, ax4]:
            ax.set_facecolor('#1e1e1e')
            ax.tick_params(colors='white', labelsize=8)
            ax.grid(True, alpha=0.2)
        
        plt.tight_layout()
    
    def _calculate_ma(self, prices, period):
        """计算移动平均线"""
        ma = []
        for i in range(len(prices)):
            if i >= period - 1:
                ma.append(sum(prices[i-period+1:i+1]) / period)
            else:
                ma.append(prices[i])
        return ma
    
    def _calculate_bollinger_bands(self, prices, period, std_dev=2):
        """计算布林带"""
        ma = self._calculate_ma(prices, period)
        upper, lower = [], []
        
        for i in range(len(prices)):
            if i >= period - 1:
                data_slice = prices[i-period+1:i+1]
                std = np.std(data_slice)
                upper.append(ma[i] + std_dev * std)
                lower.append(ma[i] - std_dev * std)
            else:
                upper.append(prices[i])
                lower.append(prices[i])
        
        return upper, ma, lower
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """计算MACD"""
        def ema(data, period):
            result = []
            multiplier = 2 / (period + 1)
            result.append(data[0])
            
            for i in range(1, len(data)):
                result.append((data[i] * multiplier) + (result[i-1] * (1 - multiplier)))
            return result
        
        ema12 = ema(prices, fast)
        ema26 = ema(prices, slow)
        
        macd_line = [ema12[i] - ema26[i] for i in range(len(prices))]
        signal_line = ema(macd_line, signal)
        histogram = [macd_line[i] - signal_line[i] for i in range(len(macd_line))]
        
        return macd_line, signal_line, histogram
    
    def _calculate_rsi(self, prices, period=14):
        """计算RSI"""
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            gains.append(max(change, 0))
            losses.append(max(-change, 0))
        
        rsi = []
        for i in range(len(gains)):
            if i >= period - 1:
                avg_gain = sum(gains[i-period+1:i+1]) / period
                avg_loss = sum(losses[i-period+1:i+1]) / period
                
                if avg_loss == 0:
                    rsi.append(100)
                else:
                    rs = avg_gain / avg_loss
                    rsi.append(100 - (100 / (1 + rs)))
            else:
                rsi.append(50)
        
        return [50] + rsi  # 添加第一个点
    
    def _calculate_kdj(self, prices, period=9):
        """计算KDJ指标"""
        highs = [p['high'] for p in prices]
        lows = [p['low'] for p in prices]
        closes = [p['close'] for p in prices]
        
        k_values = []
        d_values = []
        j_values = []
        
        for i in range(len(prices)):
            if i >= period - 1:
                period_high = max(highs[i-period+1:i+1])
                period_low = min(lows[i-period+1:i+1])
                
                if period_high == period_low:
                    rsv = 50
                else:
                    rsv = (closes[i] - period_low) / (period_high - period_low) * 100
            else:
                rsv = 50
            
            if i == 0:
                k = 50
                d = 50
            else:
                k = (k_values[-1] * 2 + rsv) / 3
                d = (d_values[-1] * 2 + k) / 3
            
            j = 3 * k - 2 * d
            
            k_values.append(k)
            d_values.append(d)
            j_values.append(j)
        
        return k_values, d_values, j_values
    
    def _update_stock_info(self):
        """更新股票信息显示"""
        symbol = self.symbol_var.get()
        if symbol in self.main_app.market_data.stocks:
            stock = self.main_app.market_data.stocks[symbol]
            
            info_text = f"""股票代码: {symbol}
公司名称: {stock['name']}
当前价格: ${stock['price']:.2f}
涨跌幅: ${stock.get('change', 0):+.2f}
涨跌比: {stock.get('change', 0)/stock['price']*100:+.2f}%
所属行业: {stock.get('sector', 'N/A')}
市值: ${stock.get('market_cap', 0):,.0f}
市盈率: {stock.get('pe_ratio', 'N/A')}
成交量: {stock.get('volume', 0):,}
Beta值: {stock.get('beta', 'N/A')}
股息率: {stock.get('dividend_yield', 0)*100:.2f}%

📈 最近更新:
{stock.get('last_updated', 'N/A')[:19]}
"""
            
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info_text)
    
    def _update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
    
    def _update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self._update_time)
    
    def _start_auto_update(self):
        """启动自动更新"""
        self._auto_update()
    
    def _auto_update(self):
        """自动更新图表"""
        if self.root and self.root.winfo_exists():
            self._update_chart()
            self._update_stock_info()
            # 每30秒更新一次
            self.update_job = self.root.after(30000, self._auto_update)
    
    def _on_symbol_change(self, event=None):
        """股票代码改变事件"""
        self.symbol = self.symbol_var.get()
        self._update_chart()
        self._update_stock_info()
    
    def _on_chart_type_change(self, event=None):
        """图表类型改变事件"""
        self.chart_type = self.chart_type_var.get()
        self._update_chart()
    
    def _on_timeframe_change(self, event=None):
        """时间范围改变事件"""
        self._update_chart()
    
    def _on_mouse_click(self, event):
        """鼠标点击事件"""
        if event.inaxes and event.xdata is not None:
            # 显示数据点信息
            x_index = int(round(event.xdata))
            data = self._get_stock_data()
            if data and 0 <= x_index < len(data['prices']):
                price_info = data['prices'][x_index]
                self._update_status(f"数据点信息: {price_info['date'].strftime('%Y-%m-%d')} 收盘 ${price_info['close']:.2f}")
    
    def _save_chart(self):
        """保存图表"""
        try:
            filename = f"chart_{self.symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            self.fig.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#2e2e2e')
            messagebox.showinfo("保存成功", f"图表已保存为: {filename}")
        except Exception as e:
            messagebox.showerror("保存失败", f"保存图表时出错: {str(e)}")
    
    def _show_technical_analysis(self):
        """显示技术分析"""
        data = self._get_stock_data()
        if not data:
            return
        
        prices = [p['close'] for p in data['prices']]
        current_price = prices[-1]
        
        # 简单的技术分析
        ma5 = self._calculate_ma(prices, 5)[-1]
        ma20 = self._calculate_ma(prices, 20)[-1]
        rsi = self._calculate_rsi(prices)[-1]
        
        analysis = f"""📈 {data['symbol']} 技术分析报告
        
当前价格: ${current_price:.2f}
MA5: ${ma5:.2f} {'↗️' if current_price > ma5 else '↘️'}
MA20: ${ma20:.2f} {'↗️' if current_price > ma20 else '↘️'}
RSI: {rsi:.1f} {'超买' if rsi > 70 else '超卖' if rsi < 30 else '正常'}

趋势判断:
{'看涨' if current_price > ma5 > ma20 else '看跌' if current_price < ma5 < ma20 else '震荡'}

建议:
{'建议买入' if rsi < 30 and current_price > ma5 else '建议卖出' if rsi > 70 and current_price < ma5 else '持有观望'}
"""
        
        messagebox.showinfo("技术分析", analysis)
    
    def _on_closing(self):
        """窗口关闭事件"""
        if self.update_job:
            self.root.after_cancel(self.update_job)
        self.root.destroy() 