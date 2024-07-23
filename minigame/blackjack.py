import random

# 名词解释
# 庄家：游戏中第一个坐下的玩家默认为庄家。
# 闲家：本轮不坐庄的玩家。

# 牌面值字典
card_values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

# 初始筹码数量
default_money = 100
money = default_money

# 发牌函数
def deal_card():
    cards = list(card_values.keys())
    card = random.choice(cards)
    return card

# 计算手牌总值
def calculate_hand_value(hand):
    total = 0
    num_aces = 0
    for card in hand:
        if card == 'A':
            num_aces += 1
            total += 11
        else:
            total += card_values[card]
    while total > 21 and num_aces > 0:
        total -= 10
        num_aces -= 1
    return total

# 分牌函数
def split_hand(hand):
    if len(hand) == 2 and hand[0] == hand[1]:  # 只有初始的两张牌相同才能分牌
        new_hand1 = [hand[0]]
        new_hand2 = [hand[1]]
        return new_hand1, new_hand2
    else:
        print("不符合分牌条件")
        return hand, None

# 打印当前玩家的筹码数量
def print_money():
    print(f"您当前的筹码数量为：{money}")

# 游戏主逻辑
def play_game():
    global money  # 使用全局变量记录筹码

    player_hand = [deal_card(), deal_card()]
    dealer_hand = [deal_card(), deal_card()]
    print("您的手牌：", player_hand)
    player_value = calculate_hand_value(player_hand)
    print("您的手牌总值：", player_value)

    while True:
        choice = input("要牌吗？(y/n) 或选择其他操作 (split/stand/double/insurance)：")
        if choice.lower() == 'y':  # 要牌
            new_card = deal_card()
            player_hand.append(new_card)
            player_value = calculate_hand_value(player_hand)
            print("您的手牌：", player_hand)
            print("您的手牌总值：", player_value)
            if player_value > 21:
                print("您爆牌了，输了！")
                money -= bet  # 输掉赌注
                return
        elif choice.lower() =='split':  # 分牌
            new_hand1, new_hand2 = split_hand(player_hand)
            if new_hand2:  # 成功分牌
                bet1 = bet  # 为新分的手牌设置相同的赌注
                bet2 = bet
                print("第一手分牌后的手牌：", new_hand1)
                print("第二手分牌后的手牌：", new_hand2)
                # 分别对两手牌进行后续操作
                play_split_hand(new_hand1, dealer_hand, bet1)
                play_split_hand(new_hand2, dealer_hand, bet2)
                return
        elif choice.lower() =='stand':  # 停牌
            break
        elif choice.lower() == 'double':  # 加倍
            if money >= bet:  # 确保有足够的筹码进行加倍
                money -= bet  # 先扣除当前赌注
                bet *= 2  # 赌注加倍
                new_card = deal_card()
                player_hand.append(new_card)
                player_value = calculate_hand_value(player_hand)
                print("您的手牌：", player_hand)
                print("您的手牌总值：", player_value)
                break
            else:
                print("您没有足够的筹码进行加倍")
        elif choice.lower() == 'insurance':  # 保险
            insurance_bet = bet // 2  # 保险金是赌注的一半
            if money >= insurance_bet:  # 确保有足够的筹码支付保险金
                money -= insurance_bet  # 扣除保险金
                if dealer_hand[0] == 'A':  # 庄家确实有黑杰克
                    print("庄家是黑杰克，您赢得保险金")
                    money += (bet + insurance_bet)  # 赢回赌注和保险金
                else:  # 庄家没有黑杰克
                    print("庄家不是黑杰克，您输掉保险金")
            else:
                print("您没有足够的筹码购买保险")

    dealer_value = calculate_hand_value(dealer_hand)
    print("庄家的手牌：", dealer_hand)
    print("庄家的手牌总值：", dealer_value)

    while dealer_value < 17:
        new_card = deal_card()
        dealer_hand.append(new_card)
        dealer_value = calculate_hand_value(dealer_hand)

    if dealer_value > 21:
        print("庄家爆牌，您赢了！")
        money += bet * 2  # 赢得两倍赌注
    elif dealer_value > player_value:
        print("庄家赢了！")
        money -= bet  # 输掉赌注
    elif dealer_value < player_value:
        print("您赢了！")
        money += bet * 2  # 赢得两倍赌注
    else:
        print("平局！")
        money += bet  # 退回赌注

# 处理分牌后的手牌逻辑
def play_split_hand(hand, dealer_hand, bet):
    global money  # 使用全局变量记录筹码

    player_value = calculate_hand_value(hand)
    while True:
        choice = input(f"对于分牌后的手牌，要牌吗？(y/n) 或选择操作 (stand/double)：")
        if choice.lower() == 'y':  # 要牌
            new_card = deal_card()
            hand.append(new_card)
            player_value = calculate_hand_value(hand)
            print("手牌：", hand)
            print("手牌总值：", player_value)
            if player_value > 21:
                print("您爆牌了，输了这手牌！")
                money -= bet  # 输掉该手牌的赌注
                return
        elif choice.lower() =='stand':  # 停牌
            break
        elif choice.lower() == 'double':  # 加倍
            if money >= bet:  # 确保有足够的筹码进行加倍
                money -= bet  # 先扣除当前赌注
                bet *= 2  # 赌注加倍
                new_card = deal_card()
                hand.append(new_card)
                player_value = calculate_hand_value(hand)
                print("手牌：", hand)
                print("手牌总值：", player_value)
                break

    dealer_value = calculate_hand_value(dealer_hand)
    print("庄家的手牌：", dealer_hand)
    print("庄家的手牌总值：", dealer_value)

    if dealer_value > 21:
        print("庄家爆牌，您赢了这手牌！")
        money += bet * 2  # 赢得两倍赌注
    elif dealer_value > player_value:
        print("庄家赢了这手牌！")
        money -= bet  # 输掉该手牌的赌注
    elif dealer_value < player_value:
        print("您赢了这手牌！")
        money += bet * 2  # 赢得两倍赌注
    else:
        print("这手牌平局！")
        money += bet  # 退回该手牌的赌注

if __name__ == "__main__":
    while True:
        print_money()  # 打印当前筹码数量
        print("欢迎来到 21 点游戏！")
        bet = int(input("请输入您的赌注："))  # 玩家输入赌注
        if bet <= money:  # 检查赌注是否小于等于玩家的筹码
            play_game()
        else:
            print("您的赌注超过了当前拥有的筹码，请重新输入。")