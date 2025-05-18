import random
import json
import os
from models.stock import Stock
from models.portfolio import Portfolio
from models.news import NewsGenerator
# 在文件顶部导入成就管理器
from models.achievement import AchievementManager


class MarketSimulator:
    def __init__(self, config_file="data/config.json"):
        # 加载配置文件
        self.config = self.load_config(config_file)
        
        # Define sectors
        self.sectors = ["Technology", "Healthcare", "Finance", "Energy", "Consumer", "Crypto"]
        self.stocks_file = self.config["files"]["stocks_file"]
        
        # Load stocks from JSON file if it exists, otherwise use defaults
        if os.path.exists(self.stocks_file):
            self.load_stocks_from_json()
        else:
            # Create stocks with different characteristics
            self.stocks = [
                Stock("TechGiant", "TGT", 150.0, 2.5, "Technology", True, 0.5),
                Stock("MediHealth", "MHC", 85.0, 1.8, "Healthcare", True, 1.2),
                Stock("BankCorp", "BNK", 65.0, 1.5, "Finance", True, 2.5),
                Stock("EnergyOne", "ENO", 40.0, 2.2, "Energy", False, 0),
                Stock("RetailShop", "RSP", 55.0, 1.7, "Consumer", True, 1.0),
                Stock("StartupTech", "STU", 25.0, 3.5, "Technology", False, 0),
                Stock("PharmaCure", "PHC", 120.0, 2.0, "Healthcare", True, 0.8),
                Stock("InvestFund", "INF", 95.0, 1.6, "Finance", True, 1.8),
                Stock("OilDrill", "ODL", 70.0, 2.3, "Energy", True, 3.0),
                Stock("FoodMarket", "FMT", 45.0, 1.5, "Consumer", True, 1.5)
            ]
            
            # Save default stocks to JSON
            self.save_stocks_to_json()

        # Dictionary to track stocks by symbol
        self.stock_dict = {stock.symbol: stock for stock in self.stocks}

        # Game settings from config
        self.current_day = 0
        self.max_days = self.config["game"]["max_days"]

        # Initialize news generator
        self.news_generator = NewsGenerator(self.config["files"]["news_file"] if "news_file" in self.config["files"] else None)

        # Initialize portfolio with configurable starting cash
        self.portfolio = Portfolio(starting_cash=self.config["game"]["starting_cash"])
        
        # Initialize ongoing events list
        self.ongoing_events = []
        
        # 初始化成就管理器
        self.achievement_manager = AchievementManager()
    
    def load_config(self, config_file):
        """加载配置文件"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as file:
                    return json.load(file)
            else:
                # 默认配置
                default_config = {
                    "game": {
                        "starting_cash": 10000,
                        "max_days": 300
                    },
                    "files": {
                        "stocks_file": "data/stocks.json",
                        "news_file": "data/news.json"
                    },
                    "simulation": {
                        "news_event_chance": 0.3,
                        "stock_news_chance": 0.2,
                        "market_volatility": 1.0
                    }
                }
                
                # 确保data目录存在
                os.makedirs(os.path.dirname(config_file), exist_ok=True)
                
                # 保存默认配置
                with open(config_file, 'w') as file:
                    json.dump(default_config, file, indent=4)
                    
                return default_config
        except Exception as e:
            print(f"Error loading config from {config_file}: {e}")
            # 返回硬编码的默认值
            return {
                "game": {"starting_cash": 10000, "max_days": 300},
                "files": {"stocks_file": "data/stocks.json"},
                "simulation": {"news_event_chance": 0.3, "stock_news_chance": 0.2}
            }
        
    def load_stocks_from_json(self):
        """Load stocks from JSON file"""
        try:
            with open(self.stocks_file, 'r') as file:
                stocks_data = json.load(file)
                self.stocks = []
                
                for stock_data in stocks_data:
                    self.stocks.append(Stock(
                        stock_data["name"],
                        stock_data["symbol"],
                        stock_data["price"],
                        stock_data["volatility"],
                        stock_data["sector"],
                        stock_data["pays_dividend"],
                        stock_data["dividend_yield"]
                    ))
                print(f"Loaded {len(self.stocks)} stocks from {self.stocks_file}")
        except Exception as e:
            print(f"Error loading stocks from {self.stocks_file}: {e}")
            # Fall back to defaults if loading fails
            self.stocks = []
            
    def save_stocks_to_json(self):
        """Save current stocks to JSON file"""
        try:
            stocks_data = []
            for stock in self.stocks:
                stocks_data.append({
                    "name": stock.name,
                    "symbol": stock.symbol,
                    "price": stock.price,
                    "volatility": stock.volatility,
                    "sector": stock.sector,
                    "pays_dividend": stock.pays_dividend,
                    "dividend_yield": stock.dividend_yield
                })
                
            # 确保目录存在
            os.makedirs(os.path.dirname(self.stocks_file), exist_ok=True)
                
            with open(self.stocks_file, 'w') as file:
                json.dump(stocks_data, file, indent=4)
                print(f"Saved {len(stocks_data)} stocks to {self.stocks_file}")
        except Exception as e:
            print(f"Error saving stocks to {self.stocks_file}: {e}")
            
    def add_custom_stock(self, name, symbol, price, volatility, sector, pays_dividend, dividend_yield):
        """Add a custom stock to the market"""
        # Check if symbol already exists
        if symbol in self.stock_dict:
            print(f"Stock with symbol {symbol} already exists")
            return False
            
        # Create new stock
        new_stock = Stock(name, symbol, price, volatility, sector, pays_dividend, dividend_yield)
        self.stocks.append(new_stock)
        self.stock_dict[symbol] = new_stock
        
        # Save updated stocks to JSON
        self.save_stocks_to_json()
        return True

    def process_ongoing_events(self, sector_movements):
        """Process any ongoing events and update their effects"""
        # Process any active ongoing events
        i = 0
        while i < len(self.ongoing_events):
            event = self.ongoing_events[i]
            event["days_remaining"] -= 1
            
            # Reduce impact factor as event ages
            event["impact_factor"] *= 0.8
            
            # Apply the effect with reduced impact
            if event["event"]["impact"]["sector"] == "all":
                for sector in self.sectors:
                    sector_movements[sector] += event["event"]["impact"]["change"] * event["impact_factor"]
            else:
                affected_sector = event["event"]["impact"]["sector"]
                sector_movements[affected_sector] += event["event"]["impact"]["change"] * event["impact_factor"]
            
            # Remove event if it has expired
            if event["days_remaining"] <= 0:
                self.ongoing_events.pop(i)
            else:
                i += 1
                
        return sector_movements

    def simulate_day(self):
        """Simulate a single market day"""
        if self.current_day >= self.max_days:
            return False
    
        # 保存当前现金值
        current_cash = self.portfolio.cash
        print(f"开始模拟前 - 现金: ${current_cash:.2f}")
    
        self.current_day += 1
        affected_stock = None
        
        # Initialize sector movements
        sector_movements = {sector: random.normalvariate(0, 1.0) for sector in self.sectors}
        
        # Check for active ongoing events
        self.process_ongoing_events(sector_movements)
        
        # Generate market news
        news_event = self.news_generator.generate_market_news(self.current_day)
        if news_event:
            # Check if this is a multi-day event
            if "duration" in news_event:
                self.ongoing_events.append({
                    "event": news_event,
                    "days_remaining": news_event["duration"],
                    "impact_factor": 1.0  # Full impact on first day
                })
            if news_event["impact"]["sector"] == "all":
                for sector in self.sectors:
                    sector_movements[sector] += news_event["impact"]["change"]
            else:
                sector_movements[news_event["impact"]["sector"]] += news_event["impact"]["change"]
        
        # Generate stock-specific news
        stock_news = self.news_generator.generate_stock_news(self.current_day)
        if stock_news:
            affected_stock = stock_news["impact"]["stock"]
        
            # Apply direct impact to stock
            stock = self.stock_dict.get(affected_stock)
            if stock:
                change_percent = stock_news["impact"]["change"]
                current_price = stock.price
                stock.price = max(0.1, current_price * (1 + change_percent / 100))
        
        # Update each stock price
        for stock in self.stocks:
            if stock.symbol != affected_stock if affected_stock else True:
                stock.update_price(sector_movements[stock.sector])
        
            # Check for dividends
            dividend = stock.check_dividend(self.current_day)
            if dividend > 0 and stock.symbol in self.portfolio.stocks:
                shares_owned = self.portfolio.stocks[stock.symbol]
                dividend_total = dividend * shares_owned
                self.portfolio.cash += dividend_total
                
                # 记录股息交易
                self.portfolio.add_dividend_transaction(self.current_day, stock.symbol, dividend_total)
                
                self.news_generator.add_dividend_news(
                    self.current_day, stock.name, stock.symbol, dividend_total
                )
        
        # Update portfolio value history
        stock_prices = {stock.symbol: stock.price for stock in self.stocks}
        self.portfolio.update_net_worth(stock_prices)
        
        # 检查成就
        unlocked_achievements = self.achievement_manager.check_achievements(self, self.portfolio)
        
        # 如果有新解锁的成就，添加到新闻提要
        for achievement in unlocked_achievements:
            self.news_generator.news_feed.insert(0, 
                f"Day {self.current_day}: 🏆 成就解锁 - {achievement.name}: {achievement.description}")
        
        # 删除这段代码，因为它会导致卖出股票后的现金被重置
        # if self.portfolio.cash != current_cash:
        #     if abs(self.portfolio.cash - current_cash) > 0.01 and not any(dividend > 0 for stock in self.stocks for dividend in [stock.check_dividend(self.current_day)]):
        #         print(f"现金值从 ${current_cash:.2f} 变为 ${self.portfolio.cash:.2f}，正在恢复...")
        #         self.portfolio.cash = current_cash
        
        print(f"模拟结束后 - 现金: ${self.portfolio.cash:.2f}")
        return True

    @property
    def news_feed(self):
        return self.news_generator.news_feed

    def reset(self, reset_portfolio=False):
        """Reset the market state while optionally preserving portfolio"""
        # Store current portfolio if we're not resetting it
        current_portfolio = None
        if not reset_portfolio:
            current_portfolio = self.portfolio
        
        # Reset game settings
        self.current_day = 0
        self.ongoing_events = []
        
        # Reset stocks to initial state
        if os.path.exists(self.stocks_file):
            self.load_stocks_from_json()
        
        # Reset news generator
        self.news_generator = NewsGenerator()
        
        # Either restore the previous portfolio or create a new one
        if not reset_portfolio and current_portfolio:
            self.portfolio = current_portfolio
        else:
            self.portfolio = Portfolio(starting_cash=10000)
        
        # Update the stock dictionary
        self.stock_dict = {stock.symbol: stock for stock in self.stocks}
        
        return True
