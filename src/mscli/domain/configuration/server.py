
from abc import abstractmethod
from ..configuration.properties import Properties

class Server:
    
    def __init__(self, properties: Properties = None, icon: str = None, world: str = None) -> None:
        self.properties = properties
        self.icon = icon
        self.world = world

    @abstractmethod
    def save(self):
        pass