from commands.base import Command

class HomeMarketCommand(Command):
    name = "home market"
    aliases = []
    description = "Show luxury market"

    def execute(self, *args):
        # Call home_service.show_market()
        pass 