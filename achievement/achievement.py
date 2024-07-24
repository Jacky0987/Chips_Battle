class Achievement:
    def __init__(self, name, description, condition_func):
        self.name = name
        self.description = description
        self.condition_func = condition_func
        self.completed = False

    def load_achievement(self):
        self.completed = True
