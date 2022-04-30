
from typing import List
from ...domain.entity.json_data import JSONData

class Mod:

    def __init__(self, name: str, url: str, version: str) -> None:
        self.name = name
        self.url = url
        self.version = version

    def to_json(self) -> dict:
        return {
            "version": self.version,
            "name": self.name,
            "url": self.url
        }

class MinecraftMods(JSONData):

    def get_version(self) -> str:
        return self.json_data["version"]

    def get_creation(self) -> str:
        return self.json_data["creation"]

    def get_lastmodified(self) -> str:
        return self.json_data["lastmodified"]

    def get_mods(self) -> List[Mod]:
        for mod in self.json_data["mods"]:
            yield Mod(mod["name"], mod["url"], mod["version"])

    def get_mod(self, name: str) -> Mod:
        for mod in self.get_mods():
            if mod.name == name:
                return mod
        return None

    def validate(self) -> bool:
        return "mods" in self.json_data and \
            "version" in self.json_data and \
            "creation" in self.json_data and \
            "lastmodified" in self.json_data

    def to_json(self) -> dict:
        return {
            "version": self.get_version(),
            "creation": self.get_creation(),
            "lastmodified": self.get_lastmodified(),
            "mods": [mod.to_json() for mod in self.get_mods()]
        }