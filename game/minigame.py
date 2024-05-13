# This file contains the implementation of the minigame in the game.

# Including : Blackjack, Lottery, Roulette, Casino.

import random
import time
from user import User


class Minigame:
    def __init__(self, user):
        self.user = user
