from commands.base import Command

class MediaListCommand(Command):
    name = "media list"
    aliases = []
    description = "List media outlets"

    def execute(self, *args):
        # Call media_service.show_list
        pass 