import logging
import json
import os

from ...domain.pipeline.stage import Stage
from ...domain.configuration.registry import RegistryObject
from ...core.configuration.registry import MinecraftRegistry
from datetime import date, datetime

class AddToRegistry(Stage):

    def __init__(self, builder, stage_id: str, name: str, description: str, id: str, local_path: list, config_data: list):
        super().__init__(builder, stage_id, name, description)
        self.id = id
        self.local_path = local_path
        self.config_data = config_data

    def run(self):
        
        if len(self.local_path) == 0:
            logging.error("No local path specified")
            self._failed = True
            self._completed = True
            return False

        if len(self.config_data) == 0:
            logging.error("No config data specified")
            self._failed = True
            self._completed = True
            return False

        registry: MinecraftRegistry
        registry = self.builder.registry
        path = self.local_path[0]
        config_data = self.config_data[1]

        registry_object = RegistryObject(
            id=self.id,
            ip=self.builder.configuration.get_ip(),
            schema=self.builder.credentials.__type__(),
            provider=self.builder.provider.name,
            version=self.builder.provider.version,
            path=path,
            lastmodified=config_data["lastmodified"],
            creation=config_data["createdat"],
            extra=config_data["extra"]
        )

        registry.add(registry_object)

        self._completed = True

class AddExistingObjectToRegistry(Stage):

    def __init__(self, builder, stage_id: str, name: str, description: str, existing_object: RegistryObject, local_path: list):
        super().__init__(builder, stage_id, name, description)
        self.existing_object = existing_object
        self.local_path = local_path
    
    def run(self):
        
        if len(self.local_path) == 0:
            logging.error("No local path specified")
            self._failed = True
            self._completed = True
            return False

        registry: MinecraftRegistry
        registry = self.builder.registry
        path = self.local_path[0]

        self.existing_object.path = path
        self.existing_object.lastmodified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        registry.add(self.existing_object)

        self._completed = True

class UpdateRegistryObject(Stage):

    def __init__(self, builder, stage_id: str, name: str, description: str, existing_object: RegistryObject, config_path: str):
        super().__init__(builder, stage_id, name, description)
        self.existing_object = existing_object
        self.config_path = config_path

    def run(self):

        registry: MinecraftRegistry = self.builder.registry
    
        config_data = None
        with open(self.config_path, "r") as f:
            config_data = json.loads(f.read())
            f.close()
        
        self.existing_object.ip = config_data["ip"]
        self.existing_object.lastmodified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.existing_object.update = False

        registry.update(self.existing_object)

        self._completed = True

class RunUpdateRegistry(Stage):

    def __init__(self, builder, stage_id: str, name: str, description: str, registry_object: RegistryObject, running: bool):
        super().__init__(builder, stage_id, name, description)
        self.registry_object = registry_object
        self.running = running

    def run(self):

        self.registry_object.running = self.running
        self.registry_object.lastmodified = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.builder.registry.update(self.registry_object)
        self._completed = True