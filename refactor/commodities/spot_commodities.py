"""
现货商品交易模块
实现现货商品的即期交易功能
"""

from datetime import datetime, time
import random
from .base_commodity import BaseCommodity


class SpotCommodity(BaseCommodity):
    """现货商品类"""
    
    def __init__(self, symbol, name, current_price, unit, storage_cost=0.02, 
                 quality_grade="标准级", origin="国际", currency="USD", 
                 volatility=0.03, tick_size=0.01):
        super().__init__(symbol, name, current_price, currency, 
                        volatility, tick_size, 1)  # 现货通常按实际重量/数量交易
        
        self.unit = unit  # 交易单位 (盎司、吨、桶等)
        self.storage_cost = storage_cost  # 年存储成本比例
        self.quality_grade = quality_grade
        self.origin = origin
        
        # 现货特有属性
        self.delivery_locations = self._get_delivery_locations()
        self.quality_specifications = self._get_quality_specs()
        self.spot_premium = random.uniform(-0.05, 0.05)  # 现货升贴水
        
        # 供需信息
        self.inventory_level = random.uniform(0.3, 0.9)  # 库存水平
        self.production_rate = random.uniform(0.8, 1.2)  # 生产比率
        self.consumption_rate = random.uniform(0.9, 1.1)  # 消费比率
        
    def update_price(self):
        """更新现货价格"""
        # 现货价格受供需关系影响更直接
        supply_demand_factor = self._calculate_supply_demand_factor()
        
        # 临时调整波动率
        original_volatility = self.volatility
        self.volatility *= supply_demand_factor
        
        # 模拟价格变动
        new_price = self._simulate_price_movement()
        
        # 现货价格通常有存储成本影响
        storage_impact = self._calculate_storage_impact()
        new_price *= (1 + storage_impact)
        
        # 恢复原始波动率
        self.volatility = original_volatility
        
        return new_price
    
    def get_trading_hours(self):
        """获取现货交易时间"""
        return {
            'extended_hours': True,
            'description': '24小时交易，但主要活跃时间为当地商业时间'
        }
    
    def calculate_margin_required(self, quantity, leverage=1):
        """计算现货保证金需求（通常需要全额支付）"""
        total_value = abs(quantity) * self.current_price
        # 现货交易通常要求100%保证金，但允许一定杠杆
        margin = total_value / max(leverage, 1)
        return margin
    
    def calculate_storage_cost(self, quantity, days):
        """计算存储费用"""
        total_value = quantity * self.current_price
        daily_storage_rate = self.storage_cost / 365
        return total_value * daily_storage_rate * days
    
    def get_delivery_info(self, quantity):
        """获取交割信息"""
        total_value = quantity * self.current_price
        delivery_fee = max(total_value * 0.001, 50)  # 最低$50交割费
        
        return {
            'quantity': quantity,
            'unit': self.unit,
            'total_value': total_value,
            'delivery_fee': delivery_fee,
            'delivery_locations': self.delivery_locations,
            'quality_grade': self.quality_grade,
            'origin': self.origin,
            'estimated_delivery_days': self._get_delivery_time()
        }
    
    def get_supply_demand_analysis(self):
        """获取供需分析"""
        balance = self.production_rate - self.consumption_rate
        
        if balance > 0.1:
            market_condition = "供过于求"
            price_outlook = "下跌压力"
        elif balance < -0.1:
            market_condition = "供不应求"
            price_outlook = "上涨动力"
        else:
            market_condition = "供需平衡"
            price_outlook = "价格稳定"
        
        inventory_status = self._get_inventory_status()
        
        return {
            'market_condition': market_condition,
            'price_outlook': price_outlook,
            'inventory_status': inventory_status,
            'inventory_level': f"{self.inventory_level*100:.1f}%",
            'production_rate': f"{self.production_rate*100:.1f}%",
            'consumption_rate': f"{self.consumption_rate*100:.1f}%",
            'supply_demand_balance': f"{balance:+.2f}"
        }
    
    def _calculate_supply_demand_factor(self):
        """计算供需影响因子"""
        # 库存水平影响
        inventory_factor = 1.0
        if self.inventory_level < 0.3:
            inventory_factor = 1.3  # 低库存推高价格波动
        elif self.inventory_level > 0.8:
            inventory_factor = 0.8  # 高库存降低价格波动
        
        # 供需平衡影响
        balance = self.production_rate - self.consumption_rate
        if abs(balance) > 0.1:
            inventory_factor *= 1.2  # 供需失衡增加波动
        
        return inventory_factor
    
    def _calculate_storage_impact(self):
        """计算存储成本对价格的影响"""
        daily_storage = self.storage_cost / 365
        # 存储成本会轻微推高现货价格
        return daily_storage * random.uniform(0.5, 1.5)
    
    def _get_delivery_locations(self):
        """获取交割地点"""
        if self.symbol.startswith('XAU') or self.symbol.startswith('XAG'):
            return ['伦敦', '纽约', '苏黎世', '香港']
        elif 'OIL' in self.symbol or 'CL' in self.symbol:
            return ['库欣', '新加坡', '鹿特丹', '富查伊拉']
        elif 'CU' in self.symbol or 'AL' in self.symbol:
            return ['上海', '伦敦', '纽约', '新加坡']
        else:
            return ['芝加哥', '堪萨斯城', '明尼阿波利斯']
    
    def _get_quality_specs(self):
        """获取质量规格"""
        if self.symbol.startswith('XAU'):
            return {'纯度': '99.5%以上', '形式': '金条/金锭'}
        elif self.symbol.startswith('XAG'):
            return {'纯度': '99.9%以上', '形式': '银条/银锭'}
        elif 'OIL' in self.symbol:
            return {'API比重': '37-42°', '硫含量': '<0.42%'}
        elif 'CU' in self.symbol:
            return {'纯度': '99.95%以上', '形式': '阴极铜'}
        else:
            return {'等级': self.quality_grade, '水分': '<14%'}
    
    def _get_inventory_status(self):
        """获取库存状态描述"""
        if self.inventory_level < 0.3:
            return "严重短缺"
        elif self.inventory_level < 0.5:
            return "偏紧"
        elif self.inventory_level < 0.7:
            return "正常"
        elif self.inventory_level < 0.9:
            return "充足"
        else:
            return "过剩"
    
    def _get_delivery_time(self):
        """获取交割时间"""
        if self.symbol.startswith('XAU') or self.symbol.startswith('XAG'):
            return random.randint(2, 5)  # 贵金属2-5天
        elif 'OIL' in self.symbol:
            return random.randint(3, 7)  # 原油3-7天
        else:
            return random.randint(5, 15)  # 其他商品5-15天


