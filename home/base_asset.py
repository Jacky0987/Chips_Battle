"""
资产基类 - 所有投资品的基础类
"""

from abc import ABC, abstractmethod
from datetime import datetime
import random


class BaseAsset(ABC):
    """资产基类"""
    
    def __init__(self, asset_id, name, description, current_price, category, rarity="common", emoji="💎"):
        self.asset_id = asset_id
        self.name = name
        self.description = description
        self.current_price = current_price
        self.category = category
        self.rarity = rarity  # common, rare, epic, legendary
        self.emoji = emoji
        self.purchase_date = None
        self.purchase_price = 0
        self.quantity = 0
        self.last_update = datetime.now().isoformat()
        
        # 价格历史
        self.price_history = [current_price]
        self.volatility = self._get_base_volatility()
    
    @abstractmethod
    def update_price(self):
        """更新价格 - 子类必须实现"""
        pass
    
    def _get_base_volatility(self):
        """根据稀有度获取基础波动率"""
        volatility_map = {
            'common': 0.02,
            'rare': 0.05,
            'epic': 0.08,
            'legendary': 0.12
        }
        return volatility_map.get(self.rarity, 0.02)
    
    def get_value(self):
        """获取当前总价值"""
        return self.current_price * self.quantity
    
    def get_profit_loss(self):
        """获取盈亏"""
        if self.quantity == 0:
            return 0
        return (self.current_price - self.purchase_price) * self.quantity
    
    def get_profit_percentage(self):
        """获取盈亏百分比"""
        if self.purchase_price == 0:
            return 0
        return ((self.current_price - self.purchase_price) / self.purchase_price) * 100
    
    def get_rarity_info(self):
        """获取稀有度信息"""
        rarity_map = {
            'common': {'name': '普通', 'color': '⚪', 'multiplier': 1.0},
            'rare': {'name': '稀有', 'color': '🔵', 'multiplier': 1.5},
            'epic': {'name': '史诗', 'color': '🟣', 'multiplier': 2.0},
            'legendary': {'name': '传奇', 'color': '🟡', 'multiplier': 3.0}
        }
        return rarity_map.get(self.rarity, rarity_map['common'])
    
    def get_price_trend(self):
        """获取价格趋势"""
        if len(self.price_history) < 2:
            return "持平"
        
        recent_change = (self.price_history[-1] - self.price_history[-2]) / self.price_history[-2]
        if recent_change > 0.02:
            return "📈 上涨"
        elif recent_change < -0.02:
            return "📉 下跌"
        else:
            return "➡️ 持平"
    
    def get_info_display(self):
        """获取信息展示"""
        rarity_info = self.get_rarity_info()
        trend = self.get_price_trend()
        
        return f"""
{self.emoji} {self.name} {rarity_info['color']}
  类别: {self.category}
  稀有度: {rarity_info['name']}
  当前价格: ${self.current_price:,.2f}
  趋势: {trend}
  持有数量: {self.quantity}
  总价值: ${self.get_value():,.2f}
  盈亏: ${self.get_profit_loss():+,.2f} ({self.get_profit_percentage():+.1f}%)
""" 


