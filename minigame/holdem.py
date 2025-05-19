"""
德州扑克游戏实现
"""

import random
from typing import Dict, Any, List, Tuple, Optional
import sys
import os
from collections import Counter

# 添加项目根目录到系统路径，以便导入models模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.minigame import MiniGame, Card, Deck


class PokerHand:
    """扑克牌手牌评估类"""
    
    HAND_RANKS = {
        "高牌": 1,
        "一对": 2,
        "两对": 3,
        "三条": 4,
        "顺子": 5,
        "同花": 6,
        "葫芦": 7,
        "四条": 8,
        "同花顺": 9,
        "皇家同花顺": 10
    }
    
    @staticmethod
    def evaluate_hand(cards: List[Card]) -> Tuple[str, List[int]]:
        """
        评估手牌
        
        Args:
            cards: 手牌列表（5-7张牌）
            
        Returns:
            Tuple[str, List[int]]: (牌型名称, 用于比较大小的值列表)
        """
        if len(cards) < 5:
            raise ValueError("评估手牌需要至少5张牌")
            
        # 如果有超过5张牌，需要找出最佳的5张牌组合
        if len(cards) > 5:
            return PokerHand._find_best_hand(cards)
            
        # 获取牌的点数和花色
        values = [card.get_poker_value() for card in cards]
        suits = [card.suit for card in cards]
        
        # 检查是否同花
        is_flush = len(set(suits)) == 1
        
        # 检查是否顺子
        sorted_values = sorted(values)
        is_straight = (len(set(sorted_values)) == 5 and 
                      max(sorted_values) - min(sorted_values) == 4)
        
        # 特殊情况：A-5-4-3-2顺子
        if sorted(values) == [2, 3, 4, 5, 14]:
            is_straight = True
            # 将A视为1而非14
            sorted_values = [1, 2, 3, 4, 5]
            
        # 计算每个点数出现的次数
        value_counts = Counter(values)
        
        # 判断牌型
        if is_straight and is_flush:
            if max(sorted_values) == 14:  # 如果最大的牌是A
                return "皇家同花顺", [10]
            return "同花顺", [9, max(sorted_values)]
            
        if 4 in value_counts.values():
            four_kind = [v for v, count in value_counts.items() if count == 4][0]
            kicker = [v for v, count in value_counts.items() if count == 1][0]
            return "四条", [8, four_kind, kicker]
            
        if 3 in value_counts.values() and 2 in value_counts.values():
            three_kind = [v for v, count in value_counts.items() if count == 3][0]
            pair = [v for v, count in value_counts.items() if count == 2][0]
            return "葫芦", [7, three_kind, pair]
            
        if is_flush:
            return "同花", [6] + sorted(values, reverse=True)
            
        if is_straight:
            return "顺子", [5, max(sorted_values)]
            
        if 3 in value_counts.values():
            three_kind = [v for v, count in value_counts.items() if count == 3][0]
            kickers = sorted([v for v, count in value_counts.items() if count == 1], reverse=True)
            return "三条", [4, three_kind] + kickers
            
        if list(value_counts.values()).count(2) == 2:
            pairs = sorted([v for v, count in value_counts.items() if count == 2], reverse=True)
            kicker = [v for v, count in value_counts.items() if count == 1][0]
            return "两对", [3] + pairs + [kicker]
            
        if 2 in value_counts.values():
            pair = [v for v, count in value_counts.items() if count == 2][0]
            kickers = sorted([v for v, count in value_counts.items() if count == 1], reverse=True)
            return "一对", [2, pair] + kickers
            
        return "高牌", [1] + sorted(values, reverse=True)
        
    @staticmethod
    def _find_best_hand(cards: List[Card]) -> Tuple[str, List[int]]:
        """
        从多于5张的牌中找出最佳的5张牌组合
        
        Args:
            cards: 手牌列表（6-7张牌）
            
        Returns:
            Tuple[str, List[int]]: (牌型名称, 用于比较大小的值列表)
        """
        import itertools
        
        best_rank = ("高牌", [0])
        
        # 生成所有可能的5张牌组合
        for combo in itertools.combinations(cards, 5):
            rank = PokerHand.evaluate_hand(list(combo))
            
            # 比较牌型
            if PokerHand.HAND_RANKS[rank[0]] > PokerHand.HAND_RANKS[best_rank[0]]:
                best_rank = rank
            elif PokerHand.HAND_RANKS[rank[0]] == PokerHand.HAND_RANKS[best_rank[0]]:
                # 如果牌型相同，比较牌值
                if rank[1] > best_rank[1]:
                    best_rank = rank
                    
        return best_rank


