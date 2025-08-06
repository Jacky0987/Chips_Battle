"""
经典轮盘赌游戏
体验蒙特卡洛风情的经典赌场游戏
"""

import random
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_app import BaseApp


class RouletteApp(BaseApp):
    """轮盘赌游戏"""
    
    def __init__(self):
        super().__init__(
            app_id="roulette",
            name="🎯 蒙特卡洛轮盘",
            description="经典欧式轮盘赌，体验赌场的优雅与刺激，多种投注方式等你尝试",
            price=9000,
            category="entertainment",
            version="1.0",
            emoji="🎯"
        )
        
        # 轮盘设置（欧式轮盘）
        self.numbers = list(range(0, 37))  # 0-36
        self.red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        self.black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    def run(self, main_app, action=None, bet_type=None, bet_value=None, bet_amount=None):
        """运行轮盘游戏"""
        self.main_app = main_app
        self.update_usage()
        
        if action == "spin" and bet_type and bet_amount:
            try:
                amount = float(bet_amount)
                return self._place_bet_and_spin(bet_type, bet_value, amount)
            except (ValueError, TypeError):
                return "❌ 无效的投注金额"
        elif action == "rules":
            return self._show_rules()
        elif action == "odds":
            return self._show_odds_table()
        else:
            return self._show_roulette_menu()
    
    def _place_bet_and_spin(self, bet_type: str, bet_value: str, bet_amount: float) -> str:
        """下注并旋转轮盘"""
        if bet_amount <= 0:
            return "❌ 投注金额必须大于0"
        
        if bet_amount > 20000:
            return "❌ 单次投注不能超过$20,000"
        
        if self.main_app.cash < bet_amount:
            return f"❌ 余额不足，需要${bet_amount:,.2f}，当前余额${self.main_app.cash:,.2f}"
        
        # 验证投注类型
        bet_info = self._validate_bet(bet_type, bet_value)
        if not bet_info['valid']:
            return bet_info['error']
        
        # 扣除投注金额
        self.main_app.cash -= bet_amount
        
        # 旋转轮盘
        winning_number = self._spin_wheel()
        
        # 计算是否中奖和奖金
        payout = self._calculate_payout(bet_info, winning_number, bet_amount)
        
        if payout > 0:
            self.main_app.cash += payout
            
            # 更新统计
            self.main_app.user_data.setdefault('roulette_stats', {'wins': 0, 'spins': 0, 'total_winnings': 0})
            self.main_app.user_data['roulette_stats']['wins'] += 1
            self.main_app.user_data['roulette_stats']['total_winnings'] += (payout - bet_amount)
        
        self.main_app.user_data.setdefault('roulette_stats', {'wins': 0, 'spins': 0, 'total_winnings': 0})
        self.main_app.user_data['roulette_stats']['spins'] += 1
        
        # 生成结果报告
        return self._generate_result_report(bet_info, winning_number, bet_amount, payout)
    
    def _validate_bet(self, bet_type: str, bet_value: str = None) -> dict:
        """验证投注"""
        bet_type = bet_type.lower()
        
        valid_bets = {
            # 直注
            'number': lambda v: v and v.isdigit() and 0 <= int(v) <= 36,
            'straight': lambda v: v and v.isdigit() and 0 <= int(v) <= 36,
            
            # 颜色投注
            'red': lambda v: True,
            'black': lambda v: True,
            
            # 奇偶投注
            'odd': lambda v: True,
            'even': lambda v: True,
            
            # 大小投注
            'low': lambda v: True,  # 1-18
            'high': lambda v: True,  # 19-36
            
            # 列投注
            'column1': lambda v: True,  # 1,4,7...34
            'column2': lambda v: True,  # 2,5,8...35
            'column3': lambda v: True,  # 3,6,9...36
            
            # 打投注
            'dozen1': lambda v: True,  # 1-12
            'dozen2': lambda v: True,  # 13-24
            'dozen3': lambda v: True,  # 25-36
        }
        
        if bet_type not in valid_bets:
            return {
                'valid': False,
                'error': f"❌ 无效的投注类型: {bet_type}\n💡 可用类型: number, red, black, odd, even, low, high, column1-3, dozen1-3"
            }
        
        if not valid_bets[bet_type](bet_value):
            return {
                'valid': False,
                'error': f"❌ 投注类型 {bet_type} 的参数无效: {bet_value}"
            }
        
        return {
            'valid': True,
            'bet_type': bet_type,
            'bet_value': bet_value,
            'description': self._get_bet_description(bet_type, bet_value)
        }
    
    def _get_bet_description(self, bet_type: str, bet_value: str = None) -> str:
        """获取投注描述"""
        descriptions = {
            'number': f"直注 {bet_value}号",
            'straight': f"直注 {bet_value}号",
            'red': "红色",
            'black': "黑色", 
            'odd': "奇数",
            'even': "偶数",
            'low': "小数 (1-18)",
            'high': "大数 (19-36)",
            'column1': "第一列 (1,4,7...34)",
            'column2': "第二列 (2,5,8...35)",
            'column3': "第三列 (3,6,9...36)",
            'dozen1': "第一打 (1-12)",
            'dozen2': "第二打 (13-24)",
            'dozen3': "第三打 (25-36)"
        }
        return descriptions.get(bet_type, bet_type)
    
    def _spin_wheel(self) -> int:
        """旋转轮盘"""
        return random.choice(self.numbers)
    
    def _calculate_payout(self, bet_info: dict, winning_number: int, bet_amount: float) -> float:
        """计算奖金"""
        bet_type = bet_info['bet_type']
        bet_value = bet_info['bet_value']
        
        # 直注 (35:1)
        if bet_type in ['number', 'straight']:
            if winning_number == int(bet_value):
                return bet_amount * 36  # 35:1 + 本金
        
        # 0单独处理（只有直注才中）
        if winning_number == 0:
            return 0
        
        # 颜色投注 (1:1)
        if bet_type == 'red' and winning_number in self.red_numbers:
            return bet_amount * 2
        if bet_type == 'black' and winning_number in self.black_numbers:
            return bet_amount * 2
        
        # 奇偶投注 (1:1)
        if bet_type == 'odd' and winning_number % 2 == 1:
            return bet_amount * 2
        if bet_type == 'even' and winning_number % 2 == 0:
            return bet_amount * 2
        
        # 大小投注 (1:1)
        if bet_type == 'low' and 1 <= winning_number <= 18:
            return bet_amount * 2
        if bet_type == 'high' and 19 <= winning_number <= 36:
            return bet_amount * 2
        
        # 列投注 (2:1)
        if bet_type == 'column1' and winning_number % 3 == 1:
            return bet_amount * 3
        if bet_type == 'column2' and winning_number % 3 == 2:
            return bet_amount * 3
        if bet_type == 'column3' and winning_number % 3 == 0:
            return bet_amount * 3
        
        # 打投注 (2:1)
        if bet_type == 'dozen1' and 1 <= winning_number <= 12:
            return bet_amount * 3
        if bet_type == 'dozen2' and 13 <= winning_number <= 24:
            return bet_amount * 3
        if bet_type == 'dozen3' and 25 <= winning_number <= 36:
            return bet_amount * 3
        
        return 0  # 未中奖
    
    def _generate_result_report(self, bet_info: dict, winning_number: int, bet_amount: float, payout: float) -> str:
        """生成结果报告"""
        # 确定数字颜色
        number_color = ""
        if winning_number == 0:
            number_color = "🟢 绿色"
        elif winning_number in self.red_numbers:
            number_color = "🔴 红色"
        else:
            number_color = "⚫ 黑色"
        
        # 确定数字属性
        attributes = []
        if winning_number > 0:
            attributes.append("奇数" if winning_number % 2 == 1 else "偶数")
            attributes.append("小数 (1-18)" if winning_number <= 18 else "大数 (19-36)")
            
            # 列
            if winning_number % 3 == 1:
                attributes.append("第一列")
            elif winning_number % 3 == 2:
                attributes.append("第二列")
            else:
                attributes.append("第三列")
            
            # 打
            if 1 <= winning_number <= 12:
                attributes.append("第一打")
            elif 13 <= winning_number <= 24:
                attributes.append("第二打")
            else:
                attributes.append("第三打")
        
        is_winner = payout > 0
        
        report = f"""
🎯 轮盘结果报告

🎰 轮盘结果:
  中奖号码: {winning_number}
  颜色: {number_color}
  属性: {' | '.join(attributes) if attributes else '特殊号码'}

💰 您的投注:
  投注类型: {bet_info['description']}
  投注金额: ${bet_amount:,.2f}

🏆 开奖结果:
"""
        
        if is_winner:
            profit = payout - bet_amount
            multiplier = payout / bet_amount
            report += f"""  🎉 恭喜中奖！
  奖金总额: ${payout:,.2f}
  净盈利: ${profit:,.2f}
  赔率: 1:{multiplier-1:.1f}
  当前余额: ${self.main_app.cash:,.2f}"""
        else:
            report += f"""  ❌ 很遗憾未中奖
  当前余额: ${self.main_app.cash:,.2f}"""
        
        # 统计信息
        stats = self.main_app.user_data.get('roulette_stats', {'wins': 0, 'spins': 0, 'total_winnings': 0})
        win_rate = (stats['wins'] / stats['spins'] * 100) if stats['spins'] > 0 else 0
        
        report += f"""

📈 个人统计:
  游戏次数: {stats['spins']}
  中奖次数: {stats['wins']}
  胜率: {win_rate:.1f}%
  累计盈亏: ${stats['total_winnings']:,.2f}

🎮 继续游戏:
  appmarket.app roulette                      # 返回主菜单
  appmarket.app roulette spin red 500         # 投注红色$500
  appmarket.app roulette spin number 7 100    # 直注7号$100
"""
        
        return report
    
    def _show_roulette_menu(self) -> str:
        """显示轮盘主菜单"""
        stats = self.main_app.user_data.get('roulette_stats', {'wins': 0, 'spins': 0, 'total_winnings': 0})
        win_rate = (stats['wins'] / stats['spins'] * 100) if stats['spins'] > 0 else 0
        
        return f"""
🎯 蒙特卡洛轮盘 - 欢迎光临

🎰 经典欧式轮盘体验
  • 37个数字 (0-36)
  • 多种投注选择
  • 真实赔率计算
  • 优雅的赌场氛围

💰 当前状态:
  可用资金: ${self.main_app.cash:,.2f}
  游戏次数: {stats['spins']}
  胜率: {win_rate:.1f}%
  累计盈亏: ${stats['total_winnings']:,.2f}

🎮 投注命令:
  appmarket.app roulette spin <类型> [值] <金额>

🔴 颜色投注 (1:1赔率):
  appmarket.app roulette spin red 500         # 投注红色$500
  appmarket.app roulette spin black 1000      # 投注黑色$1000

🎯 数字直注 (35:1赔率):
  appmarket.app roulette spin number 7 100    # 直注7号$100
  appmarket.app roulette spin straight 23 500 # 直注23号$500

⚖️ 奇偶投注 (1:1赔率):
  appmarket.app roulette spin odd 300          # 投注奇数$300
  appmarket.app roulette spin even 800         # 投注偶数$800

📊 大小投注 (1:1赔率):
  appmarket.app roulette spin low 400          # 投注小数(1-18)$400
  appmarket.app roulette spin high 600         # 投注大数(19-36)$600

📋 列投注 (2:1赔率):
  appmarket.app roulette spin column1 200      # 第一列$200
  appmarket.app roulette spin column2 200      # 第二列$200
  appmarket.app roulette spin column3 200      # 第三列$200

🎲 打投注 (2:1赔率):
  appmarket.app roulette spin dozen1 300       # 第一打(1-12)$300
  appmarket.app roulette spin dozen2 300       # 第二打(13-24)$300
  appmarket.app roulette spin dozen3 300       # 第三打(25-36)$300

📖 查看信息:
  appmarket.app roulette rules                # 游戏规则
  appmarket.app roulette odds                 # 赔率表

⚡ 投注限制:
  • 单次最低投注: $10
  • 单次最高投注: $20,000
  • 支持多种投注组合

🎯 投注策略:
  • 保守型: 颜色、奇偶、大小投注
  • 激进型: 数字直注
  • 平衡型: 列投注、打投注

💫 特殊说明:
  • 0号为绿色特殊号码
  • 只有直注0号才能在0开出时获胜
  • 其他投注在0开出时均败北
"""
    
    def _show_odds_table(self) -> str:
        """显示赔率表"""
        return """
🎯 蒙特卡洛轮盘 - 赔率表

🎰 投注类型与赔率:

📍 单号投注:
  • 直注 (Straight Up)          35:1
    投注单个数字(0-36)

🎨 颜色投注:
  • 红色 (Red)                 1:1
  • 黑色 (Black)               1:1

⚖️ 奇偶投注:
  • 奇数 (Odd)                 1:1
  • 偶数 (Even)                1:1

📊 大小投注:
  • 小数 1-18 (Low)            1:1
  • 大数 19-36 (High)          1:1

📋 列投注:
  • 第一列 (1,4,7...34)        2:1
  • 第二列 (2,5,8...35)        2:1
  • 第三列 (3,6,9...36)        2:1

🎲 打投注:
  • 第一打 1-12                2:1
  • 第二打 13-24               2:1
  • 第三打 25-36               2:1

🟢 特殊号码:
  • 0号 - 绿色
  • 只有直注0号才能获胜
  • 其他投注在0出现时均败北

💡 中奖概率:
  • 直注: 2.7% (1/37)
  • 颜色/奇偶/大小: 48.6% (18/37)
  • 列投注/打投注: 32.4% (12/37)

🎯 策略建议:
  • 新手推荐: 颜色投注 (风险较低)
  • 进阶玩家: 列投注/打投注 (平衡)
  • 冒险家: 直注 (高风险高回报)

⚠️ 重要提醒:
  轮盘是概率游戏，每次旋转都是独立事件
  理性投注，量力而行，享受游戏乐趣
"""
    
    def _show_rules(self) -> str:
        """显示游戏规则"""
        return """
🎯 蒙特卡洛轮盘 - 游戏规则

🎰 基本规则:
  • 欧式轮盘: 0-36共37个数字
  • 荷官旋转轮盘，小球落在某个数字上
  • 根据投注类型判断是否中奖
  • 按照相应赔率支付奖金

🎨 数字分布:
  • 红色数字: 1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36
  • 黑色数字: 2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35  
  • 绿色数字: 0 (特殊号码)

📋 投注区域:
  1. 内围投注 (Inside Bets):
     • 直注: 投注单个数字
     
  2. 外围投注 (Outside Bets):
     • 颜色: 红色/黑色
     • 奇偶: 奇数/偶数
     • 大小: 1-18/19-36
     • 列投注: 三列数字
     • 打投注: 1-12/13-24/25-36

🎯 中奖判定:
  • 小球最终停留的数字决定结果
  • 根据投注类型检查是否中奖
  • 中奖按相应赔率支付奖金
  • 未中奖失去投注金额

🟢 零号特殊规则:
  • 0号出现时，只有直注0号获胜
  • 所有外围投注(颜色、奇偶等)均败北
  • 这是赌场的数学优势来源

💰 奖金计算:
  • 奖金 = 投注金额 × (赔率 + 1)
  • 例: $100直注中奖 = $100 × 36 = $3,600
  • 例: $100红色中奖 = $100 × 2 = $200

⚡ 投注限制:
  • 每次投注: $10 - $20,000
  • 必须有足够余额
  • 每次只能选择一种投注类型

🎮 游戏流程:
  1. 选择投注类型和金额
  2. 确认投注并扣除资金
  3. 轮盘旋转，小球滚动
  4. 小球停止，公布结果
  5. 结算奖金或损失

🏆 获胜策略:
  • 没有必胜策略，每次旋转都是独立事件
  • 合理分配资金，设置止损点
  • 不要追逐损失，保持冷静
  • 享受游戏过程，理性投注

⚠️ 风险提示:
  轮盘赌存在数学优势给赌场 (约2.7%)
  长期来看，玩家胜率略低于50%
  请理性娱乐，切勿成瘾，量力而行
""" 