class CollectibleAsset(BaseAsset):
    """收藏品资产类"""
    
    def __init__(self, asset_id, name, description, current_price, collectible_type, artist_creator="", year_created="", rarity="common"):
        super().__init__(
            asset_id,
            name,
            description,
            current_price,
            f"收藏品-{collectible_type}",
            rarity,
            self._get_collectible_emoji(collectible_type)
        )
        self.collectible_type = collectible_type  # art, jewelry, digital, antique, memorabilia
        self.artist_creator = artist_creator
        self.year_created = year_created
        self.condition = "完美"  # 完美、优良、良好、一般
        self.authentication = "已认证"
        self.provenance = "清晰"  # 来源记录
        
    def _get_collectible_emoji(self, collectible_type):
        """根据收藏品类型获取emoji"""
        emoji_map = {
            'art': '🎨',
            'jewelry': '💎',
            'digital': '🖼️',
            'antique': '🏺',
            'memorabilia': '🏆',
            'watch': '⌚',
            'wine': '🍷',
            'book': '📚'
        }
        return emoji_map.get(collectible_type, '💰')
    
    def update_price(self):
        """更新收藏品价格"""
        # 收藏品价格受多种因素影响
        base_change = random.gauss(0, self.volatility)
        
        # 市场热度影响
        market_trend = self._get_market_trend()
        base_change += market_trend
        
        # 稀有度加成
        rarity_info = self.get_rarity_info()
        rarity_bonus = (rarity_info['multiplier'] - 1) * 0.01
        base_change += random.uniform(-rarity_bonus, rarity_bonus)
        
        # 时间增值（老物件可能更值钱）
        if self.year_created:
            try:
                age = 2024 - int(self.year_created)
                if age > 50:  # 超过50年的物品有时间增值
                    base_change += random.uniform(0, 0.005)
            except:
                pass
        
        # 条件影响
        condition_multiplier = {
            "完美": 1.0,
            "优良": 0.95,
            "良好": 0.85,
            "一般": 0.7
        }
        condition_factor = condition_multiplier.get(self.condition, 1.0)
        
        # 更新价格
        new_price = self.current_price * (1 + base_change) * condition_factor
        new_price = max(new_price, self.current_price * 0.7)  # 最大跌幅30%
        
        self.current_price = round(new_price, 2)
        self.price_history.append(self.current_price)
        
        if len(self.price_history) > 50:
            self.price_history = self.price_history[-50:]
        
        self.last_update = datetime.now().isoformat()
    
    def _get_market_trend(self):
        """获取市场趋势"""
        trends = {
            'art': random.uniform(-0.03, 0.04),
            'jewelry': random.uniform(-0.02, 0.03),
            'digital': random.uniform(-0.05, 0.08),  # 数字藏品波动较大
            'antique': random.uniform(-0.015, 0.025),
            'memorabilia': random.uniform(-0.04, 0.06),
            'watch': random.uniform(-0.02, 0.03),
            'wine': random.uniform(-0.01, 0.02),
            'book': random.uniform(-0.01, 0.015)
        }
        return trends.get(self.collectible_type, 0)
    
    def get_detailed_info(self):
        """获取详细信息"""
        rarity_info = self.get_rarity_info()
        trend = self.get_price_trend()
        
        return f"""
{self.emoji} {self.name} {rarity_info['color']}

📋 基本信息:
  类型: {self.collectible_type.title()}
  创作者/品牌: {self.artist_creator or '未知'}
  年份: {self.year_created or '未知'}
  稀有度: {rarity_info['name']}
  
🔍 状态信息:
  品相: {self.condition}
  认证: {self.authentication}
  来源: {self.provenance}
  
💰 价值信息:
  当前价格: ${self.current_price:,.2f}
  价格趋势: {trend}
  持有数量: {self.quantity}
  总价值: ${self.get_value():,.2f}
  
📈 投资表现:
  购入价格: ${self.purchase_price:.2f}
  盈亏金额: ${self.get_profit_loss():+,.2f}
  盈亏比例: {self.get_profit_percentage():+.1f}%
  
🎯 收藏特点:
  {self._get_collection_features()}
"""
    
    def _get_collection_features(self):
        """获取收藏特点"""
        features = []
        
        if self.condition == "完美":
            features.append("💎 完美品相")
        elif self.condition == "优良":
            features.append("✨ 优良状态")
        
        if self.authentication == "已认证":
            features.append("🔒 权威认证")
        
        if self.rarity == "legendary":
            features.append("👑 传奇稀有")
        elif self.rarity == "epic":
            features.append("🟣 史诗级别")
        
        try:
            age = 2024 - int(self.year_created)
            if age > 100:
                features.append("🏺 百年古董")
            elif age > 50:
                features.append("📜 古董收藏")
        except:
            pass
        
        if self.collectible_type == "digital":
            features.append("🔮 数字原创")
        
        return " | ".join(features) if features else "🎯 潜力收藏"


class DigitalMemento(BaseAsset):
    """数字纪念品类 - 记录游戏成就和特殊时刻"""
    
    def __init__(self, asset_id, name, description, achievement_data, rarity="common"):
        # 数字纪念品没有传统价格，价值基于成就重要性
        base_value = self._calculate_achievement_value(achievement_data)
        super().__init__(
            asset_id,
            name,
            description,
            base_value,
            "数字纪念品",
            rarity,
            "🎖️"
        )
        self.achievement_data = achievement_data
        self.creation_date = datetime.now().isoformat()
        self.is_tradeable = False  # 大部分纪念品不可交易
        
    def _calculate_achievement_value(self, achievement_data):
        """根据成就数据计算纪念品价值"""
        base_values = {
            'bronze': 1000,
            'silver': 5000,
            'gold': 15000,
            'legendary': 50000
        }
        
        tier = achievement_data.get('tier', 'bronze')
        base_value = base_values.get(tier, 1000)
        
        # 隐藏成就更有价值
        if achievement_data.get('hidden', False):
            base_value *= 2
        
        # 稀有成就更有价值
        if achievement_data.get('completion_rate', 100) < 10:  # 少于10%玩家获得
            base_value *= 3
        
        return base_value
    
    def update_price(self):
        """数字纪念品价值基本不变，只有小幅波动"""
        # 纪念品价值主要基于纪念意义，市场波动很小
        small_change = random.uniform(-0.005, 0.005)
        self.current_price *= (1 + small_change)
        self.price_history.append(self.current_price)
        
        if len(self.price_history) > 30:
            self.price_history = self.price_history[-30:]
    
    def get_detailed_info(self):
        """获取详细信息"""
        rarity_info = self.get_rarity_info()
        
        return f"""
🎖️ {self.name} {rarity_info['color']}

📋 纪念品信息:
  类型: 数字纪念品
  稀有度: {rarity_info['name']}
  创建日期: {self.creation_date[:10]}
  是否可交易: {'是' if self.is_tradeable else '否'}
  
🏆 相关成就:
  成就名称: {self.achievement_data.get('name', '未知')}
  成就等级: {self.achievement_data.get('tier', 'bronze').title()}
  成就描述: {self.achievement_data.get('desc', '暂无描述')}
  
💎 收藏价值:
  纪念价值: ${self.current_price:,.2f}
  持有数量: {self.quantity}
  总价值: ${self.get_value():,.2f}
  
🌟 特殊意义:
  这是您在投资旅程中的重要里程碑纪念品
  代表了您在 {self.achievement_data.get('category', '未知')} 领域的卓越表现
  具有独特的个人纪念价值，无法复制
"""


