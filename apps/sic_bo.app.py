"""
骰宝游戏（大小游戏）
经典三骰子投注游戏
"""

import random
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_app import BaseApp


class SicBoApp(BaseApp):
    """骰宝游戏"""
    
    def __init__(self):
        super().__init__(
            app_id="sic_bo",
            name="🎲 澳门骰宝",
            description="经典三骰子投注游戏，预测骰子点数组合，体验澳门赌场风情",
            price=6000,
            category="entertainment",
            version="1.0",
            emoji="🎲"
        )
    
    def run(self, main_app, action=None, bet_type=None, bet_value=None, bet_amount=None):
        """运行骰宝游戏"""
        self.main_app = main_app
        self.update_usage()
        
        if action == "roll" and bet_type and bet_amount:
            try:
                amount = float(bet_amount)
                return self._place_bet_and_roll(bet_type, bet_value, amount)
            except (ValueError, TypeError):
                return "❌ 无效的投注金额"
        elif action == "rules":
            return self._show_rules()
        elif action == "odds":
            return self._show_odds_table()
        else:
            return self._show_sic_bo_menu()
    
    def _place_bet_and_roll(self, bet_type: str, bet_value: str, bet_amount: float) -> str:
        """下注并掷骰子"""
        if bet_amount <= 0:
            return "❌ 投注金额必须大于0"
        
        if bet_amount > 15000:
            return "❌ 单次投注不能超过$15,000"
        
        if self.main_app.cash < bet_amount:
            return f"❌ 余额不足，需要${bet_amount:,.2f}，当前余额${self.main_app.cash:,.2f}"
        
        # 验证投注类型
        bet_info = self._validate_bet(bet_type, bet_value)
        if not bet_info['valid']:
            return bet_info['error']
        
        # 扣除投注金额
        self.main_app.cash -= bet_amount
        
        # 掷骰子
        dice_result = self._roll_dice()
        
        # 计算是否中奖和奖金
        payout = self._calculate_payout(bet_info, dice_result, bet_amount)
        
        if payout > 0:
            self.main_app.cash += payout
            
            # 更新统计
            self.main_app.user_data.setdefault('sic_bo_stats', {'wins': 0, 'rolls': 0, 'total_winnings': 0})
            self.main_app.user_data['sic_bo_stats']['wins'] += 1
            self.main_app.user_data['sic_bo_stats']['total_winnings'] += (payout - bet_amount)
        
        self.main_app.user_data.setdefault('sic_bo_stats', {'wins': 0, 'rolls': 0, 'total_winnings': 0})
        self.main_app.user_data['sic_bo_stats']['rolls'] += 1
        
        # 生成结果报告
        return self._generate_result_report(bet_info, dice_result, bet_amount, payout)
    
    def _validate_bet(self, bet_type: str, bet_value: str = None) -> dict:
        """验证投注"""
        bet_type = bet_type.lower()
        
        valid_bets = {
            # 大小投注
            'big': lambda v: True,      # 11-17点
            'small': lambda v: True,    # 4-10点
            
            # 点数投注
            'total': lambda v: v and v.isdigit() and 4 <= int(v) <= 17,
            
            # 单点投注
            'single': lambda v: v and v.isdigit() and 1 <= int(v) <= 6,
            
            # 双点投注
            'double': lambda v: v and v.isdigit() and 1 <= int(v) <= 6,
            
            # 三点投注（豹子）
            'triple': lambda v: v and v.isdigit() and 1 <= int(v) <= 6,
            'any_triple': lambda v: True,  # 任意豹子
            
            # 组合投注（二不同）
            'combo': lambda v: self._validate_combo(v),
            
            # 奇偶投注
            'odd': lambda v: True,
            'even': lambda v: True,
        }
        
        if bet_type not in valid_bets:
            return {
                'valid': False,
                'error': f"❌ 无效的投注类型: {bet_type}\n💡 可用类型: big, small, total, single, double, triple, any_triple, combo, odd, even"
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
    
    def _validate_combo(self, bet_value: str) -> bool:
        """验证组合投注"""
        if not bet_value or '-' not in bet_value:
            return False
        try:
            parts = bet_value.split('-')
            if len(parts) != 2:
                return False
            a, b = int(parts[0]), int(parts[1])
            return 1 <= a <= 6 and 1 <= b <= 6 and a != b
        except ValueError:
            return False
    
    def _get_bet_description(self, bet_type: str, bet_value: str = None) -> str:
        """获取投注描述"""
        descriptions = {
            'big': "大 (11-17点)",
            'small': "小 (4-10点)",
            'total': f"总和 {bet_value}点",
            'single': f"单点 {bet_value}",
            'double': f"对子 {bet_value}-{bet_value}",
            'triple': f"豹子 {bet_value}-{bet_value}-{bet_value}",
            'any_triple': "任意豹子",
            'combo': f"组合 {bet_value}",
            'odd': "奇数",
            'even': "偶数"
        }
        return descriptions.get(bet_type, bet_type)
    
    def _roll_dice(self) -> dict:
        """掷骰子"""
        dice = [random.randint(1, 6) for _ in range(3)]
        dice.sort()  # 排序便于比较
        total = sum(dice)
        
        return {
            'dice': dice,
            'total': total,
            'is_big': 11 <= total <= 17,
            'is_small': 4 <= total <= 10,
            'is_odd': total % 2 == 1,
            'is_even': total % 2 == 0,
            'is_triple': dice[0] == dice[1] == dice[2],
            'doubles': self._find_doubles(dice),
            'combinations': self._find_combinations(dice)
        }
    
    def _find_doubles(self, dice: list) -> list:
        """找出对子"""
        doubles = []
        if dice[0] == dice[1]:
            doubles.append(dice[0])
        elif dice[1] == dice[2]:
            doubles.append(dice[1])
        return doubles
    
    def _find_combinations(self, dice: list) -> list:
        """找出组合（二不同）"""
        combinations = []
        for i in range(3):
            for j in range(i + 1, 3):
                if dice[i] != dice[j]:
                    combo = tuple(sorted([dice[i], dice[j]]))
                    if combo not in combinations:
                        combinations.append(combo)
        return combinations
    
    def _calculate_payout(self, bet_info: dict, dice_result: dict, bet_amount: float) -> float:
        """计算奖金"""
        bet_type = bet_info['bet_type']
        bet_value = bet_info['bet_value']
        dice = dice_result['dice']
        total = dice_result['total']
        
        # 豹子特殊处理（除特定豹子投注外，其他投注均败北）
        if dice_result['is_triple'] and bet_type not in ['triple', 'any_triple', 'single']:
            return 0
        
        # 大小投注 (1:1)
        if bet_type == 'big' and dice_result['is_big']:
            return bet_amount * 2
        if bet_type == 'small' and dice_result['is_small']:
            return bet_amount * 2
        
        # 奇偶投注 (1:1)
        if bet_type == 'odd' and dice_result['is_odd']:
            return bet_amount * 2
        if bet_type == 'even' and dice_result['is_even']:
            return bet_amount * 2
        
        # 点数投注（按点数不同赔率）
        if bet_type == 'total':
            target_total = int(bet_value)
            if total == target_total:
                return bet_amount * self._get_total_odds(target_total)
        
        # 单点投注
        if bet_type == 'single':
            target_number = int(bet_value)
            count = dice.count(target_number)
            if count > 0:
                return bet_amount * (count + 1)  # 出现几次就赔几倍+本金
        
        # 对子投注 (10:1)
        if bet_type == 'double':
            target_number = int(bet_value)
            if target_number in dice_result['doubles']:
                return bet_amount * 11
        
        # 特定豹子投注 (180:1)
        if bet_type == 'triple':
            target_number = int(bet_value)
            if dice_result['is_triple'] and dice[0] == target_number:
                return bet_amount * 181
        
        # 任意豹子投注 (30:1)
        if bet_type == 'any_triple' and dice_result['is_triple']:
            return bet_amount * 31
        
        # 组合投注 (5:1)
        if bet_type == 'combo':
            target_combo = tuple(sorted([int(x) for x in bet_value.split('-')]))
            if target_combo in dice_result['combinations']:
                return bet_amount * 6
        
        return 0  # 未中奖
    
    def _get_total_odds(self, total: int) -> int:
        """获取点数投注赔率"""
        odds_table = {
            4: 61, 5: 31, 6: 18, 7: 13, 8: 9, 9: 7,
            10: 7, 11: 7, 12: 9, 13: 13, 14: 18, 15: 31, 16: 61, 17: 61
        }
        return odds_table.get(total, 1)
    
    def _generate_result_report(self, bet_info: dict, dice_result: dict, bet_amount: float, payout: float) -> str:
        """生成结果报告"""
        dice = dice_result['dice']
        total = dice_result['total']
        is_winner = payout > 0
        
        # 骰子显示
        dice_emojis = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
        dice_display = " ".join([dice_emojis[d-1] for d in dice])
        
        # 判断结果属性
        attributes = []
        if dice_result['is_triple']:
            attributes.append(f"豹子 {dice[0]}-{dice[0]}-{dice[0]}")
        else:
            attributes.append("大" if dice_result['is_big'] else "小")
            attributes.append("奇" if dice_result['is_odd'] else "偶")
            
            if dice_result['doubles']:
                for double in dice_result['doubles']:
                    attributes.append(f"对子 {double}")
        
        report = f"""
🎲 骰宝结果报告

🎰 骰子结果:
  骰子: {dice_display}
  点数: {dice[0]} + {dice[1]} + {dice[2]} = {total}
  属性: {' | '.join(attributes)}

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
        stats = self.main_app.user_data.get('sic_bo_stats', {'wins': 0, 'rolls': 0, 'total_winnings': 0})
        win_rate = (stats['wins'] / stats['rolls'] * 100) if stats['rolls'] > 0 else 0
        
        report += f"""

📈 个人统计:
  游戏次数: {stats['rolls']}
  中奖次数: {stats['wins']}
  胜率: {win_rate:.1f}%
  累计盈亏: ${stats['total_winnings']:,.2f}

🎮 继续游戏:
  appmarket.app sic_bo                      # 返回主菜单
  appmarket.app sic_bo roll big 500         # 投注大$500
  appmarket.app sic_bo roll triple 6 100    # 投注豹子6$100
"""
        
        return report
    
    def _show_sic_bo_menu(self) -> str:
        """显示骰宝主菜单"""
        stats = self.main_app.user_data.get('sic_bo_stats', {'wins': 0, 'rolls': 0, 'total_winnings': 0})
        win_rate = (stats['wins'] / stats['rolls'] * 100) if stats['rolls'] > 0 else 0
        
        return f"""
🎲 澳门骰宝 - 欢迎光临

🎰 经典三骰子投注游戏
  • 三颗骰子同时掷出
  • 多种投注选择
  • 真实澳门赔率
  • 刺激的赌场体验

💰 当前状态:
  可用资金: ${self.main_app.cash:,.2f}
  游戏次数: {stats['rolls']}
  胜率: {win_rate:.1f}%
  累计盈亏: ${stats['total_winnings']:,.2f}

🎮 投注命令:
  appmarket.app sic_bo roll <类型> [值] <金额>

🔴 大小投注 (1:1赔率):
  appmarket.app sic_bo roll big 500         # 投注大(11-17)$500
  appmarket.app sic_bo roll small 800       # 投注小(4-10)$800

⚖️ 奇偶投注 (1:1赔率):
  appmarket.app sic_bo roll odd 300          # 投注奇数$300
  appmarket.app sic_bo roll even 600         # 投注偶数$600

🎯 点数投注 (赔率不同):
  appmarket.app sic_bo roll total 4 100      # 投注总和4点$100
  appmarket.app sic_bo roll total 10 200     # 投注总和10点$200

🎲 单点投注 (按出现次数赔付):
  appmarket.app sic_bo roll single 6 300     # 投注6点$300

👯 对子投注 (10:1赔率):
  appmarket.app sic_bo roll double 5 200     # 投注对子5$200

🎯 豹子投注:
  appmarket.app sic_bo roll triple 6 100     # 投注豹子6(180:1)$100
  appmarket.app sic_bo roll any_triple 200   # 投注任意豹子(30:1)$200

🔗 组合投注 (5:1赔率):
  appmarket.app sic_bo roll combo 2-5 300    # 投注组合2-5$300

📖 查看信息:
  appmarket.app sic_bo rules                # 游戏规则
  appmarket.app sic_bo odds                 # 赔率表

⚡ 投注限制:
  • 单次最低投注: $10
  • 单次最高投注: $15,000
  • 支持多种投注组合

🎯 投注策略:
  • 稳健型: 大小、奇偶投注
  • 平衡型: 点数投注、单点投注
  • 激进型: 豹子投注

💫 特殊规则:
  • 豹子出现时大小奇偶投注败北
  • 单点投注按出现次数计算赔率
  • 组合投注需要两个不同数字
"""
    
    def _show_odds_table(self) -> str:
        """显示赔率表"""
        return """
🎲 澳门骰宝 - 赔率表

🎰 投注类型与赔率:

🔴 大小投注:
  • 大 (11-17点)              1:1
  • 小 (4-10点)               1:1
  ⚠️ 豹子出现时败北

⚖️ 奇偶投注:
  • 奇数                      1:1
  • 偶数                      1:1
  ⚠️ 豹子出现时败北

🎯 点数投注 (总和):
  • 4点, 17点                 60:1
  • 5点, 16点                 30:1
  • 6点, 15点                 17:1
  • 7点, 14点                 12:1
  • 8点, 13点                 8:1
  • 9点, 12点                 6:1
  • 10点, 11点                6:1

🎲 单点投注:
  • 出现1次                   1:1
  • 出现2次                   2:1
  • 出现3次                   3:1

👯 对子投注:
  • 指定对子 (如1-1)           10:1

🎯 豹子投注:
  • 指定豹子 (如6-6-6)         180:1
  • 任意豹子                  30:1

🔗 组合投注:
  • 二不同 (如2-5)             5:1

💡 中奖概率:
  • 大/小: 48.6% (遇豹子败北)
  • 奇/偶: 48.6% (遇豹子败北)
  • 单点1次: 34.7%
  • 单点2次: 6.9%
  • 单点3次: 0.46%
  • 对子: 7.4%
  • 指定豹子: 0.46%
  • 任意豹子: 2.8%
  • 组合: 13.9%

🎯 策略建议:
  • 新手: 大小投注 (简单易懂)
  • 进阶: 点数投注 (中等风险)
  • 高手: 组合投注 (平衡选择)
  • 冒险: 豹子投注 (高风险高回报)

⚠️ 重要提醒:
  骰宝是纯概率游戏，每次掷骰都是独立事件
  理性投注，量力而行，享受游戏乐趣
"""
    
    def _show_rules(self) -> str:
        """显示游戏规则"""
        return """
🎲 澳门骰宝 - 游戏规则

🎰 基本规则:
  • 使用三颗标准骰子
  • 同时掷出，根据结果判定输赢
  • 总点数范围: 3-18点
  • 支持多种投注方式

🎨 投注类型:

1️⃣ 大小投注:
   • 大: 总和11-17点 (赔率1:1)
   • 小: 总和4-10点 (赔率1:1)
   • 遇到豹子时败北

2️⃣ 奇偶投注:
   • 奇: 总和为奇数 (赔率1:1)
   • 偶: 总和为偶数 (赔率1:1)
   • 遇到豹子时败北

3️⃣ 点数投注:
   • 投注具体总和点数
   • 赔率根据概率不同

4️⃣ 单点投注:
   • 投注某个数字(1-6)
   • 按出现次数赔付

5️⃣ 对子投注:
   • 投注特定对子
   • 赔率10:1

6️⃣ 豹子投注:
   • 指定豹子: 三个相同数字
   • 任意豹子: 任何三个相同

7️⃣ 组合投注:
   • 投注两个不同数字的组合
   • 赔率5:1

🎯 特殊规则:

🟢 豹子效应:
  • 任何三个相同数字为豹子
  • 豹子出现时，大小奇偶投注败北
  • 只有豹子投注和单点投注获胜

💰 奖金计算:
  • 奖金 = 投注金额 × (赔率 + 1)
  • 单点投注特殊: 按出现次数倍数赔付

⚡ 投注限制:
  • 每次投注: $10 - $15,000
  • 必须有足够余额
  • 每次只能选择一种投注类型

🎮 游戏流程:
  1. 选择投注类型和金额
  2. 确认投注并扣除资金
  3. 掷出三颗骰子
  4. 根据结果判定输赢
  5. 结算奖金或损失

🏆 获胜策略:
  • 大小投注: 胜率接近50%，适合新手
  • 点数投注: 中等风险，合理回报
  • 组合投注: 平衡选择，多样化
  • 豹子投注: 高风险高回报，谨慎选择

⚠️ 风险提示:
  骰宝是概率游戏，没有必胜法则
  请合理规划资金，理性娱乐
  设置止损点，避免冲动投注
""" 