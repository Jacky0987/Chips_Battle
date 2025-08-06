"""
21点(Blackjack)游戏应用
"""

import random
from datetime import datetime
from apps.base_app import BaseApp


class BlackjackApp(BaseApp):
    """21点游戏应用"""
    
    def __init__(self):
        super().__init__(
            "blackjack",
            "21点大师",
            "经典21点游戏，与庄家比拼牌技，目标是接近但不超过21点。",
            6000,
            "游戏娱乐",
            "1.0",
            "🃏"
        )
        self.suits = ['♠️', '♥️', '♦️', '♣️']
        self.ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    def run(self, main_app, action=None, bet_amount=None):
        """运行21点游戏"""
        self.update_usage()
        
        if action is None:
            return self._show_blackjack_menu(main_app)
        
        if action.lower() == 'play':
            return self._play_blackjack(main_app, bet_amount)
        elif action.lower() == 'rules':
            return self._show_rules()
        else:
            return "❌ 无效操作，请使用 play <投注额> 或 rules"
    
    def _play_blackjack(self, main_app, bet_amount):
        """开始21点游戏"""
        try:
            bet_amount = float(bet_amount) if bet_amount else 100
            if bet_amount <= 0:
                return "❌ 投注金额必须大于0"
            if bet_amount > main_app.cash:
                return "❌ 资金不足"
            if bet_amount > 5000:
                return "❌ 单次投注金额不能超过$5,000"
        except (ValueError, TypeError):
            return "❌ 无效的投注金额"
        
        # 扣除投注金额
        main_app.cash -= bet_amount
        
        # 创建牌组并发牌
        deck = self._create_deck()
        random.shuffle(deck)
        
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        # 计算初始点数
        player_value = self._calculate_hand_value(player_hand)
        dealer_value = self._calculate_hand_value(dealer_hand)
        
        # 检查自然21点
        player_blackjack = player_value == 21
        dealer_blackjack = dealer_value == 21
        
        result_text = f"""
🃏 21点游戏

╔═══════════════════════════════════════════╗
║  🃏  21点大师 - 经典对决  🃏             ║
╚═══════════════════════════════════════════╝

投注金额: ${bet_amount:,.2f}

🎴 您的手牌: {' '.join(player_hand)} (点数: {player_value})
🎭 庄家手牌: {dealer_hand[0]} ? (明牌: {self._card_value(dealer_hand[0])})

"""
        
        # 游戏逻辑
        if player_blackjack and dealer_blackjack:
            # 双方都是21点，平局
            winnings = bet_amount
            result = "平局"
            result_text += "🤝 双方都是21点！平局！\n"
        elif player_blackjack:
            # 玩家21点，赢1.5倍
            winnings = bet_amount * 2.5
            result = "胜利"
            result_text += "🎉 恭喜！自然21点！\n"
        elif dealer_blackjack:
            # 庄家21点，玩家输
            winnings = 0
            result = "失败"
            result_text += "😢 庄家自然21点，您败了\n"
        else:
            # 正常游戏流程 - 简化版本，自动决策
            # 玩家策略：小于17点继续要牌
            while player_value < 17 and player_value < 21:
                new_card = deck.pop()
                player_hand.append(new_card)
                player_value = self._calculate_hand_value(player_hand)
                result_text += f"🎴 您要了一张牌: {new_card} (总点数: {player_value})\n"
            
            # 庄家翻牌
            result_text += f"🎭 庄家翻牌: {' '.join(dealer_hand)} (点数: {dealer_value})\n"
            
            # 庄家策略：小于17点必须要牌
            while dealer_value < 17:
                new_card = deck.pop()
                dealer_hand.append(new_card)
                dealer_value = self._calculate_hand_value(dealer_hand)
                result_text += f"🎭 庄家要牌: {new_card} (总点数: {dealer_value})\n"
            
            # 判断结果
            if player_value > 21:
                winnings = 0
                result = "失败"
                result_text += "💥 您爆牌了！\n"
            elif dealer_value > 21:
                winnings = bet_amount * 2
                result = "胜利"
                result_text += "🎉 庄家爆牌！您赢了！\n"
            elif player_value > dealer_value:
                winnings = bet_amount * 2
                result = "胜利"
                result_text += "🏆 您的点数更高！胜利！\n"
            elif player_value < dealer_value:
                winnings = 0
                result = "失败"
                result_text += "😔 庄家点数更高，您败了\n"
            else:
                winnings = bet_amount
                result = "平局"
                result_text += "🤝 点数相同，平局！\n"
        
        # 最终结果显示
        result_text += f"\n🎴 最终手牌:\n"
        result_text += f"  您: {' '.join(player_hand)} (点数: {player_value})\n"
        result_text += f"  庄家: {' '.join(dealer_hand)} (点数: {dealer_value})\n\n"
        
        # 更新资金和统计
        main_app.cash += winnings
        net_result = winnings - bet_amount
        
        if result == "胜利":
            main_app.user_data['blackjack_wins'] = main_app.user_data.get('blackjack_wins', 0) + 1
        main_app.user_data['blackjack_total_bet'] = main_app.user_data.get('blackjack_total_bet', 0) + bet_amount
        main_app.user_data['blackjack_total_win'] = main_app.user_data.get('blackjack_total_win', 0) + winnings
        
        if winnings > bet_amount:
            result_text += f"🎉 游戏结果: {result}\n"
            result_text += f"获得奖金: ${winnings:,.2f}\n"
            result_text += f"净收益: ${net_result:+,.2f}\n"
        elif winnings == bet_amount:
            result_text += f"🤝 游戏结果: {result}\n"
            result_text += f"返还投注: ${winnings:,.2f}\n"
        else:
            result_text += f"😢 游戏结果: {result}\n"
            result_text += f"损失: ${bet_amount:,.2f}\n"
        
        result_text += f"\n当前余额: ${main_app.cash:,.2f}\n"
        
        # 显示统计
        total_bet = main_app.user_data.get('blackjack_total_bet', bet_amount)
        total_win = main_app.user_data.get('blackjack_total_win', winnings)
        win_rate = (main_app.user_data.get('blackjack_wins', 0) / max(self.usage_count, 1)) * 100
        
        result_text += f"""
📊 游戏统计:
  总投注: ${total_bet:,.2f}
  总奖金: ${total_win:,.2f}
  净盈亏: ${total_win - total_bet:+,.2f}
  胜率: {win_rate:.1f}%
  游戏次数: {self.usage_count}

💡 继续游戏: appmarket.app blackjack play <投注额>
"""
        
        main_app.save_game_data()
        return result_text
    
    def _create_deck(self):
        """创建标准扑克牌组"""
        deck = []
        for suit in self.suits:
            for rank in self.ranks:
                deck.append(f"{rank}{suit}")
        return deck
    
    def _card_value(self, card):
        """获取单张牌的点数"""
        rank = card[:-2] if len(card) > 2 else card[:-1]
        if rank in ['J', 'Q', 'K']:
            return 10
        elif rank == 'A':
            return 11  # A的值会在计算总点数时调整
        else:
            return int(rank)
    
    def _calculate_hand_value(self, hand):
        """计算手牌总点数"""
        total = 0
        aces = 0
        
        for card in hand:
            rank = card[:-2] if len(card) > 2 else card[:-1]
            if rank in ['J', 'Q', 'K']:
                total += 10
            elif rank == 'A':
                aces += 1
                total += 11
            else:
                total += int(rank)
        
        # 处理A的点数
        while total > 21 and aces > 0:
            total -= 10  # 将A从11变为1
            aces -= 1
        
        return total
    
    def _show_blackjack_menu(self, main_app):
        """显示21点游戏菜单"""
        return f"""
🃏 21点大师 - 游戏介绍

🎮 游戏目标:
  • 手牌点数尽可能接近21点，但不能超过
  • 点数比庄家高且不爆牌即获胜
  • 自然21点(前两张牌)可获得1.5倍奖金

🎴 牌点规则:
  • A = 1点或11点(自动选择最优)
  • K, Q, J = 10点
  • 其他牌 = 面值点数

🏆 获胜条件:
  • 自然21点 → 2.5倍奖金
  • 普通获胜 → 2倍奖金
  • 平局 → 返还投注
  • 爆牌/败北 → 失去投注

📊 当前状态:
  可用资金: ${main_app.cash:,.2f}
  游戏次数: {self.usage_count}
  胜率: {(main_app.user_data.get('blackjack_wins', 0) / max(self.usage_count, 1)) * 100:.1f}%

🎮 开始游戏:
  appmarket.app blackjack play 100    # 投注$100开始游戏
  appmarket.app blackjack play 500    # 投注$500开始游戏
  appmarket.app blackjack rules       # 查看详细规则

💡 提示: 
  • 单次最大投注$5,000
  • 策略：16点以下建议要牌，17点以上停牌
  • 观察庄家明牌制定策略
"""
    
    def _show_rules(self):
        """显示详细规则"""
        return """
🃏 21点详细规则

🎯 基本玩法:
  1. 玩家和庄家各发2张牌
  2. 庄家一张明牌，一张暗牌
  3. 玩家根据手牌决定是否要牌
  4. 目标是接近但不超过21点

🎴 牌值说明:
  • A: 可算作1点或11点
  • K, Q, J: 均为10点
  • 2-10: 按面值计算

🏆 获胜规则:
  • 自然21点(前两张牌): 2.5倍赔率
  • 普通胜利: 2倍赔率
  • 平局: 返还投注
  • 爆牌(超过21点): 立即失败

🎯 庄家规则:
  • 16点或以下必须要牌
  • 17点或以上必须停牌
  • 软17(A+6)也必须停牌

💡 基本策略:
  • 12-16点: 庄家2-6停牌，7-A要牌
  • 17-21点: 总是停牌
  • 软手牌(有A): 更灵活的策略
  • 对子: 建议分牌(简化版不支持)

⚠️ 注意事项:
  • 本版本为简化版21点
  • 不支持分牌、双倍下注等高级规则
  • 系统会自动执行最优策略
""" 