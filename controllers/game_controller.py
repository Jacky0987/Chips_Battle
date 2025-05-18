from models.market import MarketSimulator


class GameController:
    def __init__(self, config_file="data/config.json"):
        """Initialize the game controller"""
        self.market = MarketSimulator(config_file)
        print(f"[DEBUG] GameController 初始化完成，市场模拟器已创建")

    def next_day(self):
        """Advance the market by one day
        Returns True if game continues, False if game over"""
        result = self.market.simulate_day()
        print(f"[DEBUG] 模拟前进一天: 当前天数 = {self.market.current_day}, 继续游戏 = {result}")
        return result

    def reset_game(self):
        """Reset the game to initial state"""
        # Reset the market but preserve portfolio
        print(f"[DEBUG] 重置游戏")
        return self.market.reset(reset_portfolio=False)
