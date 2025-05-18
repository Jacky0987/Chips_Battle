import json
import os
from datetime import datetime

class Achievement:
    def __init__(self, id, name, description, category, icon=None, hidden=False):
        self.id = id                  # 成就唯一标识符
        self.name = name              # 成就名称
        self.description = description # 成就描述
        self.category = category      # 成就类别（如"交易"、"投资组合"等）
        self.icon = icon              # 成就图标（可选）
        self.hidden = hidden          # 是否为隐藏成就
        self.unlocked = False         # 是否已解锁
        self.unlock_date = None       # 解锁日期

    def unlock(self):
        """解锁成就"""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
        return False

    def to_dict(self):
        """将成就转换为字典以便存储"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "icon": self.icon,
            "hidden": self.hidden,
            "unlocked": self.unlocked,
            "unlock_date": self.unlock_date
        }

    @classmethod
    def from_dict(cls, data):
        """从字典创建成就对象"""
        achievement = cls(
            data["id"], 
            data["name"], 
            data["description"], 
            data["category"],
            data.get("icon"),
            data.get("hidden", False)
        )
        achievement.unlocked = data.get("unlocked", False)
        achievement.unlock_date = data.get("unlock_date")
        return achievement


class AchievementManager:
    def __init__(self, achievements_file="data/achievements.json"):
        self.achievements_file = achievements_file
        self.achievements = {}
        self.load_achievements()
        
        # 如果没有成就，创建默认成就
        if not self.achievements:
            self.create_default_achievements()
            
    def create_default_achievements(self):
        """创建默认成就列表"""
        default_achievements = [
            # 交易类成就
            Achievement("first_trade", "初次交易", "完成您的第一笔交易", "交易"),
            Achievement("day_trader", "日内交易者", "在一天内完成10笔交易", "交易"),
            Achievement("big_spender", "大手笔", "单笔交易金额超过$10,000", "交易"),
            Achievement("diversified", "多元化投资", "同时持有5种不同的股票", "交易"),
            
            # 利润类成就
            Achievement("first_profit", "初尝甜头", "获得第一笔利润", "利润"),
            Achievement("double_money", "翻倍", "使您的投资组合价值翻倍", "利润"),
            Achievement("crypto_winner", "加密货币赢家", "从加密货币投资中获利超过50%", "利润"),
            Achievement("dividend_collector", "股息收藏家", "从股息中获得超过$1,000", "利润"),
            
            # 风险类成就
            Achievement("short_seller", "卖空者", "成功完成一笔卖空交易", "风险"),
            Achievement("risk_taker", "冒险家", "投资波动性超过4的股票", "风险"),
            Achievement("comeback_kid", "东山再起", "从20%的亏损中恢复", "风险"),
            
            # 时间类成就
            Achievement("week_survivor", "一周生存者", "成功交易一周（7天）", "时间"),
            Achievement("month_master", "月度大师", "成功交易一个月（30天）", "时间"),
            Achievement("market_veteran", "市场老手", "完成整个游戏周期", "时间"),
            
            # 隐藏成就
            Achievement("market_crash", "幸存者", "在市场崩盘中生存下来", "隐藏", hidden=True),
            Achievement("perfect_timing", "完美时机", "在股票价格最低点买入，最高点卖出", "隐藏", hidden=True),
            Achievement("crypto_billionaire", "加密货币亿万富翁", "加密货币投资获利超过1000%", "隐藏", hidden=True)
        ]
        
        for achievement in default_achievements:
            self.achievements[achievement.id] = achievement
            
        self.save_achievements()
        
    def load_achievements(self):
        """从文件加载成就"""
        try:
            if os.path.exists(self.achievements_file):
                with open(self.achievements_file, 'r') as file:
                    achievements_data = json.load(file)
                    for achievement_data in achievements_data:
                        achievement = Achievement.from_dict(achievement_data)
                        self.achievements[achievement.id] = achievement
                    print(f"已加载 {len(self.achievements)} 个成就")
        except Exception as e:
            print(f"加载成就时出错: {e}")
            self.achievements = {}
            
    def save_achievements(self):
        """保存成就到文件"""
        try:
            achievements_data = [achievement.to_dict() for achievement in self.achievements.values()]
            
            # 确保目录存在
            os.makedirs(os.path.dirname(self.achievements_file), exist_ok=True)
                
            with open(self.achievements_file, 'w') as file:
                json.dump(achievements_data, file, indent=4)
                print(f"已保存 {len(achievements_data)} 个成就到 {self.achievements_file}")
        except Exception as e:
            print(f"保存成就时出错: {e}")
            
    def unlock_achievement(self, achievement_id):
        """解锁指定的成就"""
        if achievement_id in self.achievements:
            achievement = self.achievements[achievement_id]
            if achievement.unlock():
                self.save_achievements()
                return achievement
        return None
    
    def get_achievement(self, achievement_id):
        """获取指定的成就"""
        return self.achievements.get(achievement_id)
    
    def get_all_achievements(self):
        """获取所有成就"""
        return list(self.achievements.values())
    
    def get_unlocked_achievements(self):
        """获取所有已解锁的成就"""
        return [a for a in self.achievements.values() if a.unlocked]
    
    def get_locked_achievements(self, include_hidden=False):
        """获取所有未解锁的成就"""
        if include_hidden:
            return [a for a in self.achievements.values() if not a.unlocked]
        else:
            return [a for a in self.achievements.values() if not a.unlocked and not a.hidden]
    
    def check_achievements(self, market, portfolio):
        """检查是否有新的成就可以解锁"""
        unlocked = []
        
        # 获取当前状态
        current_day = market.current_day
        net_worth = portfolio.net_worth_history[-1] if portfolio.net_worth_history else 0
        starting_cash = portfolio.starting_cash
        profit_percent = ((net_worth - starting_cash) / starting_cash) * 100 if starting_cash > 0 else 0
        
        # 交易相关成就
        if len(portfolio.transaction_history) >= 1:
            achievement = self.unlock_achievement("first_trade")
            if achievement:
                unlocked.append(achievement)
        
        # 计算当天交易数
        today_trades = sum(1 for t in portfolio.transaction_history if t["day"] == current_day)
        if today_trades >= 10:
            achievement = self.unlock_achievement("day_trader")
            if achievement:
                unlocked.append(achievement)
        
        # 检查大额交易
        for transaction in portfolio.transaction_history:
            if transaction["total"] >= 10000:
                achievement = self.unlock_achievement("big_spender")
                if achievement:
                    unlocked.append(achievement)
                break
        
        # 多元化投资
        if len(portfolio.stocks) >= 5:
            achievement = self.unlock_achievement("diversified")
            if achievement:
                unlocked.append(achievement)
        
        # 利润相关成就
        if profit_percent > 0 and not self.achievements["first_profit"].unlocked:
            achievement = self.unlock_achievement("first_profit")
            if achievement:
                unlocked.append(achievement)
        
        if profit_percent >= 100:
            achievement = self.unlock_achievement("double_money")
            if achievement:
                unlocked.append(achievement)
        
        # 时间相关成就
        if current_day >= 7:
            achievement = self.unlock_achievement("week_survivor")
            if achievement:
                unlocked.append(achievement)
        
        if current_day >= 30:
            achievement = self.unlock_achievement("month_master")
            if achievement:
                unlocked.append(achievement)
        
        if current_day >= market.max_days:
            achievement = self.unlock_achievement("market_veteran")
            if achievement:
                unlocked.append(achievement)
        
        # 卖空相关成就
        has_short = any(t["type"] == "SHORT" for t in portfolio.transaction_history)
        if has_short:
            achievement = self.unlock_achievement("short_seller")
            if achievement:
                unlocked.append(achievement)
        
        # 检查股息收入
        dividend_transactions = [t for t in portfolio.transaction_history if t.get("type") == "DIVIDEND"]
        total_dividends = sum(t["total"] for t in dividend_transactions) if dividend_transactions else 0
        if total_dividends >= 1000:
            achievement = self.unlock_achievement("dividend_collector")
            if achievement:
                unlocked.append(achievement)
        
        # 返回新解锁的成就
        return unlocked