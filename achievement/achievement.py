class Achievement:
    def __init__(self, name, description, condition_func):
        self.name = name
        self.description = description
        self.condition_func = condition_func
        self.completed = False

    def check_condition(self, player_data):
        if self.condition_func(player_data):
            self.completed = True
            return True
        return False

# 定义一些成就的条件函数
def first_trade(player_data):
    return len(player_data['trades']) > 0

def initial_funds_growth_10_percent(player_data):
    initial_funds = player_data['initial_funds']
    current_funds = player_data['current_funds']
    return current_funds >= initial_funds * 1.1

# 创建成就实例
achievements = [
    Achievement("First Trade", "Complete your first stock trade", first_trade),
    Achievement("10% Initial Funds Growth", "Increase your initial funds by 10%", initial_funds_growth_10_percent)
]