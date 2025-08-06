import json
import os
import random
import time
import threading
from datetime import datetime
import pytz


class MarketDataManager:
    def __init__(self):
        self.stocks = {}
        self.market_events = []
        self.achievement_definitions = {}
        self.index_manager = None
        self.ensure_data_directory()
        self.load_all_data()
        self.init_index_manager()

    def ensure_data_directory(self):
        """Ensure the data directory exists."""
        if not os.path.exists('data'):
            os.makedirs('data')

    def load_all_data(self):
        """Load all market data from JSON files."""
        self.stocks = self.load_stocks()
        self.market_events = self.load_market_events()
        self.achievement_definitions = self.load_achievements()

    def load_stocks(self):
        """Load stock data from all_stocks.json."""
        stocks = {}
        
        # 优先加载合并后的股票文件
        all_stocks_file = 'data/all_stocks.json'
        if os.path.exists(all_stocks_file):
            try:
                with open(all_stocks_file, 'r', encoding='utf-8') as f:
                    stocks = json.load(f)
                    # Ensure last_updated is in ISO format
                    for symbol, data in stocks.items():
                        data['last_updated'] = data.get('last_updated', datetime.now().isoformat())
                    print(f"[DEBUG] 从 all_stocks.json 加载了 {len(stocks)} 只股票")
                    return stocks
            except Exception as e:
                print(f"加载all_stocks.json时出错: {str(e)}")
        
        # 如果all_stocks.json不存在，尝试加载原来的文件
        print("all_stocks.json不存在，尝试加载原始股票文件...")
        
        # 加载主要股票数据
        try:
            with open('data/stocks.json', 'r', encoding='utf-8') as f:
                main_stocks = json.load(f)
                # Ensure last_updated is in ISO format
                for symbol, data in main_stocks.items():
                    data['last_updated'] = data.get('last_updated', datetime.now().isoformat())
                stocks.update(main_stocks)
                print(f"[DEBUG] 从 stocks.json 加载了 {len(main_stocks)} 只股票")
        except FileNotFoundError:
            print("错误: 未找到 stocks.json 文件")
        except json.JSONDecodeError:
            print("错误: stocks.json 格式错误")
        except Exception as e:
            print(f"加载主要股票数据时出错: {str(e)}")
        
        # 如果没有加载到任何股票，创建一些默认股票
        if not stocks:
            print("创建默认股票数据")
            stocks = self.create_default_stocks()
        
        print(f"[DEBUG] 总共加载了 {len(stocks)} 只股票")
        return stocks

    def load_market_events(self):
        """Load market events from market_events.json."""
        default_events = [
            {
                "id": "default_001",
                "title": "市场平稳，无重大事件",
                "description": "当前市场无重大新闻，价格波动正常。",
                "impact": {
                    "sectors": ["All"],
                    "effect": "neutral",
                    "magnitude": 0.0,
                    "duration": "short_term"
                },
                "related_stocks": [],
                "timestamp": datetime.now().isoformat()
            }
        ]
        try:
            with open('data/market_events.json', 'r', encoding='utf-8') as f:
                events = json.load(f)
                # Validate event structure
                for event in events:
                    event['timestamp'] = event.get('timestamp', datetime.now().isoformat())
                    event['impact'] = event.get('impact', {"sectors": ["All"], "effect": "neutral", "magnitude": 0.0,
                                                           "duration": "short_term"})
                    event['related_stocks'] = event.get('related_stocks', [])
                return events
        except FileNotFoundError:
            print("错误: 未找到 market_events.json 文件，使用默认市场事件")
            return default_events
        except json.JSONDecodeError:
            print("错误: market_events.json 格式错误，使用默认市场事件")
            return default_events
        except Exception as e:
            print(f"加载市场事件时出错: {str(e)}")
            return default_events

    def load_achievements(self):
        """Load achievement definitions from achievements.json."""
        try:
            with open('data/achievements.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("错误: 未找到 achievements.json 文件，使用默认成就数据")
            return {}
        except json.JSONDecodeError:
            print("错误: achievements.json 格式错误，使用默认成就数据")
            return {}
        except Exception as e:
            print(f"加载成就数据领奖时出错: {str(e)}")
            return {}

    def save_stocks(self):
        """Save stock data back to all_stocks.json."""
        try:
            with open('data/all_stocks.json', 'w', encoding='utf-8') as f:
                json.dump(self.stocks, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存股票数据时出错: {str(e)}")

    def save_market_events(self):
        """Save market events back to market_events.json."""
        try:
            with open('data/market_events.json', 'w', encoding='utf-8') as f:
                json.dump(self.market_events, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存市场事件时出错: {str(e)}")

    def update_stock_prices(self, print_callback=None):
        """Update stock prices with influence from market events."""
        while True:
            try:
                # Calculate market sentiment from recent events
                utc_now = datetime.now(pytz.UTC)  # Make datetime.now() UTC-aware
                recent_events = []
                
                # 安全地处理事件时间戳
                for event in self.market_events:
                    try:
                        timestamp_str = event.get('timestamp', '')
                        if timestamp_str:
                            # 处理各种时间戳格式
                            if timestamp_str.endswith('Z'):
                                timestamp_str = timestamp_str.replace('Z', '+00:00')
                            elif '+' not in timestamp_str and 'T' in timestamp_str:
                                timestamp_str += '+00:00'
                            
                            event_time = datetime.fromisoformat(timestamp_str)
                            if event_time.tzinfo is None:
                                event_time = pytz.UTC.localize(event_time)
                            
                            # 检查事件是否在最近一小时内
                            time_diff = (utc_now - event_time).total_seconds()
                            if time_diff < 3600:  # 1小时内
                                recent_events.append(event)
                    except (ValueError, TypeError) as e:
                        # 跳过无效的时间戳
                        print(f"警告: 无效的事件时间戳 {event.get('id', 'unknown')}: {e}")
                        continue
                
                sentiment_score = sum(1 for e in recent_events if e['impact']['effect'] == 'positive') - \
                                  sum(1 for e in recent_events if e['impact']['effect'] == 'negative')
                sentiment_factor = 1.0 + (sentiment_score * 0.005)

                # Map events to sectors and stocks
                event_impacts = {}
                for event in recent_events:
                    try:
                        for sector in event['impact']['sectors']:
                            if sector not in event_impacts:
                                event_impacts[sector] = []
                            event_impacts[sector].append(event['impact'])
                        for stock in event['related_stocks']:
                            if stock not in event_impacts:
                                event_impacts[stock] = []
                            event_impacts[stock].append(event['impact'])
                    except KeyError as e:
                        print(f"警告: 事件结构不完整 {event.get('id', 'unknown')}: 缺少 {e}")
                        continue

                # 安全地更新股票价格
                for symbol in list(self.stocks.keys()):  # 使用list()避免字典在迭代时被修改
                    try:
                        stock = self.stocks[symbol]
                        old_price = stock.get('price', 100.0)
                        volatility = stock.get('volatility', 0.02)
                        volume = stock.get('volume', 1000000)
                        beta = stock.get('beta', 1.0)

                        # Base price change
                        random_change = random.uniform(-volatility, volatility)
                        volume_factor = 1.0 - (min(volume, 100000000) / 100000000) * 0.1

                        # Apply event-based impact
                        event_factor = 1.0
                        sector = stock.get('sector', 'Other')
                        
                        if sector in event_impacts:
                            impacts = event_impacts[sector]
                            for impact in impacts:
                                magnitude = impact.get('magnitude', 0.01)
                                if impact.get('effect') == 'negative':
                                    magnitude = -magnitude
                                event_factor *= (1 + magnitude)
                                
                        if symbol in event_impacts:
                            impacts = event_impacts[symbol]
                            for impact in impacts:
                                magnitude = impact.get('magnitude', 0.01)
                                if impact.get('effect') == 'negative':
                                    magnitude = -magnitude
                                event_factor *= (1 + magnitude)

                        # Combine factors with safety limits
                        total_change = random_change * volume_factor * sentiment_factor * event_factor * beta
                        # 限制单次变化幅度
                        total_change = max(-0.1, min(0.1, total_change))  # 最大10%变化
                        
                        new_price = old_price * (1 + total_change)
                        if new_price < 1:
                            new_price = max(1, old_price * 0.99)

                        # Update stock data with safety checks
                        stock['price'] = round(new_price, 2)
                        stock['change'] = round(new_price - old_price, 2)
                        stock['volume'] = int(volume * random.uniform(0.8, 1.2))
                        
                        # 安全地更新价格历史
                        if 'price_history' not in stock:
                            stock['price_history'] = [old_price] * 20
                        stock['price_history'].append(stock['price'])
                        if len(stock['price_history']) > 20:
                            stock['price_history'].pop(0)
                            
                        stock['last_updated'] = datetime.now(pytz.UTC).isoformat()
                        
                        # 安全地计算PE比率
                        eps = stock.get('eps', 0)
                        if eps and eps > 0:
                            stock['pe_ratio'] = round(stock['price'] / eps, 2)
                        else:
                            stock['pe_ratio'] = None
                            
                    except Exception as e:
                        print(f"更新股票 {symbol} 价格时出错: {e}")
                        continue

                # 安全地保存数据
                try:
                    self.save_stocks()
                except Exception as e:
                    print(f"保存股票数据时出错: {e}")
                
                # 更新指数
                try:
                    self.update_indices()
                except Exception as e:
                    print(f"更新指数时出错: {e}")
                
            except Exception as e:
                print(f"价格更新循环出错: {e}")
                # 出错时等待更长时间再继续
                time.sleep(10)
                continue
            
            # 正常情况下的等待时间
            time.sleep(random.uniform(1, 3))

    def generate_market_event(self):
        """Generate a new market event based on templates loaded from event_template.json."""
        # Load event templates from file
        template_file = os.path.join("data", "event_template.json")
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                event_templates = json.load(f)
        except FileNotFoundError:
            print(f"错误: 未找到 {template_file}")
            event_templates = [
                {
                    "title": "默认事件: {sector}板块波动",
                    "description": "由于未知原因，{sector}行业出现市场波动。",
                    "impact": {"sectors": ["All"], "effect": "neutral", "magnitude": 0.01, "duration": "short_term"},
                    "related_stocks": []
                }
            ]
        except json.JSONDecodeError:
            print(f"错误: {template_file} 格式无效")
            event_templates = [
                {
                    "title": "默认事件: {sector}板块波动",
                    "description": "由于未知原因，{sector}行业出现市场波动。",
                    "impact": {"sectors": ["All"], "effect": "neutral", "magnitude": 0.01, "duration": "short_term"},
                    "related_stocks": []
                }
            ]

        # Get available sectors from stocks
        sectors = list(set(stock['sector'] for stock in self.stocks.values()))
        template = random.choice(event_templates)
        sector = random.choice(sectors)

        # Create event
        event = {
            "id": f"event_{len(self.market_events) + 1:03d}",
            "title": template["title"].format(sector=sector),
            "description": template["description"].format(sector=sector),
            "impact": template["impact"].copy(),
            "related_stocks": template["related_stocks"].copy(),
            "timestamp": datetime.now(pytz.UTC).isoformat()
        }

        # Replace "All" with the randomly selected sector, or keep specific sectors
        event["impact"]["sectors"] = [sector] if event["impact"]["sectors"] == ["All"] else event["impact"]["sectors"]

        # Filter related stocks to ensure they exist in self.stocks
        event["related_stocks"] = [stock for stock in event["related_stocks"] if stock in self.stocks]

        return event

    def start_price_update_thread(self, print_callback=None):
        """启动价格更新线程"""
        price_thread = threading.Thread(target=lambda: self.update_stock_prices(print_callback), daemon=True)
        price_thread.start()

    def start_market_events_thread(self, events_callback=None):
        """Start market events thread to display and generate events."""

        def market_events_loop():
            while True:
                # Display a recent event
                if self.market_events and events_callback:
                    event = random.choice(self.market_events)
                    events_callback(event)

                # Occasionally generate a new event
                if random.random() < 0.1:  # 10% chance per cycle
                    new_event = self.generate_market_event()
                    self.market_events.append(new_event)
                    self.save_market_events()

                time.sleep(random.uniform(10, 60))

        events_thread = threading.Thread(target=market_events_loop, daemon=True)
        events_thread.start()
    
    def init_index_manager(self):
        """初始化指数管理器"""
        try:
            from core.index_manager import IndexManager
            self.index_manager = IndexManager(self)
            print(f"[DEBUG] 指数管理器初始化完成")
        except Exception as e:
            print(f"[DEBUG] 指数管理器初始化失败: {e}")
    
    def create_default_stocks(self):
        """创建默认股票数据"""
        default_stocks = {
            "AAPL": {
                "name": "Apple Inc.",
                "price": 175.50,
                "change": 0.0,
                "sector": "Technology",
                "volatility": 0.02,
                "market_cap": 2700000000000,
                "pe_ratio": 28.5,
                "volume": 50000000,
                "beta": 1.2,
                "dividend_yield": 0.005,
                "price_history": [175.50],
                "eps": 6.15,
                "last_updated": datetime.now().isoformat()
            },
            "MSFT": {
                "name": "Microsoft Corporation",
                "price": 350.25,
                "change": 0.0,
                "sector": "Technology",
                "volatility": 0.018,
                "market_cap": 2600000000000,
                "pe_ratio": 32.8,
                "volume": 35000000,
                "beta": 0.9,
                "dividend_yield": 0.007,
                "price_history": [350.25],
                "eps": 10.68,
                "last_updated": datetime.now().isoformat()
            }
        }
        return default_stocks
    
    def update_indices(self):
        """更新所有指数"""
        if self.index_manager:
            self.index_manager.update_all_indices() 