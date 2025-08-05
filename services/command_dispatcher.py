from commands.registry import CommandRegistry

class CommandDispatcher:
    def __init__(self):
        self.registry = CommandRegistry()

    def dispatch(self, input_str: str):
        parts = input_str.split()
        cmd = parts[0]
        args = parts[1:]
        if cmd in self.registry.commands:
            self.registry.commands[cmd].execute(*args)
        else:
            print(f"Unknown command: {cmd}") 