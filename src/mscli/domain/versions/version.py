from ..entity.json_data import JSONData
from .provider import Provider
from typing import List

from ... import __version__
from datetime import datetime

class Version(JSONData):

    def __init__(self, json_data: dict):
        super().__init__(json_data)
        self.name = json_data["name"]
        self.jvm = json_data["jvm"]
        self.type = json_data["type"]
        self.providers = self.get_providers()

    def get_providers(self):
        """
        Returns a list of providers
        """
        for name, info in self.json_data["providers"].items():
            yield Provider(
                name=name,
                version=self.name,
                jvm=self.jvm,
                url=info["url"],
                filename=info["filename"],
                type=info["type"],
                data=info["data"]
            )

    def get_provider(self, provider_name: str) -> Provider:
        """
        Returns a provider by name
        """
        for provider in self.get_providers():
            if provider.name == provider_name:
                return provider
        return None

    def validate(self) -> bool:
        return "name" in self.json_data and \
            "jvm" in self.json_data and \
            "type" in self.json_data and \
            "providers" in self.json_data

    def __str__(self):
        return f"Version={{version: {self.name}, providers: {self.providers}}}"

class Versions(JSONData):

    def get_mscli_version(self) -> str:
        return self.json_data["version"]

    def get_creation(self) -> str:
        return self.json_data["creation"]

    def get_version(self, version_name: str):
        for version in self.get_versions():
            version: Version
            if version.name == version_name:
                return version
        return None

    def get_versions(self) -> List[Version]:
        for version in self.json_data["versions"]:
            yield Version(
                json_data=version
            )

    def validate(self) -> bool:
        return "versions" in self.json_data and \
            "version" in self.json_data and \
            "creation" in self.json_data

    @staticmethod
    def create():
        return Versions(
            json_data={
                "version": __version__,
                "creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "versions": [
                    {
                        "name": "1.12.2",
                        "jvm": "1.8",
                        "type": "release",
                        "providers": {
                            "vanilla": {
                                "url": "https://launcher.mojang.com/mc/game/1.12.2/server/886945bfb2b978778c3a0288fd7fab09d315b25f/server.jar",
                                "filename": "server.jar",
                                "type": "simple",
                                "data": {}
                            },
                            "spigot": {
                                "url": "https://cdn.getbukkit.org/spigot/spigot-1.12.2.jar",
                                "filename": "spigot-1.12.2.jar",
                                "type": "simple",
                                "data": {}
                            },
                            "forge": {
                                "url": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.12.2-14.23.5.2855/forge-1.12.2-14.23.5.2855-installer.jar",
                                "filename": "",
                                "type": "extended",
                                "data": {
                                    "installer": "forge-1.12.2-14.23.5.2855-installer.jar",
                                    "vanilla_binary": "minecraft_server.1.12.2.jar",
                                    "forge_binary": "forge-1.12.2-14.23.5.2855.jar",
                                    "libraries": "libraries"
                                }
                            }
                        }
                    },
                    {
                        "name": "1.18",
                        "jvm": "1.17",
                        "type": "release",
                        "providers": {
                            "vanilla": {
                                "url": "https://launcher.mojang.com/v1/objects/3cf24a8694aca6267883b17d934efacc5e44440d/server.jar",
                                "filename": "server.jar",
                                "type": "simple",
                                "data": {}
                            }
                        }
                    }
                ]
            }
        )