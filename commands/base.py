from abc import ABC, abstractmethod

class Command(ABC):
    name: str
    aliases: list[str]
    description: str

    @abstractmethod
    def execute(self, *args):
        pass 