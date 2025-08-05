from commands.base import Command

class RoleCommand(Command):
    name = "role"
    aliases = []
    description = "Manage roles"

    def execute(self, *args):
        if args[0] == "list":
            # List roles
            pass
        # ... other subcommands 