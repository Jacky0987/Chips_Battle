from commands.base import Command

class AppMarketCommand(Command):
    name = "app market"
    aliases = ["appmarket"]
    description = "Show app market"

    def execute(self, *args):
        # Call app_service.show_market()
        pass 