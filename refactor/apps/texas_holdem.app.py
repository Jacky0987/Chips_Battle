"""
德州扑克游戏应用
"""

import random
from datetime import datetime
from apps.base_app import BaseApp


class TexasHoldemApp(BaseApp):
    """德州扑克游戏应用"""
    
    def __init__(self):
        super().__init__(
            "texas_holdem",
            "德州扑克王",
            "经典德州扑克游戏，与AI对手进行激烈的牌桌对决！",
            10000,
            "游戏娱乐",
            "1.0",
            "♠️"
        )
        self.suits = ['♠️', '♥️', '♦️', '♣️']
        self.ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                           '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    def run(self, main_app, action=None, bet_amount=None):
        """运行德州扑克游戏"""
        self.update_usage()
        
        if action is None:
            return self._show_poker_menu(main_app)
        
        if action.lower() == 'play':
            return self._play_poker(main_app, bet_amount)
        elif action.lower() == 'tournament':
            return self._play_tournament(main_app, bet_amount)
        elif action.lower() == 'rules':
            return self._show_rules()
        else:
            return "❌ 无效操作，请使用 play <投注额>、tournament <费用> 或 rules"
    
    def _play_poker(self, main_app, bet_amount):
        """开始德州扑克游戏"""
        try:
            bet_amount = float(bet_amount) if bet_amount else 200
            if bet_amount <= 0:
                return "❌ 投注金额必须大于0"
            if bet_amount > main_app.cash:
                return "❌ 资金不足"
            if bet_amount > 8000:
                return "❌ 单次投注金额不能超过$8,000"
        except (ValueError, TypeError):
            return "❌ 无效的投注金额"
        
        # 扣除投注金额
        main_app.cash -= bet_amount
        
        # 创建牌组并发牌
        deck = self._create_deck()
        random.shuffle(deck)
        
        # 发底牌
        player_hand = [deck.pop(), deck.pop()]
        ai_hand = [deck.pop(), deck.pop()]
        
        # 发公共牌
        flop = [deck.pop(), deck.pop(), deck.pop()]  # 翻牌
        turn = deck.pop()  # 转牌
        river = deck.pop()  # 河牌
        
        community_cards = flop + [turn, river]
        
        # 评估牌力
        player_best = self._get_best_hand(player_hand + community_cards)
        ai_best = self._get_best_hand(ai_hand + community_cards)
        
        # 比较牌力
        player_score = self._evaluate_hand(player_best)
        ai_score = self._evaluate_hand(ai_best)
        
        result_text = f"""
♠️ 德州扑克游戏

╔═══════════════════════════════════════════╗
║  ♠️  德州扑克王 - 牌桌对决  ♠️           ║
╚═══════════════════════════════════════════╝

投注金额: ${bet_amount:,.2f}

🃏 您的底牌: {' '.join(player_hand)}
🤖 AI底牌: ? ? (暂时隐藏)

🃏 公共牌发牌过程:
  翻牌(Flop): {' '.join(flop)}
  转牌(Turn): {turn}
  河牌(River): {river}

🃏 最终公共牌: {' '.join(community_cards)}

🎴 最佳手牌:
  您的最佳牌型: {' '.join(player_best)}
  牌型: {self._hand_name(player_score)} ({player_score})
  
🤖 AI最佳牌型: {' '.join(ai_best)}
  牌型: {self._hand_name(ai_score)} ({ai_score})

🃏 AI底牌揭示: {' '.join(ai_hand)}

"""
        
        # 确定胜负
        if player_score > ai_score:
            winnings = bet_amount * 2.2  # 德州扑克胜利奖金稍高
            result = "胜利"
            result_text += "🏆 恭喜获胜！您的牌型更强！\n"
            main_app.user_data['poker_wins'] = main_app.user_data.get('poker_wins', 0) + 1
        elif player_score < ai_score:
            winnings = 0
            result = "失败"
            result_text += "😔 遗憾败北，AI的牌型更强\n"
        else:
            winnings = bet_amount
            result = "平局"
            result_text += "🤝 平局！双方牌型相同\n"
        
        # 更新资金和统计
        main_app.cash += winnings
        net_result = winnings - bet_amount
        
        main_app.user_data['poker_total_bet'] = main_app.user_data.get('poker_total_bet', 0) + bet_amount
        main_app.user_data['poker_total_win'] = main_app.user_data.get('poker_total_win', 0) + winnings
        
        if winnings > bet_amount:
            result_text += f"获得奖金: ${winnings:,.2f}\n"
            result_text += f"净收益: ${net_result:+,.2f}\n"
        elif winnings == bet_amount:
            result_text += f"返还投注: ${winnings:,.2f}\n"
        else:
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