class TexasHoldem(MiniGame):
    """德州扑克游戏实现"""
    
    STAGES = ["preflop", "flop", "turn", "river", "showdown"]
    
    def __init__(self, min_bet: float = 10.0, max_bet: float = 1000.0, num_ai_players: int = 3):
        """
        初始化德州扑克游戏
        
        Args:
            min_bet: 最小下注金额
            max_bet: 最大下注金额
            num_ai_players: AI玩家数量
        """
        super().__init__(
            name="德州扑克",
            description="最流行的扑克游戏，结合策略和运气",
            min_bet=min_bet,
            max_bet=max_bet
        )
        self.deck = Deck()
        self.community_cards = []
        self.player_hand = []
        self.ai_players = []
        self.num_ai_players = num_ai_players
        self.pot = 0.0
        self.current_stage = ""
        self.player_bet = 0.0
        self.player_folded = False
        self.player_hand_rank = ("", [])
        self.ai_hand_ranks = []
        
    def start_game(self) -> Dict[str, Any]:
        """
        开始游戏
        
        Returns:
            Dict: 游戏初始状态
        """
        if self.current_bet <= 0:
            return {"error": "请先下注"}
            
        # 重置游戏状态
        self.is_game_over = False
        self.community_cards = []
        self.player_hand = []
        self.ai_players = []
        self.pot = 0.0
        self.current_stage = "preflop"
        self.player_bet = self.current_bet
        self.player_folded = False
        self.player_hand_rank = ("", [])
        self.ai_hand_ranks = []
        
        # 洗牌
        self.deck = Deck()
        self.deck.shuffle()
        
        # 创建AI玩家
        self._create_ai_players()
        
        # 发手牌
        self.player_hand = [self.deck.deal(), self.deck.deal()]
        for ai in self.ai_players:
            ai["hand"] = [self.deck.deal(), self.deck.deal()]
            
        # 收集盲注
        self.pot = self.current_bet * (len(self.ai_players) + 1)
        
        return self.get_game_state()
        
    def make_move(self, move: str, **kwargs) -> Dict[str, Any]:
        """
        执行游戏动作
        
        Args:
            move: 动作名称
            **kwargs: 动作参数
            
        Returns:
            Dict: 执行动作后的游戏状态
        """
        if self.is_game_over:
            return {"error": "游戏已结束，请重新开始"}
            
        if move == "fold":
            return self._handle_fold()
        elif move == "call":
            return self._handle_call()
        elif move == "raise":
            bet_amount = kwargs.get("amount", 0)
            return self._handle_raise(bet_amount)
        elif move == "check":
            return self._handle_check()
        else:
            return {"error": f"无效的动作: {move}"}
            
    def get_available_moves(self) -> List[str]:
        """
        获取当前可用的动作列表
        
        Returns:
            List[str]: 可用动作列表
        """
        if self.is_game_over or self.player_folded:
            return []
            
        moves = ["fold"]
        
        # 检查是否可以check（无需额外下注）
        if self.player_bet >= max([ai["bet"] for ai in self.ai_players]):
            moves.append("check")
        else:
            moves.append("call")
            
        # 始终可以加注
        moves.append("raise")
            
        return moves
        
    def get_game_state(self) -> Dict[str, Any]:
        """
        获取当前游戏状态
        
        Returns:
            Dict: 游戏状态
        """
        state = {
            "player_hand": [str(card) for card in self.player_hand],
            "community_cards": [str(card) for card in self.community_cards],
            "pot": self.pot,
            "current_bet": self.current_bet,
            "player_bet": self.player_bet,
            "current_stage": self.current_stage,
            "available_moves": self.get_available_moves(),
            "is_game_over": self.is_game_over,
            "player_folded": self.player_folded,
            "ai_players": []
        }
        