# This file contains the implementation of the minigame in the game.

# Including : Blackjack, Lottery, Roulette, Casino.

import random
import time
from user import User


def start_lottery_game(user):
    print("Welcome to Lottery Game!")
    print(f"You have {user.get_current_cash()} J$ in your account!")
    print("Please enter the numbers for the lottery ticket separated by commas.")
    numbers = input().split(",")
    numbers = [int(num) for num in numbers]
    print("Generating lottery numbers...")
    time.sleep(2)
    print("Lottery numbers are:")
    print(f"First number: {random.randint(1, 39)}")
    print(f"Second number: {random.randint(1, 12)}")
    print(f"Third number: {random.randint(1, 12)}")
    print(f"Fourth number: {random.randint(1, 12)}")
    print(f"Fifth number: {random.randint(1, 12)}")
    print(f"Your numbers are: {numbers}")
    if numbers == [random.randint(1, 39), random.randint(1, 12), random.randint(1, 12), random.randint(1, 12),
                   random.randint(1, 12)]:
        print("Congratulations! You won the lottery!")
        user.add_cash(1000)
        print(f"You have won 1000 J$!")
    else:
        print("Sorry, you did not win the lottery.")
        print(f"Your numbers are: {numbers}")
        print(f"Your current cash is {user.get_cash()}")