💡 继续游戏: appmarket.app texas_holdem play <投注额>
"""
        
        main_app.save_game_data()
        return result_text
    
    def _play_tournament(self, main_app, entry_fee):
        """锦标赛模式"""
        try:
            entry_fee = float(entry_fee) if entry_fee else 500
            if entry_fee < 100:
                return "❌ 锦标赛报名费最少$100"
            if entry_fee > main_app.cash:
                return "❌ 资金不足"
        except (ValueError, TypeError):
            return "❌ 无效的报名费"
        
        main_app.cash -= entry_fee
        
        # 模拟锦标赛
        rounds = ['第一轮', '第二轮', '第三轮', '决赛']
        prize_pool = entry_fee * 10  # 奖池
        
        result_text = f"""
🏆 德州扑克锦标赛

报名费: ${entry_fee:,.2f}
奖池: ${prize_pool:,.2f}
参赛人数: 10人

锦标赛进程:
"""
        
        for i, round_name in enumerate(rounds):
            success_rate = 0.6 - (i * 0.1)  # 每轮难度递增
            if random.random() < success_rate:
                result_text += f"✅ {round_name}: 胜利晋级\n"
            else:
                result_text += f"❌ {round_name}: 淘汰出局\n"
                # 根据淘汰轮次给予奖金
                if i == 0:
                    winnings = 0
                elif i == 1:
                    winnings = entry_fee * 0.5
                elif i == 2:
                    winnings = entry_fee * 1.5
                else:
                    winnings = entry_fee * 3
                
                main_app.cash += winnings
                result_text += f"\n排名奖金: ${winnings:,.2f}\n"
                result_text += f"当前余额: ${main_app.cash:,.2f}\n"
                return result_text
        
        # 如果全胜
        winnings = prize_pool * 0.4  # 冠军奖金
        main_app.cash += winnings
        main_app.user_data['tournament_wins'] = main_app.user_data.get('tournament_wins', 0) + 1
        
        result_text += f"""
🎉🎉🎉 恭喜夺冠！🎉🎉🎉

冠军奖金: ${winnings:,.2f}
净收益: ${winnings - entry_fee:+,.2f}
当前余额: ${main_app.cash:,.2f}

