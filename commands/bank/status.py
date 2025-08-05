from commands.base import Command

class BankStatusCommand(Command):
    name = "bank status"
    aliases = []
    description = "Show bank status"

    def execute(self, *args):
        # Call bank_service.show_status()
        pass 