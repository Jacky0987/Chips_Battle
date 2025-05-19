"""
21点游戏实现
"""

import random
from typing import Dict, Any, List, Tuple, Optional
import sys
import os

# 添加项目根目录到系统路径，以便导入models模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.minigame import MiniGame, Card, Deck


class Blackjack(MiniGame):
    """21点游戏实现"""
    
    def __init__(self, min_bet: float = 10.0, max_bet: float = 1000.0):
        """
        初始化21点游戏
        
        Args:
            min_bet: 最小下注金额
            max_bet: 最大下注金额
        """
        super().__init__(
            name="21点",
            description="尽可能接近21点但不超过21点的纸牌游戏",
            min_bet=min_bet,
            max_bet=max_bet
        )
        self.deck = Deck(num_decks=6)  # 使用6副牌
        self.player_hand = []
        self.dealer_hand = []
        self.player_score = 0
        self.dealer_score = 0
        self.game_status = ""
        
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
        self.player_hand = []
        self.dealer_hand = []
        self.player_score = 0
        self.dealer_score = 0
        self.game_status = "进行中"
        
        # 洗牌
        self.deck.shuffle()
        
        # 发牌：玩家两张，庄家两张（一张明牌，一张暗牌）
        self.player_hand.append(self.deck.deal())
        self.dealer_hand.append(self.deck.deal())
        self.player_hand.append(self.deck.deal())
        self.dealer_hand.append(self.deck.deal())
        
        # 计算初始分数
        self.player_score = self._calculate_hand_value(self.player_hand)
        self.dealer_score = self._calculate_hand_value([self.dealer_hand[0]])  # 只计算明牌
        
        # 检查是否有黑杰克
        if self.player_score == 21:
            return self._handle_blackjack()
            
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
            
        if move == "hit":
            return self._handle_hit()
        elif move == "stand":
            return self._handle_stand()
        elif move == "double":
            return self._handle_double()
        else:
            return {"error": f"无效的动作: {move}"}
            
    def get_available_moves(self) -> List[str]:
        """
        获取当前可用的动作列表
        
        Returns:
            List[str]: 可用动作列表
        """
        if self.is_game_over:
            return []
            
        moves = ["hit", "stand"]
        
        # 只有在只有两张牌的情况下才能加倍
        if len(self.player_hand) == 2 and self.player_cash >= self.current_bet:
            moves.append("double")
            
        return moves
        
    def get_game_state(self) -> Dict[str, Any]:
        """
        获取当前游戏状态
        
        Returns:
            Dict: 游戏状态
        """
        return {
            "player_hand": [str(card) for card in self.player_hand],
            "dealer_hand": [str(card) if i == 0 or self.is_game_over else "?" 
                           for i, card in enumerate(self.dealer_hand)],
            "player_score": self.player_score,
            "dealer_score": self._calculate_hand_value([self.dealer_hand[0]]) if not self.is_game_over 
                           else self._calculate_hand_value(self.dealer_hand),
            "current_bet": self.current_bet,
            "available_moves": self.get_available_moves(),
            "game_status": self.game_status,
            "is_game_over": self.is_game_over
        }
        
    def _calculate_result(self) -> Tuple[bool, float]:
        """
        计算游戏结果
        
        Returns:
            Tuple[bool, float]: (是否获胜, 获得/损失金额)
        """
        if self.game_status == "玩家获胜-黑杰克":
            return True, self.current_bet * 1.5
        elif self.game_status == "玩家获胜":
            return True, self.current_bet
        elif self.game_status == "平局":
            return False, 0
        else:  # 庄家获胜或玩家爆牌
            return False, -self.current_bet
            
    def _calculate_hand_value(self, hand: List[Card]) -> int:
        """
        计算手牌点数
        
        Args:
            hand: 手牌列表
            
        Returns:
            int: 手牌点数
        """
        value = 0
        aces = 0
        
        for card in hand:
            if card.rank == "A":
                aces += 1
                value += 11
            else:
                value += card.get_value()
                
        # 如果点数超过21且有A，则将A当作1点
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
            
        return value
        
    def _handle_hit(self) -> Dict[str, Any]:
        """处理要牌动作"""
        # 发一张牌给玩家
        self.player_hand.append(self.deck.deal())
        self.player_score = self._calculate_hand_value(self.player_hand)
        
        # 检查是否爆牌
        if self.player_score > 21:
            self.game_status = "庄家获胜-玩家爆牌"
            self.is_game_over = True
            
        return self.get_game_state()
        
    def _handle_stand(self) -> Dict[str, Any]:
        """处理停牌动作"""
        # 庄家亮出暗牌
        self.dealer_score = self._calculate_hand_value(self.dealer_hand)
        
        # 庄家按规则要牌（小于17点必须要牌）
        while self.dealer_score < 17:
            self.dealer_hand.append(self.deck.deal())
            self.dealer_score = self._calculate_hand_value(self.dealer_hand)
            
        # 判断胜负
        if self.dealer_score > 21:
            self.game_status = "玩家获胜-庄家爆牌"
        elif self.dealer_score > self.player_score:
            self.game_status = "庄家获胜"
        elif self.dealer_score < self.player_score:
            self.game_status = "玩家获胜"
        else:
            self.game_status = "平局"
            
        self.is_game_over = True
        return self.get_game_state()
        
    def _handle_double(self) -> Dict[str, Any]:
        """处理加倍动作"""
        # 加倍下注
        if self.player_cash < self.current_bet * 2:
            return {"error": "现金不足，无法加倍"}
            
        self.current_bet *= 2
        
        # 只再要一张牌
        self.player_hand.append(self.deck.deal())
        self.player_score = self._calculate_hand_value(self.player_hand)
        
        # 检查是否爆牌
        if self.player_score > 21:
            self.game_status = "庄家获胜-玩家爆牌"
            self.is_game_over = True
            return self.get_game_state()
            
        # 自动停牌，进入庄家回合
        return self._handle_stand()
        
    def _handle_blackjack(self) -> Dict[str, Any]:
        """处理黑杰克情况"""
        # 检查庄家是否也有黑杰克
        dealer_score = self._calculate_hand_value(self.dealer_hand)
        
        if dealer_score == 21:
            self.game_status = "平局-双方黑杰克"
        else:
            self.game_status = "玩家获胜-黑杰克"
            
        self.is_game_over = True
        return self.get_game_state()
        
    def reset(self) -> None:
        """重置游戏状态"""
        super().reset()
        self.player_hand = []
        self.dealer_hand = []
        self.player_score = 0
        self.dealer_score = 0
        self.game_status = ""
        
        # 如果牌不足，重新洗牌
        if len(self.deck.cards) < 52:
            self.deck = Deck(num_decks=6)
            self.deck.shuffle()


# 测试代码
if __name__ == "__main__":
    game = Blackjack()
    game.set_player_cash(1000)
    game.place_bet(100)
    
    # 开始游戏
    state = game.start_game()
    print("游戏开始:")
    print(f"玩家手牌: {state['player_hand']}, 点数: {state['player_score']}")
    print(f"庄家手牌: {state['dealer_hand']}, 点数: {state['dealer_score']}")
    
    # 模拟游戏流程
    while not game.is_game_over:
        moves = game.get_available_moves()
        if not moves:
            break
            
        # 简单AI：小于17点要牌，否则停牌
        move = "hit" if game.player_score < 17 and "hit" in moves else "stand"
        print(f"选择动作: {move}")
        
        state = game.make_move(move)
        print(f"玩家手牌: {state['player_hand']}, 点数: {state['player_score']}")
        print(f"庄家手牌: {state['dealer_hand']}, 点数: {state['dealer_score']}")
        print(f"游戏状态: {state['game_status']}")
        
    # 结算
    won, amount = game.end_game()
    print(f"游戏结束: {'获胜' if won else '失败'}, {'获得' if amount > 0 else '损失'} ${abs(amount)}")