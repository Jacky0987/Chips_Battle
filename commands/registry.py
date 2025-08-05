from typing import Dict
from .base import Command

class CommandRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.commands: Dict[str, Command] = {}
        return cls._instance

    def register(self, command: Command):
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command 