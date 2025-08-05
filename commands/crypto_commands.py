from commands.base import Command

class CryptoTradeCommand(Command):
    name = "crypto trade"
    aliases = []
    description = "Trade crypto"

    def execute(self, action, symbol, quantity):
        # Call crypto_service.trade
        pass 