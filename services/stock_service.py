from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dal.database import get_session
from models.stock.stock import Stock
from models.stock.stock_price import StockPrice
from models.stock.portfolio import Portfolio
from models.finance.account import Account
from models.auth.user import User
from core.event_bus import EventBus
from services.time_service import TimeService
from services.currency_service import CurrencyService
import json
import os
import random
import math
from decimal import Decimal

class StockService:
    """股票服务，管理股票市场模拟和交易"""
    
    def __init__(self, event_bus: EventBus, currency_service: CurrencyService, time_service: TimeService):
        self.event_bus = event_bus
        self.currency_service = currency_service
        self.time_service = time_service
        self._stocks_cache = None
        
        # 订阅事件
        self.event_bus.subscribe('time_tick', self._on_time_tick)
        self.event_bus.subscribe('news_published', self._on_news_published)
    
    def _load_stock_definitions(self) -> Dict[str, Any]:
        """加载股票定义文件"""
        if self._stocks_cache is None:
            stocks_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'definitions', 'jc_stocks.json')
            with open(stocks_file, 'r', encoding='utf-8') as f:
                self._stocks_cache = json.load(f)
        return self._stocks_cache
    
    def _on_time_tick(self, event_data: Dict[str, Any]):
        """处理时间滴答事件，更新股价"""
        self._update_stock_prices()
    
    def _on_news_published(self, event_data: Dict[str, Any]):
        """处理新闻发布事件，影响股价"""
        impact_type = event_data.get('impact_type', 'neutral')
        impact_strength = event_data.get('impact_strength', 0.0)
        
        if impact_type != 'neutral' and impact_strength != 0.0:
            self._apply_news_impact(impact_type, impact_strength)
    
    def _update_stock_prices(self):
        """更新所有股票价格"""
        with get_session() as session:
            stocks = session.query(Stock).all()
            
            for stock in stocks:
                new_price = self._calculate_new_price(stock)
                
                # 创建价格记录
                price_record = StockPrice(
                    stock_id=stock.id,
                    price=new_price,
                    volume=random.randint(1000, 100000),
                    timestamp=self.time_service.get_current_time()
                )
                session.add(price_record)
                
                # 更新股票当前价格
                stock.current_price = new_price
            
            session.commit()
    
    def _calculate_new_price(self, stock: Stock) -> Decimal:
        """计算股票新价格"""
        current_price = stock.current_price
        volatility = stock.volatility
        
        # 基础随机波动
        random_factor = random.gauss(0, float(volatility))
        
        # 趋势因子（基于股票类型）
        trend_factor = self._get_trend_factor(stock.sector)
        
        # 计算价格变化
        price_change = float(current_price) * (random_factor + trend_factor)
        new_price = float(current_price) + price_change
        
        # 确保价格不会过低
        min_price = float(stock.ipo_price) * 0.1
        new_price = max(new_price, min_price)
        
        return Decimal(str(round(new_price, 2)))
    
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
    
    def _apply_news_impact(self, impact_type: str, impact_strength: float):
        """应用新闻对股价的影响"""
        with get_session() as session:
            stocks = session.query(Stock).all()
            
            for stock in stocks:
                # 根据新闻类型和股票行业计算影响
                sector_sensitivity = self._get_sector_sensitivity(stock.sector, impact_type)
                impact_factor = impact_strength * sector_sensitivity
                
                if impact_type == 'positive':
                    price_change = float(stock.current_price) * impact_factor
                elif impact_type == 'negative':
                    price_change = -float(stock.current_price) * impact_factor
                else:
                    continue
                
                new_price = float(stock.current_price) + price_change
                new_price = max(new_price, float(stock.ipo_price) * 0.1)
                stock.current_price = Decimal(str(round(new_price, 2)))
            
            session.commit()
    
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
    
    def initialize_stocks(self):
        """初始化股票数据"""
        stock_definitions = self._load_stock_definitions()
        
        with get_session() as session:
            for stock_data in stock_definitions['stocks']:
                # 检查股票是否已存在
                existing_stock = session.query(Stock).filter_by(ticker=stock_data['ticker']).first()
                if existing_stock:
                    continue
                
                stock = Stock(
                    ticker=stock_data['ticker'],
                    name=stock_data['name'],
                    sector=stock_data['sector'],
                    ipo_price=Decimal(str(stock_data['ipo_price'])),
                    current_price=Decimal(str(stock_data['current_price'])),
                    market_cap=Decimal(str(stock_data['market_cap'])),
                    volatility=Decimal(str(stock_data['volatility'])),
                    description=stock_data.get('description', '')
                )
                session.add(stock)
            
            session.commit()
    
    def get_all_stocks(self) -> List[Stock]:
        """获取所有股票"""
        with get_session() as session:
            return session.query(Stock).all()
    
    def get_stock_by_ticker(self, ticker: str) -> Optional[Stock]:
        """根据代码获取股票"""
        with get_session() as session:
            return session.query(Stock).filter_by(ticker=ticker).first()
    
    def get_stock_price_history(self, ticker: str, days: int = 30) -> List[StockPrice]:
        """获取股票价格历史"""
        stock = self.get_stock_by_ticker(ticker)
        if not stock:
            return []
        
        cutoff_date = self.time_service.get_current_time() - timedelta(days=days)
        
        with get_session() as session:
            prices = session.query(StockPrice).filter(
                StockPrice.stock_id == stock.id,
                StockPrice.timestamp >= cutoff_date
            ).order_by(StockPrice.timestamp.desc()).all()
            
            return prices
    
    def buy_stock(self, user_id: int, ticker: str, quantity: int) -> Dict[str, Any]:
        """买入股票"""
        stock = self.get_stock_by_ticker(ticker)
        if not stock:
            return {'success': False, 'message': f'股票 {ticker} 不存在'}
        
        if quantity <= 0:
            return {'success': False, 'message': '购买数量必须大于0'}
        
        total_cost = stock.current_price * quantity
        
        with get_session() as session:
            # 检查用户账户余额
            account = session.query(Account).filter_by(user_id=user_id, currency_code='JCC').first()
            if not account or account.balance < total_cost:
                return {'success': False, 'message': f'余额不足，需要 {total_cost} JCC'}
            
            # 扣除费用
            account.balance -= total_cost
            
            # 更新或创建投资组合记录
            portfolio = session.query(Portfolio).filter_by(
                user_id=user_id, 
                stock_id=stock.id
            ).first()
            
            if portfolio:
                # 计算新的平均成本
                total_shares = portfolio.quantity + quantity
                total_value = (portfolio.average_cost * portfolio.quantity) + total_cost
                portfolio.average_cost = total_value / total_shares
                portfolio.quantity = total_shares
            else:
                portfolio = Portfolio(
                    user_id=user_id,
                    stock_id=stock.id,
                    quantity=quantity,
                    average_cost=stock.current_price
                )
                session.add(portfolio)
            
            session.commit()
            
            # 发布事件
            self.event_bus.publish('stock_purchased', {
                'user_id': user_id,
                'ticker': ticker,
                'quantity': quantity,
                'price': float(stock.current_price),
                'total_cost': float(total_cost)
            })
            
            return {
                'success': True,
                'message': f'成功购买 {quantity} 股 {ticker}，总计 {total_cost} JCC'
            }
    
    def sell_stock(self, user_id: int, ticker: str, quantity: int) -> Dict[str, Any]:
        """卖出股票"""
        stock = self.get_stock_by_ticker(ticker)
        if not stock:
            return {'success': False, 'message': f'股票 {ticker} 不存在'}
        
        if quantity <= 0:
            return {'success': False, 'message': '卖出数量必须大于0'}
        
        with get_session() as session:
            # 检查持仓
            portfolio = session.query(Portfolio).filter_by(
                user_id=user_id,
                stock_id=stock.id
            ).first()
            
            if not portfolio or portfolio.quantity < quantity:
                return {'success': False, 'message': f'持仓不足，当前持有 {portfolio.quantity if portfolio else 0} 股'}
            
            # 计算收益
            total_revenue = stock.current_price * quantity
            
            # 更新账户余额
            account = session.query(Account).filter_by(user_id=user_id, currency_code='JCC').first()
            account.balance += total_revenue
            
            # 更新投资组合
            portfolio.quantity -= quantity
            if portfolio.quantity == 0:
                session.delete(portfolio)
            
            session.commit()
            
            # 发布事件
            self.event_bus.publish('stock_sold', {
                'user_id': user_id,
                'ticker': ticker,
                'quantity': quantity,
                'price': float(stock.current_price),
                'total_revenue': float(total_revenue)
            })
            
            return {
                'success': True,
                'message': f'成功卖出 {quantity} 股 {ticker}，获得 {total_revenue} JCC'
            }
    
    def get_user_portfolio(self, user_id: int) -> List[Dict[str, Any]]:
        """获取用户投资组合"""
        with get_session() as session:
            portfolios = session.query(Portfolio).filter_by(user_id=user_id).all()
            
            result = []
            for portfolio in portfolios:
                stock = session.query(Stock).filter_by(id=portfolio.stock_id).first()
                if stock:
                    current_value = stock.current_price * portfolio.quantity
                    cost_value = portfolio.average_cost * portfolio.quantity
                    profit_loss = current_value - cost_value
                    profit_loss_pct = (profit_loss / cost_value) * 100 if cost_value > 0 else 0
                    
                    result.append({
                        'ticker': stock.ticker,
                        'name': stock.name,
                        'quantity': portfolio.quantity,
                        'average_cost': float(portfolio.average_cost),
                        'current_price': float(stock.current_price),
                        'current_value': float(current_value),
                        'cost_value': float(cost_value),
                        'profit_loss': float(profit_loss),
                        'profit_loss_pct': float(profit_loss_pct)
                    })
            
            return result
    
    def get_market_summary(self) -> Dict[str, Any]:
        """获取市场概况"""
        with get_session() as session:
            stocks = session.query(Stock).all()
            
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
                'avg_price_change': avg_price_change
            }