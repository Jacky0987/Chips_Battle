"""
JC股票价格更新系统
提供更智能的价格更新机制，支持与分析工具的集成
"""

import random
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class JCStockUpdater:
    """JC股票价格更新器"""
    
    def __init__(self, company_manager, market_data_manager):
        self.company_manager = company_manager
        self.market_data_manager = market_data_manager
        self.update_thread = None
        self.is_running = False
        self.update_interval = 30  # 30秒更新一次
        
        # 价格历史缓存 - 用于技术分析
        self.price_history_cache = {}  # {symbol: [price_data]}
        self.technical_indicators = {}  # {symbol: indicators}
        
    def start_price_updates(self):
        """启动价格更新线程"""
        if self.is_running:
            return
        
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        print("JC股票价格更新系统已启动")
    
    def stop_price_updates(self):
        """停止价格更新"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)
        print("JC股票价格更新系统已停止")
    
    def _update_loop(self):
        """价格更新循环"""
        while self.is_running:
            try:
                self._update_all_jc_stocks()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"JC股价格更新出错: {e}")
                time.sleep(10)  # 错误时等待更长时间
    
    def _update_all_jc_stocks(self):
        """更新所有JC上市公司股价"""
        updated_count = 0
        
        for company in self.company_manager.companies.values():
            if company.is_public and company.symbol:
                try:
                    self._update_single_stock(company)
                    updated_count += 1
                except Exception as e:
                    print(f"更新股票 {company.symbol} 失败: {e}")
                    continue
        
        if updated_count > 0:
            # 更新完成后保存数据
            self.company_manager.save_companies()
            if hasattr(self.market_data_manager, 'save_stocks'):
                self.market_data_manager.save_stocks()
    
    def _update_single_stock(self, company):
        """更新单只JC股票"""
        symbol = company.symbol
        
        # 计算新价格
        new_price = self._calculate_new_price(company)
        
        # 更新公司数据
        old_price = company.stock_price
        company.update_stock_price(new_price)
        
        # 更新市场数据
        self._sync_to_market_data(company, old_price)
        
        # 更新价格历史缓存
        self._update_price_cache(symbol, new_price, old_price)
        
        # 更新技术指标
        self._update_technical_indicators(symbol)
    
    def _calculate_new_price(self, company) -> float:
        """计算新股价"""
        old_price = company.stock_price
        
        # 基础波动率（根据公司风险等级调整）
        base_volatility = 0.02 + (company.risk_level - 1) * 0.005
        
        # 公司基本面影响
        fundamentals_factor = self._calculate_fundamentals_factor(company)
        
        # 市场情绪影响
        sentiment_factor = self._calculate_sentiment_factor(company)
        
        # 新闻事件影响
        news_factor = self._calculate_news_factor(company)
        
        # 技术面影响（支撑阻力）
        technical_factor = self._calculate_technical_factor(company)
        
        # 随机波动
        random_factor = random.uniform(-base_volatility, base_volatility)
        
        # 综合计算价格变化
        total_factor = (
            fundamentals_factor * 0.3 +
            sentiment_factor * 0.2 +
            news_factor * 0.25 +
            technical_factor * 0.15 +
            random_factor * 0.1
        )
        
        # 限制单次变化幅度
        total_factor = max(-0.15, min(0.15, total_factor))
        
        new_price = old_price * (1 + total_factor)
        return max(0.01, round(new_price, 2))
    
    def _calculate_fundamentals_factor(self, company) -> float:
        """计算基本面影响因子"""
        # 盈利能力
        profit_factor = 0.0
        if company.metrics.profit > 0:
            roe = company.metrics.calculate_roe()
            profit_factor = min(roe * 0.1, 0.05)  # ROE影响，最多5%
        else:
            profit_factor = -0.02  # 亏损负面影响
        
        # 成长性
        growth_factor = company.metrics.growth_rate * 0.1
        
        # 财务健康度
        health_factor = 0.0
        if company.metrics.debt_ratio < 0.3:
            health_factor = 0.01
        elif company.metrics.debt_ratio > 0.7:
            health_factor = -0.02
        
        return profit_factor + growth_factor + health_factor
    
    def _calculate_sentiment_factor(self, company) -> float:
        """计算市场情绪影响因子"""
        # 基于公司表现评分
        performance_score = company.performance_score
        
        if performance_score > 80:
            return random.uniform(0.01, 0.03)
        elif performance_score < 40:
            return random.uniform(-0.03, -0.01)
        else:
            return random.uniform(-0.01, 0.01)
    
    def _calculate_news_factor(self, company) -> float:
        """计算新闻事件影响因子"""
        news_factor = 0.0
        
        # 最近24小时的新闻
        recent_news = [
            news for news in company.news_events
            if (datetime.now() - datetime.fromisoformat(news.publish_date)).days <= 1
        ]
        
        for news in recent_news:
            if news.impact_type == 'positive':
                news_factor += news.impact_magnitude
            elif news.impact_type == 'negative':
                news_factor -= news.impact_magnitude
        
        return max(-0.1, min(0.1, news_factor))
    
    def _calculate_technical_factor(self, company) -> float:
        """计算技术面影响因子"""
        symbol = company.symbol
        
        if symbol not in self.price_history_cache:
            return 0.0
        
        history = self.price_history_cache[symbol]
        if len(history) < 5:
            return 0.0
        
        current_price = company.stock_price
        
        # 计算简单移动平均线
        ma5 = sum(h['price'] for h in history[-5:]) / 5
        
        # 价格相对位置
        if current_price > ma5 * 1.05:
            return random.uniform(-0.02, -0.01)  # 超买，回调压力
        elif current_price < ma5 * 0.95:
            return random.uniform(0.01, 0.02)   # 超卖，反弹动力
        
        return 0.0
    
    def _sync_to_market_data(self, company, old_price: float):
        """同步到市场数据系统"""
        if not hasattr(self.market_data_manager, 'stocks'):
            return
        
        symbol = company.symbol
        
        # 创建或更新股票数据
        if symbol not in self.market_data_manager.stocks:
            self._create_market_data_entry(company)
        
        stock_data = self.market_data_manager.stocks[symbol]
        
        # 更新价格相关数据
        stock_data['price'] = company.stock_price
        stock_data['change'] = company.stock_price - old_price
        stock_data['market_cap'] = company.market_cap
        stock_data['last_updated'] = datetime.now().isoformat()
        
        # 更新价格历史
        if 'price_history' not in stock_data:
            stock_data['price_history'] = []
        stock_data['price_history'].append(company.stock_price)
        if len(stock_data['price_history']) > 100:
            stock_data['price_history'] = stock_data['price_history'][-100:]
        
        # 更新财务指标
        if company.metrics.profit > 0 and company.shares_outstanding > 0:
            eps = company.metrics.profit / company.shares_outstanding
            stock_data['eps'] = eps
            stock_data['pe_ratio'] = round(company.stock_price / eps, 2)
        
        # 模拟成交量
        volume_base = random.randint(50000, 500000)
        price_change_pct = abs(stock_data['change'] / old_price) if old_price > 0 else 0
        volume_multiplier = 1 + price_change_pct * 10  # 价格变化越大，成交量越大
        stock_data['volume'] = int(volume_base * volume_multiplier)
    
    def _create_market_data_entry(self, company):
        """为JC公司创建市场数据条目"""
        stock_data = {
            'name': company.name,
            'price': company.stock_price,
            'change': 0.0,
            'sector': company.industry.value.title(),
            'volatility': 0.02 + company.risk_level * 0.005,
            'market_cap': company.market_cap,
            'pe_ratio': company.calculate_pe_ratio(),
            'volume': random.randint(100000, 1000000),
            'beta': random.uniform(0.8, 1.5),
            'dividend_yield': random.uniform(0.0, 0.03),
            'price_history': [company.stock_price],
            'eps': company.metrics.profit / company.shares_outstanding if company.shares_outstanding > 0 else 0,
            'last_updated': datetime.now().isoformat(),
            'company_id': company.company_id,
            'is_jc_company': True
        }
        
        self.market_data_manager.stocks[company.symbol] = stock_data
    
    def _update_price_cache(self, symbol: str, new_price: float, old_price: float):
        """更新价格历史缓存"""
        if symbol not in self.price_history_cache:
            self.price_history_cache[symbol] = []
        
        price_data = {
            'timestamp': datetime.now().isoformat(),
            'price': new_price,
            'change': new_price - old_price,
            'volume': random.randint(10000, 100000)
        }
        
        self.price_history_cache[symbol].append(price_data)
        
        # 保持最近1000个数据点
        if len(self.price_history_cache[symbol]) > 1000:
            self.price_history_cache[symbol] = self.price_history_cache[symbol][-1000:]
    
    def _update_technical_indicators(self, symbol: str):
        """更新技术指标"""
        if symbol not in self.price_history_cache:
            return
        
        history = self.price_history_cache[symbol]
        if len(history) < 20:
            return
        
        prices = [h['price'] for h in history]
        
        # 计算技术指标
        indicators = {}
        
        # 移动平均线
        if len(prices) >= 5:
            indicators['ma5'] = sum(prices[-5:]) / 5
        if len(prices) >= 10:
            indicators['ma10'] = sum(prices[-10:]) / 10
        if len(prices) >= 20:
            indicators['ma20'] = sum(prices[-20:]) / 20
        
        # RSI (简化版)
        if len(prices) >= 14:
            gains = []
            losses = []
            for i in range(1, 15):
                change = prices[-i] - prices[-i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            avg_gain = sum(gains) / 14
            avg_loss = sum(losses) / 14
            
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                indicators['rsi'] = 100 - (100 / (1 + rs))
            else:
                indicators['rsi'] = 100
        
        self.technical_indicators[symbol] = indicators
    
    def get_stock_analysis_data(self, symbol: str) -> Optional[Dict]:
        """获取股票分析数据（供分析工具使用）"""
        company = self.company_manager.get_company_by_symbol(symbol)
        if not company:
            return None
        
        # 基础数据
        analysis_data = {
            'symbol': symbol,
            'name': company.name,
            'current_price': company.stock_price,
            'market_cap': company.market_cap,
            'industry': company.industry.value,
            'company_type': company.company_type.value,
            'stage': company.stage.value,
            'is_jc_company': True,
            'company': company  # 添加公司对象引用
        }
        
        # 财务数据
        analysis_data['financials'] = {
            'revenue': company.metrics.revenue,
            'profit': company.metrics.profit,
            'assets': company.metrics.assets,
            'equity': company.metrics.calculate_equity(),
            'roe': company.metrics.calculate_roe(),
            'roa': company.metrics.calculate_roa(),
            'debt_ratio': company.metrics.debt_ratio,
            'growth_rate': company.metrics.growth_rate,
            'employees': company.metrics.employees,
            'pe_ratio': company.calculate_pe_ratio(),
            'pb_ratio': company.calculate_pb_ratio()
        }
        
        # 估值数据
        analysis_data['valuation'] = {
            'pe_ratio': company.calculate_pe_ratio(),
            'pb_ratio': company.calculate_pb_ratio(),
            'eps': company.metrics.profit / company.shares_outstanding if company.shares_outstanding > 0 else 0,
            'book_value_per_share': company.metrics.calculate_equity() / company.shares_outstanding if company.shares_outstanding > 0 else 0
        }
        
        # 🔧 修复：添加价格历史数据
        if symbol in self.price_cache:
            analysis_data['price_history'] = self.price_cache[symbol][-90:]  # 最近90天数据
        else:
            # 如果没有缓存数据，生成模拟历史数据
            current_price = company.stock_price
            price_history = []
            for i in range(30):  # 生成30天历史数据
                base_price = current_price * (0.95 + 0.1 * (i / 30))  # 模拟价格变化
                volatility = random.uniform(-0.05, 0.05)
                price = base_price * (1 + volatility)
                price_history.append(round(price, 2))
            
            price_history.append(current_price)  # 添加当前价格
            analysis_data['price_history'] = price_history
        
        # 技术指标数据
        if symbol in self.technical_indicators:
            analysis_data['technical_indicators'] = self.technical_indicators[symbol].copy()
        else:
            # 生成基础技术指标
            prices = analysis_data['price_history']
            analysis_data['technical_indicators'] = {
                'ma5': sum(prices[-5:]) / 5 if len(prices) >= 5 else company.stock_price,
                'ma20': sum(prices[-20:]) / 20 if len(prices) >= 20 else company.stock_price,
                'ma60': sum(prices[-60:]) / 60 if len(prices) >= 60 else company.stock_price,
                'rsi': random.uniform(30, 70),  # 模拟RSI
                'macd': random.uniform(-0.5, 0.5),  # 模拟MACD
                'bollinger_upper': company.stock_price * 1.05,
                'bollinger_lower': company.stock_price * 0.95,
                'avg_volume': random.randint(100000, 1000000),
                'volume_ratio': random.uniform(0.8, 1.5)
            }
        
        # 市场情绪数据
        analysis_data['sentiment'] = {
            'overall_score': company.performance_score,
            'news_impact': 'positive' if company.performance_score > 70 else 'negative' if company.performance_score < 40 else 'neutral',
            'social_sentiment': 'positive' if company.performance_score > 60 else 'negative' if company.performance_score < 50 else 'neutral',
            'institutional_view': 'bullish' if company.performance_score > 75 else 'bearish' if company.performance_score < 35 else 'neutral'
        }
        
        # 价格历史
        if symbol in self.price_history_cache:
            history = self.price_history_cache[symbol][-60:]  # 最近60个数据点
            analysis_data['price_history'] = [
                {
                    'timestamp': h['timestamp'],
                    'price': h['price'],
                    'volume': h.get('volume', 0)
                } for h in history
            ]
        
        # 技术指标
        if symbol in self.technical_indicators:
            analysis_data['technical_indicators'] = self.technical_indicators[symbol]
        
        # 新闻数据
        recent_news = company.news_events[-10:] if company.news_events else []
        analysis_data['recent_news'] = [
            {
                'title': news.title,
                'impact_type': news.impact_type,
                'impact_magnitude': news.impact_magnitude,
                'publish_date': news.publish_date,
                'category': news.category
            } for news in recent_news
        ]
        
        # 投资评级
        rating, grade = company.get_investment_rating()
        analysis_data['investment_rating'] = {
            'rating': rating,
            'grade': grade,
            'performance_score': company.performance_score,
            'risk_level': company.risk_level
        }
        
        return analysis_data
    
    def get_available_jc_stocks(self) -> List[str]:
        """获取可用的JC股票代码列表"""
        return [
            company.symbol for company in self.company_manager.companies.values()
            if company.is_public and company.symbol
        ]
    
    def force_news_event(self, symbol: str, event_type: str = None) -> bool:
        """强制触发新闻事件（用于测试）"""
        company = self.company_manager.get_company_by_symbol(symbol)
        if not company:
            return False
        
        news = company.generate_news_event(event_type)
        if news:
            self.company_manager.save_companies()
            return True
        return False 