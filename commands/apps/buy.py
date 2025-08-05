from commands.base import Command

class AppBuyCommand(Command):
    name = "app buy"
    aliases = []
    description = "Buy an app"

    def execute(self, app_id):
        # Call app_service.install_app(current_user, app_id)
        pass 