from commands.base import Command

class AllianceCreateCommand(Command):
    name = "alliance create"
    aliases = []
    description = "Create alliance"

    def execute(self, name):
        # Call alliance_service.create_alliance
        pass 