def create_collectible_items():
    """创建收藏品数据"""
    collectibles = [
        # 艺术品收藏
        CollectibleAsset("mona_lisa_print", "蒙娜丽莎限量版画", "达芬奇名作的高品质限量复制品", 15000, "art", "达芬奇", "1503", "rare"),
        CollectibleAsset("starry_night_print", "星夜限量版画", "梵高经典作品的官方授权复制品", 12000, "art", "梵高", "1889", "rare"),
        CollectibleAsset("modern_abstract", "现代抽象原作", "当代知名艺术家的原创作品", 25000, "art", "张大千", "2020", "epic"),
        CollectibleAsset("chinese_calligraphy", "古代书法真迹", "明代书法家珍贵手稿", 80000, "art", "王羲之", "1400", "legendary"),
        
        # 珠宝首饰
        CollectibleAsset("diamond_ring", "1克拉钻戒", "D色VVS1级别完美钻石戒指", 35000, "jewelry", "蒂芙尼", "2023", "epic"),
        CollectibleAsset("ruby_necklace", "红宝石项链", "缅甸产天然红宝石精工项链", 28000, "jewelry", "卡地亚", "2022", "epic"),
        CollectibleAsset("vintage_brooch", "古董胸针", "维多利亚时代珍稀古董胸针", 15000, "jewelry", "未知", "1850", "rare"),
        CollectibleAsset("platinum_watch", "铂金腕表", "瑞士制造限量版铂金腕表", 65000, "watch", "百达翡丽", "2023", "legendary"),
        
        # 数字藏品
        CollectibleAsset("nft_artwork", "加密艺术品", "区块链认证的数字艺术原创作品", 8000, "digital", "CryptoPunk", "2023", "rare"),
        CollectibleAsset("virtual_land", "虚拟土地", "元宇宙中的稀有数字地产", 12000, "digital", "Decentraland", "2023", "epic"),
        CollectibleAsset("digital_avatar", "数字化身", "独特设计的3D数字化身", 5000, "digital", "BAYC", "2023", "common"),
        
        # 古董收藏
        CollectibleAsset("ming_vase", "明代青花瓷瓶", "明朝永乐年间珍贵青花瓷器", 120000, "antique", "景德镇", "1420", "legendary"),
        CollectibleAsset("ancient_coin", "古代钱币", "唐朝开元通宝银币", 3000, "antique", "唐朝", "700", "common"),
        CollectibleAsset("jade_sculpture", "和田玉雕", "清代宫廷玉雕工艺品", 45000, "antique", "清宫", "1700", "epic"),
        
        # 纪念品收藏
        CollectibleAsset("sports_memorabilia", "体育纪念品", "著名运动员签名球衣", 8000, "memorabilia", "乔丹", "1996", "rare"),
        CollectibleAsset("vintage_guitar", "古董吉他", "1960年代Fender Stratocaster", 35000, "memorabilia", "Fender", "1965", "epic"),
        CollectibleAsset("first_edition_book", "初版珍本", "哈利波特与魔法石初版", 2500, "book", "J.K.罗琳", "1997", "rare"),
        
        # 红酒收藏
        CollectibleAsset("bordeaux_wine", "波尔多红酒", "1982年拉菲古堡红酒", 15000, "wine", "拉菲", "1982", "epic"),
        CollectibleAsset("champagne_vintage", "年份香槟", "Dom Pérignon 1996年份香槟", 800, "wine", "Dom Pérignon", "1996", "rare"),
    ]
    
    return {item.asset_id: item for item in collectibles} 