def create_spot_commodities():
    """创建现货商品"""
    commodities = {
        # 贵金属
        'XAUUSD_SPOT': SpotCommodity(
            'XAUUSD_SPOT', '现货黄金', 2045.67, '盎司', 0.015, 
            '标准金', '伦敦', 'USD', 0.025, 0.01
        ),
        'XAGUSD_SPOT': SpotCommodity(
            'XAGUSD_SPOT', '现货白银', 24.56, '盎司', 0.02, 
            '标准银', '伦敦', 'USD', 0.035, 0.001
        ),
        'XPTUSD_SPOT': SpotCommodity(
            'XPTUSD_SPOT', '现货铂金', 1025.40, '盎司', 0.025, 
            '标准铂', '伦敦', 'USD', 0.03, 0.01
        ),
        'XPDUSD_SPOT': SpotCommodity(
            'XPDUSD_SPOT', '现货钯金', 1125.80, '盎司', 0.03, 
            '标准钯', '伦敦', 'USD', 0.045, 0.01
        ),
        
        # 能源
        'WTI_SPOT': SpotCommodity(
            'WTI_SPOT', '现货WTI原油', 75.45, '桶', 0.01, 
            'WTI轻质原油', '库欣', 'USD', 0.03, 0.01
        ),
        'BRENT_SPOT': SpotCommodity(
            'BRENT_SPOT', '现货布伦特原油', 78.92, '桶', 0.01, 
            '布伦特原油', '北海', 'USD', 0.03, 0.01
        ),
        'NATGAS_SPOT': SpotCommodity(
            'NATGAS_SPOT', '现货天然气', 3.25, 'MMBtu', 0.005, 
            '天然气', '亨利港', 'USD', 0.05, 0.001
        ),
        
        # 工业金属
        'COPPER_SPOT': SpotCommodity(
            'COPPER_SPOT', '现货铜', 4.25, '磅', 0.02, 
            '阴极铜', '伦敦', 'USD', 0.025, 0.0005
        ),
        'ALUMINUM_SPOT': SpotCommodity(
            'ALUMINUM_SPOT', '现货铝', 0.89, '磅', 0.025, 
            '原铝', '伦敦', 'USD', 0.02, 0.0001
        ),
        'ZINC_SPOT': SpotCommodity(
            'ZINC_SPOT', '现货锌', 1.15, '磅', 0.03, 
            '锌锭', '伦敦', 'USD', 0.025, 0.0001
        ),
        
        # 农产品
        'CORN_SPOT': SpotCommodity(
            'CORN_SPOT', '现货玉米', 485.25, '蒲式耳', 0.015, 
            '#2黄玉米', '芝加哥', 'USD', 0.02, 0.25
        ),
        'WHEAT_SPOT': SpotCommodity(
            'WHEAT_SPOT', '现货小麦', 652.75, '蒲式耳', 0.02, 
            '#2软红冬麦', '芝加哥', 'USD', 0.025, 0.25
        ),
        'SOYBEAN_SPOT': SpotCommodity(
            'SOYBEAN_SPOT', '现货大豆', 1235.50, '蒲式耳', 0.018, 
            '#2黄大豆', '芝加哥', 'USD', 0.022, 0.25
        ),
        'COFFEE_SPOT': SpotCommodity(
            'COFFEE_SPOT', '现货咖啡', 165.25, '磅', 0.035, 
            '阿拉比卡', '纽约', 'USD', 0.04, 0.05
        ),
        'SUGAR_SPOT': SpotCommodity(
            'SUGAR_SPOT', '现货糖', 20.85, '磅', 0.025, 
            '原糖', '纽约', 'USD', 0.035, 0.01
        ),
        'COTTON_SPOT': SpotCommodity(
            'COTTON_SPOT', '现货棉花', 72.45, '磅', 0.02, 
            'Middling棉', '纽约', 'USD', 0.03, 0.01
        ),
    }
    
    return commodities 