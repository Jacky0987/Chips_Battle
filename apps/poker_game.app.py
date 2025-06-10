"""
德州扑克游戏应用 - 独立应用模块
"""

import random
from datetime import datetime
from apps.base_app import BaseApp


class PokerGameApp(BaseApp):
    """德州扑克游戏应用"""
    
    def __init__(self):
        super().__init__(
            "poker_game",
            "♠️ 德州扑克",
            "与AI对手进行德州扑克游戏，测试你的牌技和运气！",
            8000,
            "游戏娱乐"
        )
        self.suits = ['♠️', '♥️', '♦️', '♣️']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    def run(self, main_app, action=None, amount=None):
        """运行扑克游戏"""
        self.usage_count += 1
        
        if action is None:
            return self._show_poker_menu(main_app)
        
        if action.lower() == 'play':
            return self._play_poker(main_app, amount)
        elif action.lower() == 'rules':
            return self._show_rules()
        else:
            return "❌ 无效操作，请使用 play 或 rules"
    
    def _play_poker(self, main_app, amount):
        """开始扑克游戏"""
        try:
            bet_amount = float(amount) if amount else 100
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
        ai_hand = [deck.pop(), deck.pop()]
        community_cards = [deck.pop() for _ in range(5)]
        
        # 评估牌力
        player_score = self._evaluate_hand(player_hand + community_cards)
        ai_score = self._evaluate_hand(ai_hand + community_cards)
        
        # 确定胜负
        if player_score > ai_score:
            winnings = bet_amount * 2
            result = "胜利"
            main_app.user_data['poker_wins'] = main_app.user_data.get('poker_wins', 0) + 1
        elif player_score < ai_score:
            winnings = 0
            result = "失败"
        else:
            winnings = bet_amount
            result = "平局"
        
        # 更新资金和统计
        main_app.cash += winnings
        net_result = winnings - bet_amount
        
        main_app.user_data['poker_total_bet'] = main_app.user_data.get('poker_total_bet', 0) + bet_amount
        main_app.user_data['poker_total_win'] = main_app.user_data.get('poker_total_win', 0) + winnings
        
        result_text = f"""
♠️ 德州扑克游戏结果

╔═══════════════════════════════════════════╗
║  ♠️  德州扑克 - 牌技对决  ♠️             ║
╚═══════════════════════════════════════════╝

投注金额: ${bet_amount:,.2f}

🃏 您的手牌: {' '.join(player_hand)}
🤖 AI手牌: {' '.join(ai_hand)}
🃏 公共牌: {' '.join(community_cards)}

📊 牌力评估:
  您的牌力: {self._hand_name(player_score)} ({player_score})
  AI牌力: {self._hand_name(ai_score)} ({ai_score})

🏆 游戏结果: {result}
"""
        
        if winnings > bet_amount:
            result_text += f"🎉 恭喜获胜！\n"
            result_text += f"获得奖金: ${winnings:,.2f}\n"
            result_text += f"净收益: ${net_result:+,.2f}\n"
        elif winnings == bet_amount:
            result_text += f"🤝 平局，返还投注\n"
        else:
            result_text += f"😢 遗憾失败\n"
            result_text += f"损失: ${bet_amount:,.2f}\n"
        
        result_text += f"\n当前余额: ${main_app.cash:,.2f}\n"
        
        # 显示统计
        total_bet = main_app.user_data.get('poker_total_bet', bet_amount)
        total_win = main_app.user_data.get('poker_total_win', winnings)
        win_rate = (main_app.user_data.get('poker_wins', 0) / max(self.usage_count, 1)) * 100
        
        result_text += f"""
📊 游戏统计:
  总投注: ${total_bet:,.2f}
  总奖金: ${total_win:,.2f}
  净盈亏: ${total_win - total_bet:+,.2f}
  胜率: {win_rate:.1f}%
  游戏次数: {self.usage_count}

💡 继续游戏: appmarket.app poker_game play <投注额>
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
    
    def _evaluate_hand(self, cards):
        """评估扑克手牌（简化版本）"""
        # 提取数字和花色
        ranks = []
        suits = []
        for card in cards:
            if card[:-2] == '10':
                rank = '10'
                suit = card[-2:]
            else:
                rank = card[:-2]
                suit = card[-2:]
            ranks.append(rank)
            suits.append(suit)
        
        # 转换为数值进行比较
        rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        values = [rank_values[rank] for rank in ranks]
        values.sort(reverse=True)
        
        # 统计相同牌的数量
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        counts = sorted(rank_counts.values(), reverse=True)
        
        # 检查同花
        is_flush = len(set(suits)) <= 4 and suits.count(suits[0]) >= 5
        
        # 检查顺子（简化）
        is_straight = False
        for i in range(len(values) - 4):
            if values[i] - values[i+4] == 4:
                is_straight = True
                break
        
        # 评分系统
        if is_straight and is_flush:
            return 8000 + max(values)  # 同花顺
        elif counts[0] == 4:
            return 7000 + max(values)  # 四条
        elif counts[0] == 3 and counts[1] == 2:
            return 6000 + max(values)  # 满堂红
        elif is_flush:
            return 5000 + max(values)  # 同花
        elif is_straight:
            return 4000 + max(values)  # 顺子
        elif counts[0] == 3:
            return 3000 + max(values)  # 三条
        elif counts[0] == 2 and counts[1] == 2:
            return 2000 + max(values)  # 两对
        elif counts[0] == 2:
            return 1000 + max(values)  # 一对
        else:
            return max(values)  # 高牌
    
    def _hand_name(self, score):
        """获取牌型名称"""
        if score >= 8000:
            return "同花顺"
        elif score >= 7000:
            return "四条"
        elif score >= 6000:
            return "满堂红"
        elif score >= 5000:
            return "同花"
        elif score >= 4000:
            return "顺子"
        elif score >= 3000:
            return "三条"
        elif score >= 2000:
            return "两对"
        elif score >= 1000:
            return "一对"
        else:
            return "高牌"
    
    def _show_poker_menu(self, main_app):
        """显示扑克游戏菜单"""
        return f"""
