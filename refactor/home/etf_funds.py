"""
ETF基金投资系统
"""

import random
from datetime import datetime
from home.base_asset import BaseAsset


class ETFFund(BaseAsset):
    """ETF基金资产类"""
    
    def __init__(self, etf_id, name, description, nav, expense_ratio, sector, rarity="common"):
        super().__init__(
            etf_id,
            name,
            description,
            nav,
            "ETF基金",
            rarity,
            "📊"
        )
        self.nav = nav  # 净值
        self.expense_ratio = expense_ratio  # 费用率
        self.sector = sector  # 行业
        self.dividend_yield = random.uniform(0.01, 0.06)  # 分红收益率
        self.volume = random.randint(1000000, 50000000)  # 交易量
        
    def update_price(self):
        """更新ETF价格"""
        # ETF价格相对稳定，但受市场和行业影响
        base_change = random.gauss(0, self.volatility)
        
        # 行业因素
        sector_performance = self._get_sector_performance()
        base_change += sector_performance
        
        # 市场大盘影响
        market_sentiment = random.uniform(-0.02, 0.02)
        base_change += market_sentiment
        
        # 分红影响（每季度）
        if random.random() < 0.01:  # 1%几率分红
            dividend = self.current_price * self.dividend_yield * 0.25  # 季度分红
            self.last_dividend = dividend
        
        # 费用扣除
        base_change -= self.expense_ratio / 252  # 日费用
        
        # 更新价格
        new_price = self.current_price * (1 + base_change)
        new_price = max(new_price, self.current_price * 0.8)  # 最大跌幅20%
        
        self.current_price = round(new_price, 2)
        self.nav = self.current_price  # 更新净值
        self.price_history.append(self.current_price)
        
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]
        
        self.last_update = datetime.now().isoformat()
    
    def _get_sector_performance(self):
        """获取行业表现"""
        sector_trends = {
            "Technology": random.uniform(-0.03, 0.04),
            "Healthcare": random.uniform(-0.02, 0.03),
            "Finance": random.uniform(-0.025, 0.025),
            "Energy": random.uniform(-0.04, 0.05),
            "Consumer": random.uniform(-0.02, 0.03),
            "Real Estate": random.uniform(-0.03, 0.03),
            "Utilities": random.uniform(-0.015, 0.02),
            "Materials": random.uniform(-0.03, 0.04),
            "International": random.uniform(-0.025, 0.03),
            "Emerging Markets": random.uniform(-0.05, 0.06)
        }
        return sector_trends.get(self.sector, 0)
    
    def get_detailed_info(self):
        """获取详细信息"""
        rarity_info = self.get_rarity_info()
        trend = self.get_price_trend()
        
        return f"""
📊 {self.name} {rarity_info['color']}

📋 基金信息:
  基金类型: ETF基金
  投资行业: {self.sector}
  净值(NAV): ${self.nav:.2f}
  费用率: {self.expense_ratio*100:.2f}%
  分红收益率: {self.dividend_yield*100:.1f}%
  交易量: {self.volume:,}

💰 投资信息:
  当前价格: ${self.current_price:.2f}
  价格趋势: {trend}
  持有份额: {self.quantity:,.0f}份
  总价值: ${self.get_value():,.2f}
  
📈 投资表现:
  购入价格: ${self.purchase_price:.2f}
  盈亏金额: ${self.get_profit_loss():+,.2f}
  盈亏比例: {self.get_profit_percentage():+.1f}%
  年化费用: ${self.get_value() * self.expense_ratio:,.2f}

🎯 投资特点:
  {self._get_investment_features()}
"""
    
    def _get_investment_features(self):
        """获取投资特点"""
        features = []
        
        if self.expense_ratio < 0.005:
            features.append("💡 超低费用率")
        elif self.expense_ratio < 0.01:
            features.append("✅ 低费用率") 
        else:
            features.append("⚠️ 较高费用率")
            
        if self.dividend_yield > 0.04:
            features.append("💰 高分红收益")
        elif self.dividend_yield > 0.02:
            features.append("💵 中等分红")
        else:
            features.append("📈 成长导向")
            
        if self.sector in ["Technology", "Energy", "Emerging Markets"]:
            features.append("⚡ 高成长潜力")
        elif self.sector in ["Utilities", "Consumer"]:
            features.append("🛡️ 防御型配置")
        else:
            features.append("⚖️ 均衡配置")
            
        return " | ".join(features)


def create_etf_funds():
    """创建ETF基金数据"""
    etfs = [
        # 传奇级（顶级宽基ETF）
        ETFFund("spy", "SPDR S&P 500 ETF", "追踪标普500指数的经典ETF", 420.5, 0.0009, "US Market", "legendary"),
        ETFFund("vti", "Vanguard全市场ETF", "涵盖美国全市场的旗舰ETF", 230.2, 0.0003, "US Market", "legendary"),
        
        # 史诗级（知名行业ETF）
        ETFFund("qqq", "纳斯达克100 ETF", "追踪纳斯达克100科技巨头", 380.7, 0.0020, "Technology", "epic"),
        ETFFund("arkk", "ARK创新ETF", "专注颠覆性创新技术投资", 45.8, 0.0075, "Technology", "epic"),
        ETFFund("xlf", "金融行业SPDR ETF", "美国金融行业龙头基金", 38.9, 0.0012, "Finance", "epic"),
        ETFFund("xle", "能源行业SPDR ETF", "美国能源行业投资基金", 89.2, 0.0012, "Energy", "epic"),
        
        # 稀有级（特色主题ETF）
        ETFFund("vym", "Vanguard高分红ETF", "专注高分红股票投资", 105.3, 0.0006, "Dividend", "rare"),
        ETFFund("iefa", "iShares核心MSCI EAFE ETF", "发达市场国际投资", 72.4, 0.0007, "International", "rare"),
        ETFFund("eem", "iShares新兴市场ETF", "新兴市场股票投资", 50.6, 0.0068, "Emerging Markets", "rare"),
        ETFFund("gld", "SPDR黄金ETF", "实物黄金支持的ETF", 185.7, 0.0040, "Commodities", "rare"),
        ETFFund("reit", "Vanguard房地产ETF", "房地产投资信托基金", 98.4, 0.0012, "Real Estate", "rare"),
        
        # 普通级（常见配置ETF）
        ETFFund("ivv", "iShares核心S&P500 ETF", "标普500指数基金", 420.1, 0.0003, "US Market", "common"),
        ETFFund("vxus", "Vanguard全球股票ETF", "美国以外全球市场", 58.9, 0.0008, "International", "common"),
        ETFFund("bnd", "Vanguard债券市场ETF", "美国债券市场基金", 80.2, 0.0003, "Bonds", "common"),
        ETFFund("vteb", "Vanguard免税债券ETF", "免税市政债券基金", 54.7, 0.0005, "Municipal Bonds", "common"),
        ETFFund("xlk", "科技行业SPDR ETF", "美国科技股基金", 165.3, 0.0012, "Technology", "common"),
        ETFFund("xlv", "医疗保健SPDR ETF", "美国医疗健康基金", 134.8, 0.0012, "Healthcare", "common"),
        ETFFund("xlu", "公用事业SPDR ETF", "美国公用事业基金", 70.5, 0.0012, "Utilities", "common"),
    ]
    
    return {etf.asset_id: etf for etf in etfs} 