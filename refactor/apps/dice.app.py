"""
🎲 幸运骰子游戏应用
掷骰子猜大小，简单刺激的运气游戏
"""

import random
from datetime import datetime
from apps.base_app import BaseApp


class DiceGameApp(BaseApp):
    """骰子游戏应用"""
    
    def __init__(self):
        super().__init__(
            "dice_game",
            "🎲 幸运骰子",
            "掷骰子猜大小，简单刺激的运气游戏。支持多种玩法。",
            3000,
            "游戏娱乐"
        )
    
    def run(self, main_app, *args):
        """运行骰子游戏"""
        self.usage_count += 1
        
        if len(args) < 2:
            return self._show_dice_menu(main_app)
        
        try:
            bet_type = args[0].lower()
            bet_amount = float(args[1])
            
            if bet_amount <= 0:
                return "❌ 投注金额必须大于0"
            if bet_amount > main_app.cash:
                return "❌ 资金不足"
            if bet_amount > 5000:
                return "❌ 单次投注不能超过$5,000"
            
            # 掷骰子
            dice1 = random.randint(1, 6)
            dice2 = random.randint(1, 6)
            total = dice1 + dice2
            
            result_text = f"""
🎲 幸运骰子游戏结果

🎯 您的选择: {bet_type.upper()}
💰 投注金额: ${bet_amount:,.2f}

🎲 掷骰结果:
  骰子1: {dice1} 
  骰子2: {dice2}
  总点数: {total}
  大小: {'大' if total >= 7 else '小'}
  奇偶: {'奇' if total % 2 == 1 else '偶'}

"""
            
            win = False
            multiplier = 1.0
            
            if bet_type == "big" and total >= 7:
                win = True
                multiplier = 1.8
            elif bet_type == "small" and total < 7:
                win = True
                multiplier = 1.8
            elif bet_type == "odd" and total % 2 == 1:
                win = True
                multiplier = 1.9
            elif bet_type == "even" and total % 2 == 0:
                win = True
                multiplier = 1.9
            elif bet_type == "double" and dice1 == dice2:
                win = True
                multiplier = 5.0
            elif bet_type.isdigit() and int(bet_type) == total:
                win = True
                multiplier = 8.0
            
            if win:
                winnings = bet_amount * multiplier
                profit = winnings - bet_amount
                main_app.cash += profit
                
                result_text += f"""
🎉 恭喜您获胜！

💰 投注倍率: {multiplier}x
💵 获得奖金: ${winnings:,.2f}
📈 净收益: ${profit:,.2f}
💼 当前余额: ${main_app.cash:,.2f}
"""
                
                # 记录交易
                transaction = {
                    'type': 'DICE_WIN',
                    'symbol': 'DICE',
                    'quantity': 1,
                    'price': bet_amount,
                    'total': profit,
                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'details': f"骰子游戏获胜 ({dice1},{dice2}) {bet_type}"
                }
                main_app.transaction_history.append(transaction)
                
            else:
                main_app.cash -= bet_amount
                
                result_text += f"""
😞 很遗憾，您输了

💸 损失金额: ${bet_amount:,.2f}
💼 剩余余额: ${main_app.cash:,.2f}
"""
                
                # 记录交易
                transaction = {
                    'type': 'DICE_LOSS',
                    'symbol': 'DICE',
                    'quantity': 1,
                    'price': bet_amount,
                    'total': -bet_amount,
                    'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'details': f"骰子游戏失败 ({dice1},{dice2}) {bet_type}"
                }
                main_app.transaction_history.append(transaction)
            
            result_text += f"""
🎮 继续游戏:
  appmarket.app dice_game big 100    # 猜大，投注$100
  appmarket.app dice_game small 50   # 猜小，投注$50
  appmarket.app dice_game 7 200      # 猜总点数7，投注$200
"""
            
            return result_text
            
        except ValueError:
            return "❌ 无效的投注金额"
        except Exception as e:
            return f"❌ 游戏出错: {str(e)}"
    
    def _show_dice_menu(self, main_app):
        """显示骰子游戏菜单"""
        return f"""
🎲 幸运骰子游戏

💰 当前余额: ${main_app.cash:,.2f}

🎯 游戏规则:
  • 掷两个骰子，根据结果判断输赢
  • 总点数7及以上为"大"，6及以下为"小"
  • 可以猜大小、奇偶、对子或精确点数

💸 投注选项和赔率:
  • big/small (大/小): 1.8倍 - 猜总点数大于等于7或小于7
  • odd/even (奇/偶): 1.9倍 - 猜总点数是奇数或偶数  
  • double (对子): 5.0倍 - 两个骰子点数相同
  • 精确点数 (2-12): 8.0倍 - 猜中确切的总点数

🎮 游戏命令:
  appmarket.app dice_game <选择> <金额>

📖 示例:
  appmarket.app dice_game big 100     # 猜大，投注$100
  appmarket.app dice_game small 50    # 猜小，投注$50
  appmarket.app dice_game odd 75      # 猜奇数，投注$75
  appmarket.app dice_game double 200  # 猜对子，投注$200
  appmarket.app dice_game 7 150       # 猜总点数7，投注$150

⚠️ 注意事项:
  • 单次投注限额: $5,000
  • 请合理控制投注金额
  • 赌博有风险，娱乐需谨慎

💡 小贴士: 
  对子和精确点数虽然赔率高，但中奖概率较低
  大小和奇偶相对稳妥，适合保守玩家
""" 