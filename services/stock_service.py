from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dal.unit_of_work import UnitOfWork
from models.stock.stock import Stock
from models.stock.stock_price import StockPrice
from models.stock.portfolio import Portfolio, PortfolioItem
from models.finance.account import Account
from models.auth.user import User
from core.event_bus import EventBus
from core.events import TimeTickEvent, NewsPublishedEvent
from services.time_service import TimeService
from services.currency_service import CurrencyService
from core.game_time import GameTime
import json
import os
import random
import math
import uuid
from decimal import Decimal
from sqlalchemy import select

class StockService:
    """股票服务，管理股票市场模拟和交易"""
    
    def __init__(self, uow: UnitOfWork, event_bus: EventBus, currency_service: CurrencyService, time_service: TimeService):
        self.uow = uow
        self.event_bus = event_bus
        self.currency_service = currency_service
        self.time_service = time_service
        self._stocks_cache = None
        
        # 订阅事件
        self.event_bus.subscribe(TimeTickEvent, self._on_time_tick)
        self.event_bus.subscribe(NewsPublishedEvent, self._on_news_published)
    
    def _load_stock_definitions(self) -> Dict[str, Any]:
        """加载股票定义文件"""
        if self._stocks_cache is None:
            stocks_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'definitions', 'jc_stocks.json')
            with open(stocks_file, 'r', encoding='utf-8') as f:
                self._stocks_cache = json.load(f)
        return self._stocks_cache
    
    async def _on_time_tick(self, event: TimeTickEvent):
        """处理时间滴答事件，更新股价"""
        if not self.time_service.is_market_hours():
            return
        # 使用time_service获取当前游戏时间，避免GUI事件循环问题
        current_time = self.time_service.get_game_time()
        await self._update_stock_prices(current_time)
    
    async def _on_news_published(self, event: NewsPublishedEvent):
        """处理新闻发布事件，影响股价"""
        # 从事件数据中获取影响信息
        impact_type = event.data.get('impact_type', 'neutral')
        impact_strength = event.severity
        
        if impact_type != 'neutral' and impact_strength != 0.0:
            await self._apply_news_impact(impact_type, impact_strength)
    
    async def _update_stock_prices(self, current_time: datetime):
        """更新所有股票价格（基于参考体系改进）"""
        async with self.uow:
            stmt = select(Stock)
            result = await self.uow.session.execute(stmt)
            stocks = result.scalars().all()
            
            for stock in stocks:
                try:
                    old_price = stock.current_price or 0
                    new_price = self._calculate_new_price(stock)
                    
                    # 创建价格记录（参考体系）
                    price_record = StockPrice(
                        id=str(uuid.uuid4()),
                        stock_id=stock.id,
                        price=new_price,
                        opening_price=stock.opening_price or new_price,
                        closing_price=new_price,
                        high_price=max(float(stock.day_high or new_price), float(new_price)),
                        low_price=min(float(stock.day_low or new_price), float(new_price)),
                        volume=int(stock.volume or 1000000) * random.randint(80, 120) // 100,
                        timestamp=current_time
                    )
                    self.uow.add(price_record)
                    
                    # 更新股票当前价格和相关指标（参考体系）
                    stock.current_price = new_price
                    stock.previous_close = old_price
                    stock.day_high = max(float(stock.day_high or new_price), float(new_price))
                    stock.day_low = min(float(stock.day_low or new_price), float(new_price))
                    stock.volume = price_record.volume
                    
                    # 计算价格变化
                    price_change = float(new_price) - float(old_price)
                    stock.closing_price = new_price
                    
                    # 更新PE比率（参考体系）
                    if stock.eps and float(stock.eps) > 0:
                        stock.pe_ratio = float(new_price) / float(stock.eps)
                    
                except Exception as e:
                    print(f"更新股票 {stock.symbol} 价格时出错: {e}")
                    continue
            
            await self.uow.commit()
    
    def _calculate_new_price(self, stock: Stock) -> Decimal:
        """计算股票新价格（更加复杂和贴切实际市场）"""
        current_price = stock.current_price or 0
        volatility = stock.volatility or 0.02
        volume = stock.volume or 1000000
        beta = stock.beta or 1.0
        pe_ratio = stock.pe_ratio or 15.0
        market_cap = stock.market_cap or 1000000000
        rsi = stock.rsi or 50.0
        moving_avg_50 = stock.moving_avg_50 or current_price
        moving_avg_200 = stock.moving_avg_200 or current_price
        
        # 1. 基础随机波动（基于历史波动率）
        random_change = random.gauss(0, float(volatility))
        
        # 2. 技术指标因子
        # RSI因子：超买超卖调整
        rsi_factor = 1.0
        if float(rsi) > 70:  # 超买状态，倾向于下跌
            rsi_factor = 1.0 - (float(rsi) - 70) * 0.001
        elif float(rsi) < 30:  # 超卖状态，倾向于上涨
            rsi_factor = 1.0 + (30 - float(rsi)) * 0.001
        
        # 移动平均线因子
        ma_factor = 1.0
        if float(current_price) > float(moving_avg_50) > float(moving_avg_200):
            ma_factor = 1.002  # 多头排列，轻微上涨倾向
        elif float(current_price) < float(moving_avg_50) < float(moving_avg_200):
            ma_factor = 0.998  # 空头排列，轻微下跌倾向
        
        # 3. 基本面因子
        # PE比率因子：过高或过低的PE都有调整压力
        pe_factor = 1.0
        if float(pe_ratio) > 30:  # 高PE，估值偏高
            pe_factor = 1.0 - (float(pe_ratio) - 30) * 0.0001
        elif float(pe_ratio) < 10:  # 低PE，估值偏低
            pe_factor = 1.0 + (10 - float(pe_ratio)) * 0.0001
        
        # 市值因子：小市值股票波动更大
        market_cap_factor = 1.0
        market_cap_float = float(market_cap)
        if market_cap_float < 5000000000:  # 小市值
            market_cap_factor = 1.02
        elif market_cap_float > 50000000000:  # 大市值
            market_cap_factor = 0.98
        
        # 4. 成交量因子（参考体系）
        volume_factor = 1.0 - (min(float(volume), 100000000) / 100000000) * 0.15
        
        # 5. 趋势因子（基于股票类型）
        trend_factor = self._get_trend_factor(stock.sector)
        
        # 6. 市场情绪因子（模拟市场整体情绪）
        sentiment_factor = 1.0 + random.uniform(-0.02, 0.02)
        
        # 7. 行业轮动因子
        sector_rotation_factor = self._get_sector_rotation_factor()
        
        # 8. 事件影响因子（更复杂的模拟）
        event_factor = 1.0
        if random.random() < 0.15:  # 15%概率有事件影响
            event_type = random.choice(['earnings', 'merger', 'regulation', 'market'])
            magnitude = random.uniform(0.005, 0.08)
            
            if event_type == 'earnings':
                # 财报事件影响更大
                magnitude *= 1.5
            elif event_type == 'merger':
                # 并购事件影响中等
                magnitude *= 1.2
            elif event_type == 'regulation':
                # 监管事件影响因行业而异
                if stock.sector in ['金融', '医药']:
                    magnitude *= 1.8
            
            if random.random() < 0.4:  # 40%概率是负面影响
                magnitude = -magnitude
            
            event_factor = 1 + magnitude
        
        # 9. 综合所有因子计算价格变化
        total_change = (random_change * 0.3 +  # 随机因素权重30%
                       (rsi_factor - 1) * 0.15 +  # 技术指标权重15%
                       (ma_factor - 1) * 0.1 +   # 移动平均线权重10%
                       (pe_factor - 1) * 0.1 +    # PE比率权重10%
                       (market_cap_factor - 1) * 0.05 +  # 市值因子权重5%
                       volume_factor * 0.05 +     # 成交量因子权重5%
                       trend_factor * 0.1 +      # 趋势因子权重10%
                       (sentiment_factor - 1) * 0.05 +  # 市场情绪权重5%
                       sector_rotation_factor * 0.05 +  # 行业轮动权重5%
                       (event_factor - 1) * 0.1)  # 事件影响权重10%
        
        # 10. 应用贝塔系数放大/缩小波动
        total_change *= float(beta)
        
        # 11. 限制单次变化幅度（更严格的限制）
        max_change = 0.08  # 最大8%变化
        if abs(total_change) > max_change:
            total_change = max_change if total_change > 0 else -max_change
        
        new_price = float(current_price) * (1 + total_change)
        
        # 12. 确保价格不会过低（更严格的价格保护）
        min_price = float(stock.ipo_price or 1) * 0.2  # 最低为IPO价格的20%
        new_price = max(new_price, min_price)
        
        # 13. 价格精度处理
        new_price = round(new_price, 2)
        
        return Decimal(str(new_price))
    
    def _get_sector_rotation_factor(self) -> float:
        """获取行业轮动因子，模拟市场热点切换"""
        # 模拟行业轮动周期
        rotation_cycle = {
            '科技': 0.003,
            '金融': 0.001,
            '医药': 0.002,
            '能源': -0.001,
            '消费': 0.0015,
            '工业': 0.0005,
            '房地产': -0.002
        }
        
        # 添加随机性模拟轮动不确定性
        base_factor = random.uniform(-0.002, 0.002)
        
        return base_factor
    
    def _get_trend_factor(self, sector: str) -> float:
        """根据行业获取趋势因子"""
        sector_trends = {
            '科技': 0.001,
            '金融': 0.0005,
            '医药': 0.0008,
            '能源': -0.0002,
            '消费': 0.0003,
            '工业': 0.0001
        }
        return sector_trends.get(sector, 0.0)
    
    async def _apply_news_impact(self, impact_type: str, impact_strength: float):
        """应用新闻对股价的影响"""
        async with self.uow:
            stmt = select(Stock)
            result = await self.uow.session.execute(stmt)
            stocks = result.scalars().all()
            
            for stock in stocks:
                # 根据新闻类型和股票行业计算影响
                sector_sensitivity = self._get_sector_sensitivity(stock.sector, impact_type)
                impact_factor = impact_strength * sector_sensitivity
                
                current_price = stock.current_price or 0
                ipo_price = stock.ipo_price or 1
                
                if impact_type == 'positive':
                    price_change = float(current_price) * impact_factor
                elif impact_type == 'negative':
                    price_change = -float(current_price) * impact_factor
                else:
                    continue
                
                new_price = float(current_price) + price_change
                new_price = max(new_price, float(ipo_price) * 0.1)
                stock.current_price = Decimal(str(round(new_price, 2)))
            
            await self.uow.commit()
    
    def _get_sector_sensitivity(self, sector: str, impact_type: str) -> float:
        """获取行业对新闻的敏感度"""
        sensitivities = {
            '科技': {'positive': 1.2, 'negative': 1.1, 'market': 1.0},
            '金融': {'positive': 1.0, 'negative': 1.3, 'market': 1.2},
            '医药': {'positive': 0.8, 'negative': 0.7, 'market': 0.6},
            '能源': {'positive': 1.1, 'negative': 1.2, 'market': 1.1},
            '消费': {'positive': 0.9, 'negative': 0.8, 'market': 0.9},
            '工业': {'positive': 1.0, 'negative': 1.0, 'market': 1.0}
        }
        return sensitivities.get(sector, {}).get(impact_type, 0.5)
    
    async def initialize_stocks(self):
        """初始化股票数据（更完整的初始化）"""
        stock_definitions = self._load_stock_definitions()
        current_time = self.time_service.get_game_time()
        
        async with self.uow:
            for stock_data in stock_definitions['stocks']:
                # 检查股票是否已存在
                stmt = select(Stock).filter_by(symbol=stock_data['ticker'])
                result = await self.uow.session.execute(stmt)
                existing_stock = result.scalars().first()
                if existing_stock:
                    # 如果股票已存在，更新其数据
                    await self._update_existing_stock(existing_stock, stock_data)
                    continue
                
                # 创建新股票
                stock = Stock(
                    symbol=stock_data['ticker'],
                    name=stock_data['name'],
                    sector=stock_data['sector'],
                    ipo_price=Decimal(str(stock_data['ipo_price'])),
                    current_price=Decimal(str(stock_data['current_price'])),
                    market_cap=Decimal(str(stock_data['market_cap'])),
                    volatility=Decimal(str(stock_data['volatility'])),
                    description=stock_data.get('description', ''),
                    
                    # 财务指标
                    pe_ratio=Decimal(str(stock_data.get('pe_ratio', 0))) if stock_data.get('pe_ratio') else None,
                    beta=Decimal(str(stock_data.get('beta', 0))) if stock_data.get('beta') else None,
                    dividend_yield=Decimal(str(stock_data.get('dividend_yield', 0))) if stock_data.get('dividend_yield') else None,
                    eps=Decimal(str(stock_data.get('eps', 0))) if stock_data.get('eps') else None,
                    book_value=Decimal(str(stock_data.get('book_value', 0))) if stock_data.get('book_value') else None,
                    debt_to_equity=Decimal(str(stock_data.get('debt_to_equity', 0))) if stock_data.get('debt_to_equity') else None,
                    
                    # 技术指标
                    rsi=Decimal(str(stock_data.get('rsi', 0))) if stock_data.get('rsi') else None,
                    moving_avg_50=Decimal(str(stock_data.get('moving_avg_50', 0))) if stock_data.get('moving_avg_50') else None,
                    moving_avg_200=Decimal(str(stock_data.get('moving_avg_200', 0))) if stock_data.get('moving_avg_200') else None,
                    
                    # 市场表现
                    year_high=Decimal(str(stock_data.get('year_high', 0))) if stock_data.get('year_high') else None,
                    year_low=Decimal(str(stock_data.get('year_low', 0))) if stock_data.get('year_low') else None,
                    ytd_return=Decimal(str(stock_data.get('ytd_return', 0))) if stock_data.get('ytd_return') else None,
                    
                    # 初始化其他价格相关字段
                    opening_price=Decimal(str(stock_data['current_price'])),
                    closing_price=Decimal(str(stock_data['current_price'])),
                    previous_close=Decimal(str(stock_data['current_price'])),
                    day_high=Decimal(str(stock_data['current_price'])),
                    day_low=Decimal(str(stock_data['current_price'])),
                    volume=1000000  # 初始成交量
                )
                self.uow.add(stock)
                await self.uow.flush()  # 确保股票已保存并获取ID
                
                # 为新股票创建初始价格历史记录
                await self._create_initial_price_history(stock, current_time)
            
            await self.uow.commit()
            print(f"成功初始化 {len(stock_definitions['stocks'])} 支股票")
    
    async def _update_existing_stock(self, stock: Stock, stock_data: dict):
        """更新已存在的股票数据"""
        # 更新基本信息
        stock.name = stock_data['name']
        stock.sector = stock_data['sector']
        stock.description = stock_data.get('description', '')
        
        # 更新财务指标
        if stock_data.get('pe_ratio'):
            stock.pe_ratio = Decimal(str(stock_data['pe_ratio']))
        if stock_data.get('beta'):
            stock.beta = Decimal(str(stock_data['beta']))
        if stock_data.get('dividend_yield'):
            stock.dividend_yield = Decimal(str(stock_data['dividend_yield']))
        if stock_data.get('eps'):
            stock.eps = Decimal(str(stock_data['eps']))
        if stock_data.get('book_value'):
            stock.book_value = Decimal(str(stock_data['book_value']))
        if stock_data.get('debt_to_equity'):
            stock.debt_to_equity = Decimal(str(stock_data['debt_to_equity']))
        
        # 更新技术指标
        if stock_data.get('rsi'):
            stock.rsi = Decimal(str(stock_data['rsi']))
        if stock_data.get('moving_avg_50'):
            stock.moving_avg_50 = Decimal(str(stock_data['moving_avg_50']))
        if stock_data.get('moving_avg_200'):
            stock.moving_avg_200 = Decimal(str(stock_data['moving_avg_200']))
        
        # 更新市场表现
        if stock_data.get('year_high'):
            stock.year_high = Decimal(str(stock_data['year_high']))
        if stock_data.get('year_low'):
            stock.year_low = Decimal(str(stock_data['year_low']))
        if stock_data.get('ytd_return'):
            stock.ytd_return = Decimal(str(stock_data['ytd_return']))
        
        # 更新市值和波动率
        stock.market_cap = Decimal(str(stock_data['market_cap']))
        stock.volatility = Decimal(str(stock_data['volatility']))
        
        print(f"更新股票 {stock.symbol} 的数据")
    
    async def _create_initial_price_history(self, stock: Stock, current_time: datetime):
        """为股票创建初始价格历史记录"""
        base_price = float(stock.current_price)
        
        # 创建过去30天的价格历史
        for i in range(30, 0, -1):
            # 模拟历史价格波动
            days_ago = current_time - timedelta(days=i)
            
            # 生成历史价格（基于当前价格的随机波动）
            price_change = random.uniform(-0.05, 0.05)  # 5%的日波动范围
            historical_price = base_price * (1 + price_change)
            
            # 确保价格不会过低
            min_price = float(stock.ipo_price) * 0.2
            historical_price = max(historical_price, min_price)
            
            # 创建价格记录
            price_record = StockPrice(
                id=str(uuid.uuid4()),
                stock_id=stock.id,
                price=Decimal(str(round(historical_price, 2))),
                opening_price=Decimal(str(round(historical_price, 2))),
                closing_price=Decimal(str(round(historical_price, 2))),
                high_price=Decimal(str(round(historical_price * 1.02, 2))),  # 最高价略高
                low_price=Decimal(str(round(historical_price * 0.98, 2))),   # 最低价略低
                volume=random.randint(500000, 2000000),  # 随机成交量
                timestamp=days_ago
            )
            self.uow.add(price_record)
        
        # 创建当前时间的价格记录
        current_price_record = StockPrice(
            id=str(uuid.uuid4()),
            stock_id=stock.id,
            price=stock.current_price,
            opening_price=stock.opening_price or stock.current_price,
            closing_price=stock.closing_price or stock.current_price,
            high_price=stock.day_high or stock.current_price,
            low_price=stock.day_low or stock.current_price,
            volume=stock.volume or 1000000,
            timestamp=current_time
        )
        self.uow.add(current_price_record)
    
    async def get_all_stocks(self) -> List[Stock]:
        """获取所有股票"""
        async with self.uow:
            stmt = select(Stock)
            result = await self.uow.session.execute(stmt)
            return result.scalars().all()
    
    async def get_stock_by_ticker(self, ticker: str) -> Optional[Stock]:
        """根据代码获取股票"""
        async with self.uow:
            stmt = select(Stock).filter_by(symbol=ticker)
            result = await self.uow.session.execute(stmt)
            return result.scalars().first()
    
    async def get_stock_price_history(self, ticker: str, days: int = 30) -> List[StockPrice]:
        """获取股票价格历史"""
        stock = await self.get_stock_by_ticker(ticker)
        if not stock:
            return []
        
        cutoff_date = self.time_service.get_current_time() - timedelta(days=days)
        
        async with self.uow:
            stmt = select(StockPrice).filter(
                StockPrice.stock_id == stock.id,
                StockPrice.timestamp >= cutoff_date
            ).order_by(StockPrice.timestamp.desc())
            result = await self.uow.session.execute(stmt)
            return result.scalars().all()
    
    async def buy_stock(self, user_id: int, ticker: str, quantity: int) -> Dict[str, Any]:
        """买入股票"""
        stock = await self.get_stock_by_ticker(ticker)
        if not stock:
            return {'success': False, 'message': f'股票 {ticker} 不存在'}
        
        if quantity <= 0:
            return {'success': False, 'message': '购买数量必须大于0'}
        
        total_cost = stock.current_price * quantity
        
        async with self.uow:
            # 检查用户账户余额
            stmt = select(Account).filter_by(user_id=user_id, currency_code='JCC')
            result = await self.uow.session.execute(stmt)
            account = result.scalars().first()
            if not account or account.balance < total_cost:
                return {'success': False, 'message': f'余额不足，需要 {total_cost} JCC'}
            
            # 扣除费用
            account.balance -= total_cost
            
            # 获取或创建投资组合
            stmt = select(Portfolio).filter_by(user_id=user_id)
            result = await self.uow.session.execute(stmt)
            portfolio = result.scalars().first()
            if not portfolio:
                portfolio = Portfolio(user_id=user_id, name=f"User {user_id}'s Portfolio")
                self.uow.add(portfolio)
                await self.uow.flush()

            # 更新或创建投资组合项目
            stmt = select(PortfolioItem).filter_by(
                portfolio_id=portfolio.id, 
                stock_id=stock.id
            )
            result = await self.uow.session.execute(stmt)
            portfolio_item = result.scalars().first()
            
            if portfolio_item:
                # 计算新的平均成本
                total_shares = portfolio_item.quantity + quantity
                total_value = (portfolio_item.average_cost * portfolio_item.quantity) + total_cost
                portfolio_item.average_cost = total_value / total_shares
                portfolio_item.quantity = total_shares
            else:
                portfolio_item = PortfolioItem(
                    portfolio_id=portfolio.id,
                    stock_id=stock.id,
                    quantity=quantity,
                    average_cost=stock.current_price
                )
                self.uow.add(portfolio_item)
            
            await self.uow.commit()
            
            # 发布事件
            current_price = stock.current_price or 0
            self.event_bus.publish('stock_purchased', {
                'user_id': user_id,
                'ticker': ticker,
                'quantity': quantity,
                'price': float(current_price),
                'total_cost': float(total_cost)
            })
            
            return {
                'success': True,
                'message': f'成功购买 {quantity} 股 {ticker}，总计 {total_cost} JCC'
            }
    
    async def sell_stock(self, user_id: int, ticker: str, quantity: int) -> Dict[str, Any]:
        """卖出股票"""
        stock = await self.get_stock_by_ticker(ticker)
        if not stock:
            return {'success': False, 'message': f'股票 {ticker} 不存在'}
        
        if quantity <= 0:
            return {'success': False, 'message': '卖出数量必须大于0'}
        
        async with self.uow:
            # 检查持仓
            stmt = select(Portfolio).filter_by(user_id=user_id)
            result = await self.uow.session.execute(stmt)
            portfolio = result.scalars().first()
            if not portfolio:
                return {'success': False, 'message': '用户没有投资组合'}

            stmt = select(PortfolioItem).filter_by(
                portfolio_id=portfolio.id,
                stock_id=stock.id
            )
            result = await self.uow.session.execute(stmt)
            portfolio_item = result.scalars().first()
            
            if not portfolio_item or portfolio_item.quantity < quantity:
                return {'success': False, 'message': f'持仓不足，当前持有 {portfolio_item.quantity if portfolio_item else 0} 股'}
            
            # 计算收益
            total_revenue = stock.current_price * quantity
            
            # 更新账户余额
            stmt = select(Account).filter_by(user_id=user_id, currency_code='JCC')
            result = await self.uow.session.execute(stmt)
            account = result.scalars().first()
            account.balance += total_revenue
            
            # 更新投资组合
            portfolio_item.quantity -= quantity
            if portfolio_item.quantity == 0:
                self.uow.delete(portfolio_item)
            
            await self.uow.commit()
            
            # 发布事件
            current_price = stock.current_price or 0
            self.event_bus.publish('stock_sold', {
                'user_id': user_id,
                'ticker': ticker,
                'quantity': quantity,
                'price': float(current_price),
                'total_revenue': float(total_revenue)
            })
            
            return {
                'success': True,
                'message': f'成功卖出 {quantity} 股 {ticker}，获得 {total_revenue} JCC'
            }
    
    async def get_user_portfolio(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户投资组合"""
        async with self.uow:
            stmt = select(Portfolio).filter_by(user_id=user_id)
            result = await self.uow.session.execute(stmt)
            portfolio = result.scalars().first()
            if not portfolio:
                return []

            stmt = select(PortfolioItem).filter_by(portfolio_id=portfolio.id)
            result = await self.uow.session.execute(stmt)
            portfolio_items = result.scalars().all()
            
            result = []
            for item in portfolio_items:
                stmt = select(Stock).filter_by(id=item.stock_id)
                stock_result = await self.uow.session.execute(stmt)
                stock = stock_result.scalars().first()
                if stock:
                    current_value = stock.current_price * item.quantity
                    cost_value = item.average_cost * item.quantity
                    profit_loss = current_value - cost_value
                    profit_loss_pct = (profit_loss / cost_value) * 100 if cost_value > 0 else 0
                    
                    current_price = stock.current_price or 0
                    result.append({
                        'ticker': stock.symbol,
                        'name': stock.name,
                        'quantity': item.quantity,
                        'average_cost': float(item.average_cost),
                        'current_price': float(current_price),
                        'current_value': float(current_value),
                        'cost_value': float(cost_value),
                        'profit_loss': float(profit_loss),
                        'profit_loss_pct': float(profit_loss_pct)
                    })
            
            return result
    
    async def get_market_summary(self) -> Dict[str, Any]:
        """获取市场概况"""
        async with self.uow:
            stmt = select(Stock)
            result = await self.uow.session.execute(stmt)
            stocks = result.scalars().all()
            
            if not stocks:
                return {'total_stocks': 0}
            
            total_market_cap = sum(float(stock.market_cap) for stock in stocks)
            avg_price_change = 0  # 需要计算价格变化
            
            # 按行业分组
            sectors = {}
            for stock in stocks:
                if stock.sector not in sectors:
                    sectors[stock.sector] = {'count': 0, 'market_cap': 0}
                sectors[stock.sector]['count'] += 1
                sectors[stock.sector]['market_cap'] += float(stock.market_cap)
            
            return {
                'total_stocks': len(stocks),
                'total_market_cap': total_market_cap,
                'sectors': sectors,
                'avg_price_change': avg_price_change,
            }
    
    async def get_market_statistics(self) -> Dict[str, Any]:
        """获取市场统计数据"""
        async with self.uow:
            stmt = select(Stock)
            result = await self.uow.session.execute(stmt)
            stocks = result.scalars().all()
            
            if not stocks:
                return {
                    'total_stocks': 0,
                    'total_market_cap': 0,
                    'average_price': 0,
                    'highest_price': 0,
                    'lowest_price': 0,
                    'total_volume': 0,
                    'rising_stocks': 0,
                    'falling_stocks': 0,
                    'unchanged_stocks': 0
                }
            
            # 计算基本统计数据
            prices = [float(stock.current_price or 0) for stock in stocks]
            volumes = [float(stock.volume or 0) for stock in stocks]
            market_caps = [float(stock.market_cap or 0) for stock in stocks]
            
            # 计算上涨下跌股票数量
            rising_stocks = 0
            falling_stocks = 0
            unchanged_stocks = 0
            
            for stock in stocks:
                current_price = float(stock.current_price or 0)
                previous_close = float(stock.previous_close or current_price)
                
                if current_price > previous_close:
                    rising_stocks += 1
                elif current_price < previous_close:
                    falling_stocks += 1
                else:
                    unchanged_stocks += 1
            
            return {
                'total_stocks': len(stocks),
                'total_market_cap': sum(market_caps),
                'average_price': sum(prices) / len(prices),
                'highest_price': max(prices),
                'lowest_price': min(prices),
                'total_volume': sum(volumes),
                'rising_stocks': rising_stocks,
                'falling_stocks': falling_stocks,
                'unchanged_stocks': unchanged_stocks
             }
