# DEMONSTRATION CODE FOR STOCK SIMULATOR
# This code simulates the behavior of a stock based on various factors such as market sentiment, industry trends,
# company news, macro economy, and technical analysis.
# The simulation is based on random numbers and is not intended to be used for any financial or investment decisions.
# The code is provided as-is and without any warranty or liability.


import datetime
import random
import math

class AdvancedStock:
    def __init__(self, code, name, initial_price, initial_issued_shares, historical_data, fundamental_factors):
        self.code = code
        self.name = name
        self.initial_price = initial_price
        self.current_price = initial_price
        self.initial_issued_shares = initial_issued_shares
        self.purchasable_shares = initial_issued_shares
        self.trading_volume = 0
        self.price_history = [(datetime.datetime.now(), initial_price)]
        self.historical_data = historical_data
        self.fundamental_factors = fundamental_factors

    def calculate_earnings(self):
        # 基于公司的盈利、营收等基本面因素计算盈利
        earnings = random.randint(0, 1000000)  # 示例随机盈利
        return earnings

    def calculate_dividend(self):
        # 根据盈利和公司政策计算股息
        earnings = self.calculate_earnings()
        dividend_ratio = random.uniform(0, 0.5)  # 示例股息比例
        dividend = earnings * dividend_ratio
        return dividend

    def update_price_based_on_market_sentiment(self, market_sentiment):
        # 根据市场情绪调整价格
        sentiment_factor = random.uniform(-0.2, 0.2)  # 示例情绪因子
        if market_sentiment == "bullish":
            sentiment_factor += 0.1
        elif market_sentiment == "bearish":
            sentiment_factor -= 0.1

        price_change = self.current_price * sentiment_factor
        self.current_price += price_change

    def update_price_based_on_industry_trends(self, industry_trend):
        # 根据行业趋势调整价格
        trend_factor = random.uniform(-0.15, 0.15)  # 示例趋势因子
        if industry_trend == "growing":
            trend_factor += 0.08
        elif industry_trend == "declining":
            trend_factor -= 0.08

        price_change = self.current_price * trend_factor
        self.current_price += price_change

    def update_price_based_on_company_news(self, news_type):
        # 根据公司特定新闻调整价格
        news_factor = random.uniform(-0.1, 0.1)  # 示例新闻因子
        if news_type == "positive":
            news_factor += 0.05
        elif news_type == "negative":
            news_factor -= 0.05

        price_change = self.current_price * news_factor
        self.current_price += price_change

    def update_price_based_on_macro_economy(self, economic_indicator):
        # 根据宏观经济指标调整价格
        economic_factor = random.uniform(-0.12, 0.12)  # 示例经济因子
        if economic_indicator > 0:  # 假设经济指标增长为正
            economic_factor += 0.06
        elif economic_indicator < 0:  # 假设经济指标下降为负
            economic_factor -= 0.06

        price_change = self.current_price * economic_factor
        self.current_price += price_change

    def update_price_based_on_technical_analysis(self):
        # 基于技术分析指标（如移动平均线、RSI 等）调整价格
        ma_20 = sum([price for _, price in self.price_history[-20:]]) / 20
        ma_50 = sum([price for _, price in self.price_history[-50:]]) / 50

        if self.current_price > ma_20 and ma_20 > ma_50:
            # 上升趋势，价格可能上涨
            price_change = self.current_price * random.uniform(0.02, 0.05)
        elif self.current_price < ma_20 and ma_20 < ma_50:
            # 下降趋势，价格可能下跌
            price_change = -self.current_price * random.uniform(0.02, 0.05)
        else:
            # 震荡趋势，价格随机波动
            price_change = self.current_price * random.uniform(-0.02, 0.02)

        self.current_price += price_change

    def update_price(self):
        # 综合考虑各种因素更新价格
        market_sentiment = random.choice(["bullish", "bearish", "neutral"])
        industry_trend = random.choice(["growing", "declining", "stable"])
        news_type = random.choice(["positive", "negative", "neutral"])
        economic_indicator = random.randint(-10, 10)  # 示例经济指标

        self.update_price_based_on_market_sentiment(market_sentiment)
        self.update_price_based_on_industry_trends(industry_trend)
        self.update_price_based_on_company_news(news_type)
        self.update_price_based_on_macro_economy(economic_indicator)
        self.update_price_based_on_technical_analysis()

        timestamp = datetime.datetime.now()
        self.price_history.append((timestamp, self.current_price))