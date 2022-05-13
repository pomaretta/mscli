import mcstatus
import logging
import json
import os

from ...domain.configuration.registry import Registry
from ...domain.configuration.registry import RegistryObject
from ...domain.configuration.configuration import Configuration
from ...domain.credentials.credentials import Credentials
from ...domain.storage.storage import Storage
from ...core.storage.s3 import S3Storage
from ...core.storage.ftp import FTPStorage
from ...core.storage.sftp import SFTPStorage

from datetime import datetime

class MinecraftRegistry(Registry):
    """
    Minecraft Registry
    """

    def __fetch_object__(self, registry_object: RegistryObject, configuration: Configuration, credentials: Credentials):

        # TODO: Check if the settings of the registry object are updated.
        id = registry_object.id
        local_lastmodified = registry_object.lastmodified
    
        # Get cloud update
        settings_path = os.path.join(
            configuration.get_paths()['cache'],
            f'settings_{id}_{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.tmp.json'
        )

        storage: Storage = None
        if credentials.__type__() == "aws":
            storage = S3Storage(
                configuration=configuration,
                credentials=credentials,
                provider=None,
                id=id
            )
        elif credentials.__type__() == "ftp":
            storage = FTPStorage(
                configuration=configuration,
                credentials=credentials,
                provider=None,
                id=id
            )
        elif credentials.__type__() == "sftp":
            storage = SFTPStorage(
                configuration=configuration,
                credentials=credentials,
                provider=None,
                id=id
            )
        
        storage.get_settings(settings_path)

        if not os.path.exists(settings_path):
            raise Exception("Settings path doesn't exist for ID {}".format(id))
        
        cloud_data = None
        with open(settings_path, 'r') as f:
            cloud_data = json.loads(f.read())
            f.close()
        cloud_lastmodified = cloud_data['lastmodified']

        # Compare cloud and local
        if cloud_lastmodified > local_lastmodified:
            # Update local
            registry_object.update = True
            self.update(registry_object)
            logging.info("Updated registry object: %s", id)

        # TODO: Check if the server is running.
        server_ip = cloud_data['ip'] # If is the same, it will be the same server else will be other ip.

        running = True
        try:
            remote_server = mcstatus.JavaServer.lookup(server_ip)
            remote_server.status()
        except:
            running = False

        registry_object.ip = server_ip

        # Avoid local override on port don't opened.
        if registry_object.pid is not None:
            registry_object.running = registry_object.running
        else:
            registry_object.running = running
        self.update(registry_object)

    def get(self, registry_id: str) -> RegistryObject:
        for registry_object in self.__get_registry_objects__():
            if registry_object.id == registry_id:
                return registry_object
        return None

    def add(self, registry_object: RegistryObject):
        if not isinstance(registry_object, RegistryObject):
            raise TypeError("registry_object must be of type RegistryObject")
        for registry_object_ in self.__get_registry_objects__():
            if registry_object_.id == registry_object.id:
                raise ValueError("registry_object already exists")
        self.json_data["registry"].append(registry_object.to_json())
        self.save()

    def remove(self, registry_object: RegistryObject):
        if not isinstance(registry_object, RegistryObject):
            raise TypeError("registry_object must be of type RegistryObject")
        for registry_object_ in self.__get_registry_objects__():
            if registry_object_.id == registry_object.id:
                self.json_data["registry"].remove(registry_object.to_json())
                self.save()
                return
        raise ValueError("registry_object does not exist")

    def update(self, registry_object: RegistryObject):
        if not isinstance(registry_object, RegistryObject):
            raise TypeError("registry_object must be of type RegistryObject")
        for registry_object_ in self.__get_registry_objects__():
            if registry_object_.id == registry_object.id:
                self.json_data["registry"].remove(registry_object_.to_json())
                self.json_data["registry"].append(registry_object.to_json())
                self.save()
                return
        raise ValueError("registry_object does not exist")

    def fetch_object(self, id, configuration: Configuration, credentials: Credentials) -> None:
        self.__fetch_object__(self.get(id), configuration, credentials)

    def fetch(self, configuration: Configuration, credentials: Credentials) -> None:
        # TODO: Fetch registry
        # Obtain info about running servers
        for registry_object in self.__get_registry_objects__():
            try:
                self.__fetch_object__(registry_object, configuration, credentials)
            except Exception as e:
                logging.warning("Failed to fetch registry object: %s", registry_object.id)