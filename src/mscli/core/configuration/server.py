from ...domain.configuration.server import Server
from .properties import Properties1122, Properties118
from .mods import MinecraftMods

class ForgeServer(Server):

    def __init__(self, properties: Properties1122 = None, icon: str = None, world: str = None, mods: MinecraftMods = None) -> None:
        super().__init__(properties, icon=icon, world=world)
        self.mods = mods

    def get_mods(self) -> MinecraftMods:
        return self.mods
    
    def get_properties(self) -> Properties1122:
        return self.properties

    def get_icon(self) -> str:
        return self.icon

    def get_world(self) -> str:
        return self.world


class VanillaServer(Server):

    def __init__(self, properties: Properties118 = None, icon: str = None, world: str = None) -> None:
        super().__init__(properties=properties, icon=icon, world=world)
    
    def get_properties(self) -> Properties118:
        return self.properties

    def get_icon(self) -> str:
        return self.icon

    def get_world(self) -> str:
        return self.world
