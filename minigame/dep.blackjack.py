"""import random
import time

# 游戏内容设定函数声明
def replay(ans):
    print("您是否还想继续进行？(Y/n)")
    ans = input()

def setting(chips, money):
    while chips >= 0:
        money = chips
        print(f"New chips setting applied. New chips {chips}")

# 游戏主要内容操作函数设定
def hit(total, flag_legal, playerturns):
    card = random.randint(1, 13)
    if playerturns > 2:
        print("您已经追加要牌", (playerturns - 2), "次，是否要追加下注？(输入追加的金额或 0 表示不追加): ")
        additionalBet = int(input())
        if additionalBet > 0 and additionalBet <= money:
            bet += additionalBet
            money -= additionalBet
        elif additionalBet > money:
            print("追加下注金额超过您的筹码，请重新输入。")
    if card >= 10:
        card = 0.5
    if judging21(card + total):
        total = card + total
        print("新获得的牌点数为", card)
        print("此时您的牌点总数为", total)
        print()
        flag_legal = 1
    else:
        total = card + total
        print("新获得的牌点数为", card)
        print("此时您的牌点总数为", total)
        print("您的牌已经超过 21 点，请输入 s 结束该轮比赛。")
        print()
        flag_legal = 0
        playerturns = 10

def cpu_hit(total, cputurns):
    card = random.randint(1, 13)
    if card >= 10:
        card = 0.5
    if total + card > 21:
        print("CPU 选择不获取新牌，总点数为", total)
        return 0
    else:
        total += card
        print("CPU 选择获取新牌")
        print("此时 CPU 的新牌点总数为", total)
        return 1

def deal(player, cpu, playerturns, cputurns, player_score, cpu_score):
    playerturns = 2
    cputurns = 2
    playercard1 = random.randint(1, 13)
    time.sleep(1.25)
    playercard2 = random.randint(1, 13)
    time.sleep(0.25)
    cpucard1 = random.randint(1, 13)
    time.sleep(1.25)
    cpucard2 = random.randint(1, 13)
    if playercard1 > 10:
        playercard1 = 0.5
    if playercard2 > 10:
        playercard2 = 0.5
    if cpucard1 > 10:
        cpucard1 = 0.5
    if cpucard2 > 10:
        cpucard2 = 0.5
    player = playercard1 + playercard2
    cpu = cpucard1 + cpucard2
    print("您的牌总和为", player)
    print("[" + str(playercard1) + "]")
    print("[" + str(playercard2) + "]")
    print()
    print("CPU 的牌为:")
    print("[" + str(cpucard1) + "]")
    print("[" + str(cpucard2) + "]")
    print("CPU 的牌总和为", cpu)

def admin_deal(player, cpu, playerturns, cputurns, player_score, cpu_score):
    playerturns = 2
    cputurns = 2
    playercard1 = random.randint(1, 13)
    time.sleep(1.25)
    playercard2 = random.randint(1, 13)
    time.sleep(0.25)
    cpucard1 = random.randint(1, 13)
    time.sleep(1.25)
    cpucard2 = random.randint(1, 13)
    if playercard1 > 10:
        playercard1 = 0.5
    if playercard2 > 10:
        playercard2 = 0.5
    if cpucard1 > 10:
        cpucard1 = 0.5
    if cpucard2 > 10:
        cpucard2 = 0.5
    player = playercard1 + playercard2
    cpu = cpucard1 + cpucard2
    print("您的牌总和为", player)
    print("[" + str(playercard1) + "]")
    print("[" + str(playercard2) + "]")
    print()
    print("CPU 的牌为:")
    print("[" + str(cpucard1) + "]")
    print("[" + str(cpucard2) + "]")
    print("CPU 的牌总和为", cpu)

# 游戏判断与打印函数设定
def judging21(a):
    if a > 21:
        return 0
    else:
        return 1

def print_results(wins, lose, draw, money, default_money):
    name = input("请输入您的用户名称:")
    print("胜场 :" + str(wins))
    print("败场 :" + str(lose))
    print("平局场次 :" + str(draw))
    print("筹码总数 :" + str(money))
    print(name + " 的战绩为" + str(wins) + "-" + str(draw) + "-" + str(lose) + " " + "总筹码为:" + str(money))
    print("相比于初始筹码数目，您的正负差为 $ " + str(money - default_money))

def results(player, cpu, bet, money, draw, win, lose):
    if cpu == player:
        print("您和 CPU 打平了！")
        draw += 1
        money += bet
    if player > 21:
        print("您的牌超过了 21!")
        lose += 1
    else:
        if cpu < player:
            print("您赢了！")
            money += (bet * 2)
            win += 1
    if cpu > 21:
        print("CPU 的牌点数超过了 21！")
        if player < 21:
            print("您赢了！")
            win += 1
            money += (bet * 2)
    else:
        if cpu > player:
            print("很遗憾，您输了这一回合！")
            lose += 1

# 游戏数学与计算机机制函数声明
def random(hi, lo):
    return random.randint(lo, hi)

def wait(milli):
    start = time.time()
    while (time.time() - start) < milli / 1000:
        pass

def pause():
    input("按任意键继续...")

# 全局变量声明
player = 0
cpu = 0
player_score = 0
cpu_score = 0
flag_legal = 1
flag = 0
admin_mode = 0
password = "1"
input_pwd = ""
win = 0
lose = 0
draw = 0
playerturns = 0
cputurns = 0
money = 100
default_money = 100
bet = 0

def main():
    ans = 'n'
    choice = 0

    while True:
        print("欢迎来到 21 点游戏！")
        print("1. 开始游戏")
        print("2. 游戏规则")
        print("3. 游戏设置")
        print("4. 退出")
        print("请输入您的选择: ")
        choice = int(input())

        if choice == 1:
            print("欢迎来到 21 点游戏！")
            ans = 'y'
            print("您初始拥有的筹码为 $", money)
            if ans.lower()!= 'y':
                return
            while True:
                if money <= 0:
                    print("您破产了！")
                    return
                BET(bet, money)
                if admin_mode == 0:
                    deal(player, cpu, playerturns, cputurns, player_score, cpu_score)
                else:
                    admin_deal(player, cpu, playerturns, cputurns, player_score, cpu_score)
                while True:
                    print("您是否要继续拿牌？(H 以继续，s 则停止)")
                    ans = input()
                    if ans.lower() in ['h', 'y']:
                        playerturns += 1
                        if playerturns > 5:
                            print("操作非法！")
                    if playerturns < 6 and ans.lower() == 'h':
                        hit(player, flag_legal, playerturns)
                while cpu < 16 and cputurns < 6:
                    print()
                    print("CPU 正在进行思考")
                    wait(600)
                    cpu_hit(cpu, cputurns)
                print()
                print("CPU 的总数:", cpu)
                print("您的总数:", player)
                print()
                results(player, cpu, bet, money, draw, win, lose)
                replay(ans)
            print_results(win, lose, draw, money, default_money)
            return

        elif choice == 2:
            print("游戏介绍")
            game_rules()
        elif choice == 3:
            print("游戏设置")
            print("请输入密码：")
            input_pwd = input()
            if input_pwd == password:
                print("您已获得权限，进入设置菜单。")
                admin_mode = 1
                choice3 = 0
                while True:
                    print("1. 初始筹码设置")
                    print("2. 游戏作者")
                    print("3. 回到主菜单")
                    print("请输入您的选择: ")
                    choice3 = int(input())
                    if choice3 == 1:
                        print("请输入初始筹码数目：")
                        def_money = int(input())
                        print("您设置的初始筹码为 $", def_money)
                        setting(def_money, money)
                        default_money = def_money
                        pause()
                    elif choice3 == 2:
                        print("游戏作者")
                        game_author()
                        pause()
                    elif choice3 == 3:
                        break
                    else:
                        print("无效的选择！请键入有效选项。")
            else:
                print("密码错误.")
                pause()
        elif choice == 4:
            print("退出游戏。再见！")
            break
        else:
            print("无效的选择！请键入有效选项。")

def game_rules():
    print("1. 牌面大小为 1-13，11-13 被视为 0.5 分。")
    print("2. 牌面大小相同的牌，视为同一张牌。")
    print("3. 游戏开始时，玩家会收到两张牌，出现爆牌（手中牌的总点数超过 21 点）即输掉比赛。")
    print("4. 目标是使您手中的卡牌总点数尽可能接近 21 点，但不超过 21 点。")
    print("5. 玩家可以选择“Hit”来抽取额外的牌，以尽可能接近 21 点。")
    print("6. 玩家还可以选择“Stand”（不再抽取额外的牌），并将轮到庄家表现。")
    print("7. 如果玩家和庄家的点数相同，则比赛平局。")
    pause()

def game_author():
    print("作者：SuperJacky6")
    print("联系方式：Adding2003@gmail.com")

if __name__ == "__main__":
    main()

"""