锦标赛冠军次数: {main_app.user_data.get('tournament_wins', 1)}
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
    
    def _get_best_hand(self, cards):
        """从7张牌中选出最佳的5张牌"""
        from itertools import combinations
        
        if len(cards) < 5:
            return cards
        
        best_hand = None
        best_score = -1
        
        # 尝试所有5张牌的组合
        for combo in combinations(cards, 5):
            score = self._evaluate_hand(list(combo))
            if score > best_score:
                best_score = score
                best_hand = list(combo)
        
        return best_hand
    
    def _evaluate_hand(self, hand):
        """评估5张牌的牌力"""
        if len(hand) != 5:
            return 0
        
        # 提取数字和花色
        ranks = []
        suits = []
        for card in hand:
            if card.startswith('10'):
                rank = '10'
                suit = card[2:]
            else:
                rank = card[:-2]
                suit = card[-2:]
            ranks.append(rank)
            suits.append(suit)
        
        # 转换为数值
        values = [self.rank_values[rank] for rank in ranks]
        values.sort(reverse=True)
        
        # 统计相同牌的数量
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        counts = sorted(rank_counts.values(), reverse=True)
        
        # 检查同花
        is_flush = len(set(suits)) == 1
        
        # 检查顺子
        is_straight = self._is_straight(values)
        
        # 特殊处理A-2-3-4-5顺子
        if values == [14, 5, 4, 3, 2]:
            is_straight = True
            values = [5, 4, 3, 2, 1]  # A当作1
        
        # 评分系统
        if is_straight and is_flush:
            if values[0] == 14:  # 皇家同花顺
                return 90000 + sum(values)
            return 80000 + sum(values)  # 同花顺
        elif counts[0] == 4:
            return 70000 + max(values)  # 四条
        elif counts[0] == 3 and counts[1] == 2:
            return 60000 + max(values)  # 满堂红
        elif is_flush:
            return 50000 + sum(values)  # 同花
        elif is_straight:
            return 40000 + sum(values)  # 顺子
        elif counts[0] == 3:
            return 30000 + max(values)  # 三条
        elif counts[0] == 2 and counts[1] == 2:
            return 20000 + sum(values)  # 两对
        elif counts[0] == 2:
            return 10000 + max(values)  # 一对
        else:
            return sum(values)  # 高牌
    
    def _is_straight(self, values):
        """检查是否为顺子"""
        if len(values) != 5:
            return False
        
        for i in range(4):
            if values[i] - values[i+1] != 1:
                return False
        return True
    
    def _hand_name(self, score):
        """获取牌型名称"""
        if score >= 90000:
            return "皇家同花顺"
        elif score >= 80000:
            return "同花顺"
        elif score >= 70000:
            return "四条"
        elif score >= 60000:
            return "满堂红"
        elif score >= 50000:
            return "同花"
        elif score >= 40000:
            return "顺子"
        elif score >= 30000:
            return "三条"
        elif score >= 20000:
            return "两对"
        elif score >= 10000:
            return "一对"
        else:
            return "高牌"
    
    def _show_poker_menu(self, main_app):
        """显示德州扑克菜单"""
        return f"""
♠️ 德州扑克王 - 游戏介绍

🎮 游戏模式:
  • 经典对战: 与AI一对一对决
  • 锦标赛: 多轮淘汰赛，奖池丰厚

🃏 游戏规则:
  • 每人发2张底牌
  • 5张公共牌(翻牌、转牌、河牌)
  • 用7张牌组成最佳5张牌型
  • 牌型大小决定胜负

🏆 牌型排行(从大到小):
  1. 皇家同花顺 - 10-J-Q-K-A同花色
  2. 同花顺 - 5张连续同花色
  3. 四条 - 4张相同数字
  4. 满堂红 - 三条+一对
  5. 同花 - 5张同花色
  6. 顺子 - 5张连续数字
  7. 三条 - 3张相同数字
  8. 两对 - 两个对子
  9. 一对 - 一个对子
  10. 高牌 - 单张最大

📊 当前状态:
  可用资金: ${main_app.cash:,.2f}
  游戏次数: {self.usage_count}
  胜率: {(main_app.user_data.get('poker_wins', 0) / max(self.usage_count, 1)) * 100:.1f}%
  锦标赛冠军: {main_app.user_data.get('tournament_wins', 0)}次

🎮 开始游戏:
  appmarket.app texas_holdem play 200       # 经典对战，投注$200
  appmarket.app texas_holdem tournament 500 # 锦标赛，报名费$500
  appmarket.app texas_holdem rules          # 查看详细规则

💡 提示: 
  • 经典对战：单次最大投注$8,000
  • 锦标赛：报名费最少$100，奖池为报名费10倍
  • 掌握概率和心理战是制胜关键
"""
    
    def _show_rules(self):
        """显示详细规则"""
        return """
♠️ 德州扑克详细规则

🃏 基本玩法:
  1. 每位玩家发2张底牌(手牌)
  2. 发5张公共牌，分三轮:
     - 翻牌(Flop): 3张
     - 转牌(Turn): 1张
     - 河牌(River): 1张
  3. 用7张牌组成最佳5张牌型
  4. 比较牌型大小决定胜负

🏆 牌型说明:
  • 皇家同花顺: 10-J-Q-K-A同花色(最强)
  • 同花顺: 5张连续同花色
  • 四条: 4张相同数字+1张散牌
  • 满堂红: 3张相同+2张相同
  • 同花: 5张同花色(不连续)
  • 顺子: 5张连续数字(不同花色)
  • 三条: 3张相同数字+2张散牌
  • 两对: 2个对子+1张散牌
  • 一对: 1个对子+3张散牌
  • 高牌: 没有任何牌型

🎯 锦标赛规则:
  • 10人参赛，单淘汰制
  • 4轮比赛：初赛、复赛、半决赛、决赛
  • 根据淘汰轮次获得不同奖金
  • 冠军获得奖池40%

💡 策略提示:
  • 起手牌很重要：大对子、同花连牌较强
  • 位置影响策略：后位更有信息优势
  • 观察公共牌：计算自己完成牌型的概率
  • 资金管理：不要把所有资金压在一局

⚠️ 注意事项:
  • 本版本为简化版德州扑克
  • 无下注轮，直接比较最终牌型
  • AI使用基础策略，适合练习
""" 