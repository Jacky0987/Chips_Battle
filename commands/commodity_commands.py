from commands.base import Command

class CommodityTradeCommand(Command):
    name = "trade"
    aliases = []
    description = "Trade commodities"

    def execute(self, action, symbol, quantity):
        # Call commodity_service.trade
        pass

# Add other commands: portfolio commodity, market commodity 