♠️ 德州扑克游戏

当前余额: ${main_app.cash:,.2f}

🎮 游戏选项:
  appmarket.app poker_game play <投注额>  # 开始游戏
  appmarket.app poker_game rules         # 查看规则

💰 投注建议:
  小额试玩: $50-200
  标准游戏: $500-1000  
  高额桌: $2000-5000

📊 历史战绩:
  胜利次数: {main_app.user_data.get('poker_wins', 0)}
  总投注: ${main_app.user_data.get('poker_total_bet', 0):,.2f}
  总奖金: ${main_app.user_data.get('poker_total_win', 0):,.2f}
  游戏次数: {self.usage_count}

💡 提示: 德州扑克结合技巧和运气，适度游戏，理性投注！
"""
    
    def _show_rules(self):
        """显示游戏规则"""
        return """
♠️ 德州扑克规则说明

🃏 基本玩法:
1. 每位玩家发2张底牌
2. 桌面发5张公共牌
3. 从7张牌中选出最佳5张组合
4. 牌型大小决定胜负

🏆 牌型等级 (从高到低):
1. 同花顺 - 连续的同花色五张牌
2. 四条 - 四张相同点数的牌
3. 满堂红 - 三张+一对
4. 同花 - 五张同花色的牌
5. 顺子 - 连续的五张牌
6. 三条 - 三张相同点数的牌
7. 两对 - 两个对子
8. 一对 - 一个对子
9. 高牌 - 最大的单张牌

💰 赔率说明:
- 获胜: 2倍投注额
- 平局: 返还投注额
- 失败: 失去投注额

🎯 策略提示:
- 观察公共牌组合可能性
- 合理控制投注额度
- 运气与技巧并重

💡 投注限制: 单次最高$5,000
""" 