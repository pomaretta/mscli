from abc import abstractmethod
import logging
import os

from ..credentials.credentials import Credentials
from ..entity.json_data import JSONData
from datetime import datetime
from ... import __version__

class RegistryObject:

    def __init__(
        self,
        id: str,
        ip: str,
        schema: str,
        provider: str,
        version: str,
        path: str,
        running: bool = False,
        update: bool = False,
        creation: datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        lastmodified: datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        extra: dict = {},
        pid: int = None
    ):
        self.id = id
        self.ip = ip
        self.schema = schema
        self.provider = provider
        self.version = version
        self.path = path
        self.running = running
        self.update = update
        self.creation = creation
        self.lastmodified = lastmodified
        self.extra = extra
        self.pid = pid

    def to_json(self):
        return {
            "id": self.id,
            "ip": self.ip,
            "schema": self.schema,
            "provider": self.provider,
            "version": self.version,
            "path": self.path,
            "running": self.running,
            "update": self.update,
            "creation": self.creation,
            "lastmodified": self.lastmodified,
            "extra": self.extra,
            "pid": self.pid
        }

class Registry(JSONData):

    def __get_registry_objects__(self):
        for registry_object in self.json_data["registry"]:
            yield RegistryObject(**registry_object)

    def __init__(self, json_data, path: str = os.path.expanduser("~/.mscli/config/registry.json")):
        super().__init__(json_data)
        self.version = self.get_version()
        self.creation = self.get_creation()
        self.lastmodified = self.get_lastmodified()
        self.path = path

    def get_version(self) -> str:
        """
        Returns the version of the registry
        """
        return self.json_data["version"]

    def get_creation(self) -> str:
        """
        Returns the creation time of the registry
        """
        return self.json_data["creation"]

    def get_lastmodified(self) -> str:
        """
        Returns the last modified time of the registry
        """
        return self.json_data["lastmodified"]

    def get_registry(self) -> list:
        """
        Returns a list of registry objects
        """
        return list(self.__get_registry_objects__())

    def save(self) -> None:
        """
        Saves the registry to the file
        """
        self.json_data["lastmodified"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not self.dump(
            self.json_data,
            self.path
        ):
            logging.error("Could not save registry")
            raise IOError("Could not save registry")

    def validate(self) -> bool:
        return "version" in self.json_data and \
            "creation" in self.json_data and \
            "lastmodified" in self.json_data and \
            "registry" in self.json_data

    @abstractmethod
    def add(self, registry_object: RegistryObject) -> None:
        """
        Adds a registry object to the registry
        """
        pass

    @abstractmethod
    def remove(self, registry_object: RegistryObject) -> None:
        """
        Removes a registry object from the registry
        """
        pass

    @abstractmethod
    def update(self, registry_object: RegistryObject) -> None:
        """
        Updates a registry object in the registry
        """
        pass

    @abstractmethod
    def fetch(self) -> None:
        """
        Fetches the registry from the remote server
        """
        pass

    @staticmethod
    def create():
        """
        Create a new configuration file with default version data.
        """
        logging.info("Creating new configuration.")
        return Registry(
            json_data={
                "version": __version__,
                "creation": datetime.now().isoformat(),
                "lastmodified": datetime.now().isoformat(),
                "registry": []
            }
        )