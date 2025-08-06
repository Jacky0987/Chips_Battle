"""
老虎机游戏应用
"""

import random
from datetime import datetime
from apps.base_app import BaseApp


class SlotMachineApp(BaseApp):
    """老虎机游戏应用"""
    
    def __init__(self):
        super().__init__(
            "slot_machine",
            "幸运老虎机",
            "经典老虎机游戏，投入资金试试运气！支持多种投注额度。",
            5000,
            "游戏娱乐",
            "1.0",
            "🎰"
        )
        self.symbols = ['🍒', '🍋', '🍊', '🍇', '⭐', '💎', '🔔', '7️⃣']
        self.payouts = {
            '💎💎💎': 50,
            '7️⃣7️⃣7️⃣': 30,
            '🔔🔔🔔': 20,
            '⭐⭐⭐': 15,
            '🍇🍇🍇': 10,
            '🍊🍊🍊': 8,
            '🍋🍋🍋': 6,
            '🍒🍒🍒': 5
        }
    
    def run(self, main_app, bet_amount=None):
        """运行老虎机游戏"""
        self.update_usage()
        
        # 获取投注金额
        if bet_amount is None:
            return self._show_slot_menu(main_app)
        
        try:
            bet_amount = float(bet_amount)
            if bet_amount <= 0:
                return "❌ 投注金额必须大于0"
            if bet_amount > main_app.cash:
                return "❌ 资金不足"
            if bet_amount > 10000:
                return "❌ 单次投注金额不能超过$10,000"
        except ValueError:
            return "❌ 无效的投注金额"
        
        # 扣除投注金额
        main_app.cash -= bet_amount
        
        # 生成随机结果
        result = [random.choice(self.symbols) for _ in range(3)]
        result_str = ''.join(result)
        
        # 计算奖金
        payout_multiplier = 0
        for pattern, multiplier in self.payouts.items():
            if result_str == pattern:
                payout_multiplier = multiplier
                break
        
        # 检查任意两个相同
        if payout_multiplier == 0:
            unique_symbols = set(result)
            if len(unique_symbols) == 2:  # 有两个相同
                payout_multiplier = 2
        
        winnings = bet_amount * payout_multiplier
        net_result = winnings - bet_amount
        
        # 更新资金
        main_app.cash += winnings
        
        # 更新统计
        if winnings > bet_amount:
            main_app.user_data['slot_wins'] = main_app.user_data.get('slot_wins', 0) + 1
        main_app.user_data['slot_total_bet'] = main_app.user_data.get('slot_total_bet', 0) + bet_amount
        main_app.user_data['slot_total_win'] = main_app.user_data.get('slot_total_win', 0) + winnings
        
        # 生成结果文本
        result_text = f"""
🎰 老虎机游戏结果

╔═══════════════════════════════════════════╗
║  🎰  老虎机 - 幸运转盘  🎰               ║
╚═══════════════════════════════════════════╝

投注金额: ${bet_amount:,.2f}

转轮结果:
┌─────┬─────┬─────┐
│  {result[0]}  │  {result[1]}  │  {result[2]}  │
└─────┴─────┴─────┘

"""
        
        if payout_multiplier > 0:
            if payout_multiplier >= 30:
                result_text += f"🎉🎉🎉 超级大奖！ 🎉🎉🎉\n"
            elif payout_multiplier >= 15:
                result_text += f"🎊🎊 大奖！ 🎊🎊\n"
            elif payout_multiplier >= 5:
                result_text += f"🎁 恭喜中奖！ 🎁\n"
            else:
                result_text += f"✨ 小奖！ ✨\n"
            
            result_text += f"奖金倍数: {payout_multiplier}x\n"
            result_text += f"获得奖金: ${winnings:,.2f}\n"
            result_text += f"净收益: ${net_result:+,.2f}\n"
        else:
            result_text += f"😢 很遗憾，没有中奖\n"
            result_text += f"损失: ${bet_amount:,.2f}\n"
        
        result_text += f"\n当前余额: ${main_app.cash:,.2f}\n"
        
        # 显示统计
        total_bet = main_app.user_data.get('slot_total_bet', bet_amount)
        total_win = main_app.user_data.get('slot_total_win', winnings)
        win_rate = (main_app.user_data.get('slot_wins', 0) / max(self.usage_count, 1)) * 100
        
        result_text += f"""
📊 游戏统计:
  总投注: ${total_bet:,.2f}
  总奖金: ${total_win:,.2f}
  净盈亏: ${total_win - total_bet:+,.2f}
  中奖率: {win_rate:.1f}%
  游戏次数: {self.usage_count}

💡 继续游戏: appmarket.app slot_machine <投注额>
"""
        
        main_app.save_game_data()
        return result_text
    
    def _show_slot_menu(self, main_app):
        """显示老虎机菜单"""
        return f"""
🎰 幸运老虎机 - 游戏规则

💰 奖金表:
  💎💎💎  →  50倍  (超级大奖)
  7️⃣7️⃣7️⃣  →  30倍  (大奖)
  🔔🔔🔔  →  20倍  (铃铛奖)
  ⭐⭐⭐  →  15倍  (星星奖)
  🍇🍇🍇  →  10倍  (葡萄奖)
  🍊🍊🍊  →   8倍  (橙子奖)
  🍋🍋🍋  →   6倍  (柠檬奖)
  🍒🍒🍒  →   5倍  (樱桃奖)
  任意两同 →   2倍  (安慰奖)

📊 当前状态:
  可用资金: ${main_app.cash:,.2f}
  游戏次数: {self.usage_count}
  
🎮 开始游戏:
  appmarket.app slot_machine 100    # 投注$100
  appmarket.app slot_machine 500    # 投注$500
  appmarket.app slot_machine 1000   # 投注$1000

💡 提示: 单次最大投注$10,000，请理性游戏！
""" 