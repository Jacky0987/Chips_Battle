"""
小游戏API系统 - 基础类
提供小游戏的基本接口和功能
"""

import abc
from typing import Dict, Any, List, Optional, Tuple


class MiniGame(abc.ABC):
    """小游戏基础抽象类，所有小游戏都应继承此类"""
    
    def __init__(self, name: str, description: str, min_bet: float = 10.0, max_bet: float = 1000.0):
        """
        初始化小游戏
        
        Args:
            name: 游戏名称
            description: 游戏描述
            min_bet: 最小下注金额
            max_bet: 最大下注金额
        """
        self.name = name
        self.description = description
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.current_bet = 0.0
        self.is_game_over = False
        self.player_cash = 0.0
        
    def set_player_cash(self, cash: float) -> None:
        """设置玩家当前现金"""
        self.player_cash = cash
        
    def place_bet(self, amount: float) -> bool:
        """
        下注
        
        Args:
            amount: 下注金额
            
        Returns:
            bool: 下注是否成功
        """
        if amount < self.min_bet:
            return False
        if amount > self.max_bet:
            return False
        if amount > self.player_cash:
            return False
            
        self.current_bet = amount
        return True
        
    @abc.abstractmethod
    def start_game(self) -> Dict[str, Any]:
        """
        开始游戏
        
        Returns:
            Dict: 游戏初始状态
        """
        pass
        
    @abc.abstractmethod
    def make_move(self, move: str, **kwargs) -> Dict[str, Any]:
        """
        执行游戏动作
        
        Args:
            move: 动作名称
            **kwargs: 动作参数
            
        Returns:
            Dict: 执行动作后的游戏状态
        """
        pass
        
    @abc.abstractmethod
    def get_available_moves(self) -> List[str]:
        """
        获取当前可用的动作列表
        
        Returns:
            List[str]: 可用动作列表
        """
        pass
        
    @abc.abstractmethod
    def get_game_state(self) -> Dict[str, Any]:
        """
        获取当前游戏状态
        
        Returns:
            Dict: 游戏状态
        """
        pass
        
    def end_game(self) -> Tuple[bool, float]:
        """
        结束游戏并结算
        
        Returns:
            Tuple[bool, float]: (是否获胜, 获得/损失金额)
        """
        self.is_game_over = True
        result = self._calculate_result()
        return result
        
    @abc.abstractmethod
    def _calculate_result(self) -> Tuple[bool, float]:
        """
        计算游戏结果
        
        Returns:
            Tuple[bool, float]: (是否获胜, 获得/损失金额)
        """
        pass
        
    def reset(self) -> None:
        """重置游戏状态"""
        self.current_bet = 0.0
        self.is_game_over = False


class Card:
    """扑克牌类"""
    SUITS = ["♥", "♦", "♣", "♠"]
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
    
    def __init__(self, suit: str, rank: str):
        """
        初始化扑克牌
        
        Args:
            suit: 花色
            rank: 点数
        """
        self.suit = suit
        self.rank = rank
        
    def __str__(self) -> str:
        return f"{self.suit}{self.rank}"
        
    def get_value(self, ace_high: bool = True) -> int:
        """
        获取牌的点数值
        
        Args:
            ace_high: A是否为高牌(11/14)，否则为低牌(1)
            
        Returns:
            int: 牌的点数值
        """
        if self.rank == "A":
            return 11 if ace_high else 1
        elif self.rank in ["K", "Q", "J"]:
            return 10
        else:
            return int(self.rank)
            
    def get_poker_value(self) -> int:
        """
        获取牌在扑克游戏中的点数值
        
        Returns:
            int: 牌在扑克游戏中的点数值
        """
        if self.rank == "A":
            return 14
        elif self.rank == "K":
            return 13
        elif self.rank == "Q":
            return 12
        elif self.rank == "J":
            return 11
        else:
            return int(self.rank)


class Deck:
    """扑克牌组类"""
    
    def __init__(self, num_decks: int = 1):
        """
        初始化扑克牌组
        
        Args:
            num_decks: 牌组数量
        """
        self.cards = []
        self.create_deck(num_decks)
        
    def create_deck(self, num_decks: int = 1) -> None:
        """
        创建牌组
        
        Args:
            num_decks: 牌组数量
        """
        self.cards = []
        for _ in range(num_decks):
            for suit in Card.SUITS:
                for rank in Card.RANKS:
                    self.cards.append(Card(suit, rank))
                    
    def shuffle(self) -> None:
        """洗牌"""
        import random
        random.shuffle(self.cards)
        
    def deal(self) -> Optional[Card]:
        """
        发牌
        
        Returns:
            Card: 一张牌，如果牌组为空则返回None
        """
        if not self.cards:
            return None
        return self.cards.pop()