from commands.base import Command

class NationStatusCommand(Command):
    name = "nation status"
    aliases = []
    description = "Show nation status"

    def execute(self, nation_name):
        # Call politics_service.show_status
        pass 