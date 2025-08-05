"""
豪车投资系统
"""

import random
from datetime import datetime
from home.base_asset import BaseAsset


class LuxuryCar(BaseAsset):
    """豪车资产类"""
    
    def __init__(self, car_id, name, brand, model, price, year, rarity="rare"):
        super().__init__(
            car_id, 
            name, 
            f"{brand} {model} ({year}年)", 
            price, 
            "豪车收藏", 
            rarity, 
            "🚗"
        )
        self.brand = brand
        self.model = model
        self.year = year
        self.mileage = random.randint(1000, 50000)  # 里程数
        self.condition = random.choice(['mint', 'excellent', 'good', 'fair'])  # 车况
    
    def update_price(self):
        """更新豪车价格"""
        # 豪车价格受多种因素影响
        base_change = random.gauss(0, self.volatility)
        
        # 年份因素：老爷车可能升值
        age = datetime.now().year - self.year
        if age > 30:  # 老爷车
            base_change += 0.02
        elif age > 20:  # 经典车
            base_change += 0.01
        elif age > 10:  # 二手车
            base_change -= 0.01
        else:  # 新车
            base_change -= 0.02
        
        # 稀有度影响
        rarity_bonus = self.get_rarity_info()['multiplier'] * 0.01
        base_change += rarity_bonus * random.uniform(-1, 1)
        
        # 车况影响
        condition_multiplier = {
            'mint': 1.2,
            'excellent': 1.1,
            'good': 1.0,
            'fair': 0.9
        }
        base_change *= condition_multiplier[self.condition]
        
        # 市场热度随机事件
        if random.random() < 0.05:  # 5%几率市场热点
            market_events = [
                ("经典车拍卖会推高市场", 0.15),
                ("新车型发布影响", -0.08),
                ("收藏家大量购入", 0.12),
                ("经济环境影响", -0.10),
                ("赛车传奇故事曝光", 0.20)
            ]
            event, impact = random.choice(market_events)
            base_change += impact
            self.last_market_event = event
        
        # 更新价格
        new_price = self.current_price * (1 + base_change)
        new_price = max(new_price, self.current_price * 0.7)  # 最大跌幅30%
        
        self.current_price = round(new_price, 2)
        self.price_history.append(self.current_price)
        
        # 保留最近100个价格记录
        if len(self.price_history) > 100:
            self.price_history = self.price_history[-100:]
        
        self.last_update = datetime.now().isoformat()
    
    def get_detailed_info(self):
        """获取详细信息"""
        rarity_info = self.get_rarity_info()
        trend = self.get_price_trend()
        
        condition_desc = {
            'mint': '完美车况',
            'excellent': '优秀车况', 
            'good': '良好车况',
            'fair': '一般车况'
        }
        
        return f"""
🚗 {self.name} {rarity_info['color']}

📋 基本信息:
  品牌: {self.brand}
  型号: {self.model}
  年份: {self.year}年
  里程: {self.mileage:,} 公里
  车况: {condition_desc[self.condition]}
  稀有度: {rarity_info['name']}

💰 投资信息:
  当前估值: ${self.current_price:,.2f}
  价格趋势: {trend}
  持有数量: {self.quantity}辆
  总价值: ${self.get_value():,.2f}
  
📈 投资表现:
  购入价格: ${self.purchase_price:,.2f}
  盈亏金额: ${self.get_profit_loss():+,.2f}
  盈亏比例: {self.get_profit_percentage():+.1f}%

🎯 投资建议:
  {self._get_investment_advice()}
"""
    
    def _get_investment_advice(self):
        """获取投资建议"""
        age = datetime.now().year - self.year
        profit_pct = self.get_profit_percentage()
        
        if age > 30 and self.condition in ['mint', 'excellent']:
            return "🌟 经典老爷车，长期持有价值高"
        elif profit_pct > 20:
            return "💰 收益丰厚，可考虑获利了结"
        elif profit_pct < -15:
            return "⚠️ 亏损较大，建议谨慎评估"
        elif self.rarity == 'legendary':
            return "🏆 传奇车型，建议长期收藏"
        else:
            return "📊 表现正常，可继续持有观察"


def create_luxury_cars():
    """创建豪车数据"""
    cars = [
        # 传奇级
        LuxuryCar("ferrari_250gto", "法拉利250 GTO", "Ferrari", "250 GTO", 48000000, 1962, "legendary"),
        LuxuryCar("mclaren_f1", "迈凯伦F1", "McLaren", "F1", 15000000, 1993, "legendary"),
        LuxuryCar("porsche_917k", "保时捷917K", "Porsche", "917K", 12000000, 1970, "legendary"),
        
        # 史诗级
        LuxuryCar("lamborghini_miura", "兰博基尼Miura", "Lamborghini", "Miura", 2500000, 1968, "epic"),
        LuxuryCar("ferrari_f40", "法拉利F40", "Ferrari", "F40", 1800000, 1987, "epic"),
        LuxuryCar("porsche_911gt1", "保时捷911 GT1", "Porsche", "911 GT1", 3200000, 1997, "epic"),
        LuxuryCar("aston_db5", "阿斯顿·马丁DB5", "Aston Martin", "DB5", 1500000, 1963, "epic"),
        
        # 稀有级
        LuxuryCar("ferrari_testarossa", "法拉利Testarossa", "Ferrari", "Testarossa", 280000, 1984, "rare"),
        LuxuryCar("lamborghini_countach", "兰博基尼Countach", "Lamborghini", "Countach", 450000, 1974, "rare"),
        LuxuryCar("porsche_930turbo", "保时捷930 Turbo", "Porsche", "930 Turbo", 180000, 1975, "rare"),
        LuxuryCar("bmw_m1", "宝马M1", "BMW", "M1", 650000, 1978, "rare"),
        LuxuryCar("mercedes_300sl", "奔驰300SL", "Mercedes-Benz", "300SL", 1200000, 1954, "rare"),
        
        # 普通级（现代豪车）
        LuxuryCar("ferrari_488", "法拉利488 GTB", "Ferrari", "488 GTB", 280000, 2015, "common"),
        LuxuryCar("lamborghini_huracan", "兰博基尼Huracan", "Lamborghini", "Huracan", 260000, 2014, "common"),
        LuxuryCar("porsche_911gt3", "保时捷911 GT3", "Porsche", "911 GT3", 180000, 2017, "common"),
        LuxuryCar("mclaren_720s", "迈凯伦720S", "McLaren", "720S", 300000, 2017, "common"),
        LuxuryCar("aston_vantage", "阿斯顿·马丁Vantage", "Aston Martin", "Vantage", 160000, 2018, "common"),
    ]
    
    return {car.asset_id: car for car in cars} 