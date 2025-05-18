import random
import json
import os


class NewsGenerator:
    # 在NewsGenerator类的__init__方法中添加news_file参数
    def __init__(self, news_file=None):
        # 初始化新闻源
        self.news_file = news_file
        
        # 如果提供了新闻文件并且它存在，从文件加载新闻
        if news_file and os.path.exists(news_file):
            self.load_news_from_json()
        else:
            # 使用默认新闻
            self.news_events = [
                {"headline": "Economic Boom: Markets Rally", "impact": {"sector": "all", "change": 3.0}},
                {"headline": "Market Crash: Investors Panic", "impact": {"sector": "all", "change": -4.0}},
                {"headline": "Tech Innovation Breakthrough", "impact": {"sector": "Technology", "change": 5.0}},
                {"headline": "Healthcare Reform Announced", "impact": {"sector": "Healthcare", "change": 4.0}},
                {"headline": "Banking Scandal Erupts", "impact": {"sector": "Finance", "change": -5.0}},
                {"headline": "Oil Price Surge", "impact": {"sector": "Energy", "change": 6.0}},
                {"headline": "Consumer Spending Drops", "impact": {"sector": "Consumer", "change": -3.0}},
                {"headline": "New Tech Regulations", "impact": {"sector": "Technology", "change": -4.0}},
                {"headline": "Medical Breakthrough", "impact": {"sector": "Healthcare", "change": 7.0}},
                {"headline": "Interest Rates Cut", "impact": {"sector": "Finance", "change": 4.0}},
                {"headline": "Renewable Energy Push", "impact": {"sector": "Energy", "change": -3.0}},
                {"headline": "Retail Sales Boom", "impact": {"sector": "Consumer", "change": 5.0}}
            ]

            # Stock-specific news events
            self.stock_news_events = [
                {"headline": "TechGiant Launches New Product", "impact": {"stock": "TGT", "change": 8.0}},
                {"headline": "MediHealth Recalls Drug", "impact": {"stock": "MHC", "change": -7.0}},
                {"headline": "BankCorp Announces Expansion", "impact": {"stock": "BNK", "change": 6.0}},
                {"headline": "Oil Spill at EnergyOne Facility", "impact": {"stock": "ENO", "change": -9.0}},
                {"headline": "RetailShop Beats Earnings Estimates", "impact": {"stock": "RSP", "change": 7.0}},
            ]
            
            # Save default news to JSON
            self.save_news_to_json()

        self.news_feed = ["Welcome to Stock Market Simulator! You have $10,000 to invest."]

    def load_news_from_json(self):
        """Load news events from JSON file"""
        try:
            with open(self.news_file, 'r') as file:
                news_data = json.load(file)
                self.news_events = news_data.get('market_news', [])
                self.stock_news_events = news_data.get('stock_news', [])
                print(f"Loaded news events from {self.news_file}")
        except Exception as e:
            print(f"Error loading news from {self.news_file}: {e}")
            # Fall back to defaults if loading fails
            self.news_events = []
            self.stock_news_events = []

    def save_news_to_json(self):
        """Save current news events to JSON file"""
        try:
            news_data = {
                'market_news': self.news_events,
                'stock_news': self.stock_news_events
            }
            with open(self.news_file, 'w') as file:
                json.dump(news_data, file, indent=4)
                print(f"Saved news events to {self.news_file}")
        except Exception as e:
            print(f"Error saving news to {self.news_file}: {e}")

    def add_custom_market_news(self, headline, sector, change, duration=None):
        """Add a custom market news event"""
        news_event = {
            "headline": headline,
            "impact": {"sector": sector, "change": change}
        }
        if duration:
            news_event["duration"] = duration
            
        self.news_events.append(news_event)
        self.save_news_to_json()
        return news_event
        
    def add_custom_stock_news(self, headline, stock_symbol, change):
        """Add a custom stock-specific news event"""
        news_event = {
            "headline": headline,
            "impact": {"stock": stock_symbol, "change": change}
        }
        self.stock_news_events.append(news_event)
        self.save_news_to_json()
        return news_event

    def generate_market_news(self, current_day):
        """Generate market-wide or sector news events"""
        if random.random() < 0.3:  # 30% chance of news event each day
            news_event = random.choice(self.news_events)
            self.news_feed.insert(0, f"Day {current_day}: {news_event['headline']}")
            return news_event
        return None

    def generate_stock_news(self, current_day):
        """Generate stock-specific news events"""
        if random.random() < 0.2:  # 20% chance of stock-specific news
            stock_news = random.choice(self.stock_news_events)
            self.news_feed.insert(0, f"Day {current_day}: {stock_news['headline']}")
            return stock_news
        return None

    def add_dividend_news(self, current_day, stock_name, symbol, dividend_total):
        """Add dividend payout news"""
        self.news_feed.insert(0, f"Day {current_day}: Received ${dividend_total:.2f} in dividends from {stock_name}")

