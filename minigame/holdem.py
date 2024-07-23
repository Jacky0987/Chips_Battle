import random

suits = ['♠', '♥', '♦', '♣']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

deck = [(rank, suit) for suit in suits for rank in ranks]

def shuffle_deck(deck):
    random.shuffle(deck)

def deal_cards(deck, num_players, num_cards_per_player):
    hands = []
    for _ in range(num_players):
        hand = []
        for _ in range(num_cards_per_player):
            card = deck.pop()
            hand.append(card)
        hands.append(hand)
    return hands

# 比较两张牌的大小
def compare_cards(card1, card2):
    rank1 = ranks.index(card1[0])
    rank2 = ranks.index(card2[0])
    if rank1 > rank2:
        return 1
    elif rank1 < rank2:
        return -1
    else:
        return 0

# 计算手牌的点数
def calculate_hand_value(hand):
    # 统计每个面值的出现次数
    rank_count = {}
    for card in hand:
        rank = card[0]
        if rank in rank_count:
            rank_count[rank] += 1
        else:
            rank_count[rank] = 1

    # 检查牌型
    if len(rank_count) == 2:
        for count in rank_count.values():
            if count == 4:
                return "四条"
            elif count == 1:
                return "葫芦"
    elif len(rank_count) == 3:
        for count in rank_count.values():
            if count == 3:
                for other_count in rank_count.values():
                    if other_count == 2:
                        return "满堂红"
                return "三条"
    elif len(rank_count) == 4:
        return "两对"
    elif len(rank_count) == 5:
        sorted_hand = sorted(hand, key=lambda x: ranks.index(x[0]))
        is_straight = True
        for i in range(len(sorted_hand) - 1):
            if ranks.index(sorted_hand[i + 1][0]) - ranks.index(sorted_hand[i][0])!= 1:
                is_straight = False
                break
        if is_straight:
            if sorted_hand[0][0] == 'A' and sorted_hand[-1][0] == '10':
                return "皇家同花顺"
            elif sorted_hand[0][1] == sorted_hand[-1][1]:
                return "同花顺"
            else:
                return "顺子"
        if sorted_hand[0][1] == sorted_hand[-1][1]:
            return "同花"
    return "高牌"

class Player:
    def __init__(self, name, chips=1000, is_ai=False):
        self.name = name
        self.chips = chips
        self.hand = []
        self.bet = 0
        self.folded = False
        self.is_ai = is_ai

    def bet_chips(self, amount):
        if amount <= self.chips:
            self.chips -= amount
            self.bet += amount
            print(f"{self.name} 下注 {amount} 筹码")
        else:
            print(f"{self.name} 筹码不足，无法下注")

    def raise_bet(self, amount):
        if amount <= self.chips + self.bet:
            self.chips -= amount - self.bet
            self.bet = amount
            print(f"{self.name} 加注 {amount} 筹码")
        else:
            print(f"{self.name} 筹码不足，无法加注")

    def fold(self):
        self.folded = True
        print(f"{self.name} 弃牌")

    def ai_action(self, current_bet):
        # 简单的 AI 策略：根据手牌强度决定行动
        hand_value = calculate_hand_value(self.hand)
        if hand_value in ["皇家同花顺", "同花顺", "四条", "葫芦"]:
            if current_bet < self.chips // 2:
                self.raise_bet(current_bet * 2)
            else:
                self.bet_chips(current_bet)
        elif hand_value in ["满堂红", "顺子", "同花"]:
            if current_bet < self.chips // 4:
                self.raise_bet(current_bet * 1.5)
            else:
                self.bet_chips(current_bet)
        elif hand_value in ["三条", "两对"]:
            if current_bet < self.chips // 8:
                self.raise_bet(current_bet)
            else:
                self.bet_chips(current_bet // 2)
        else:
            # 手牌较弱，有 50% 的概率弃牌，50% 的概率跟注
            if random.random() < 0.5:
                self.fold()
            else:
                self.bet_chips(current_bet)

# 发底牌函数
def deal_flop(deck):
    flop = []
    for _ in range(3):
        card = deck.pop()
        flop.append(card)
    return flop

# 游戏流程
def play_game():
    num_players = 6
    players = [Player(f"玩家 {i + 1}", is_ai=(i > 0)) for i in range(num_players)]

    shuffle_deck(deck)

    for player in players:
        player.hand = deal_cards(deck, 1, 2)[0]

    flop = deal_flop(deck)
    print("底牌：", flop)

    current_bet = 10  # 初始底注
    player_index = 0

    while True:
        player = players[player_index]

        if not player.folded:
            print(f"{player.name} 的手牌: {player.hand}")
            print(f"当前底注: {current_bet}")
            if player.is_ai:
                player.ai_action(current_bet)
            else:
                action = input(f"{player.name}，选择行动（bet/raise/fold）: ")

                if action == 'bet':
                    bet_amount = int(input("输入下注金额: "))
                    player.bet_chips(bet_amount)
                    current_bet = bet_amount
                elif action =='raise':
                    raise_amount = int(input("输入加注金额: "))
                    player.raise_bet(raise_amount)
                    current_bet = raise_amount
                elif action == 'fold':
                    player.fold()

        player_index = (player_index + 1) % num_players

        # 检查是否所有未弃牌的玩家都已行动且下注相同
        all_bets_same = True
        active_players = [p for p in players if not p.folded]
        bet_amounts = [p.bet for p in active_players]
        if len(set(bet_amounts)) > 1:
            all_bets_same = False

        if all(all_bets_same and not p.folded for p in players):
            break

    # 比较牌型，确定胜者
    hand_values = [calculate_hand_value(p.hand + flop) for p in players if not p.folded]
    winner_index = hand_values.index(max(hand_values))
    winner = players[winner_index]

    print(f"{winner.name} 获胜！")
    winner.chips += sum(p.bet for p in players)

play_game()