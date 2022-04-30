import logging

from ...domain.pipeline.stage import Stage
from ...domain.builders.builder import MinecraftBuilder
from ...domain.storage.storage import Storage

class UploadFiles(Stage):

    def __init__(self,builder:  MinecraftBuilder, stage_id: str, name: str, description: str, storage: Storage, compressed_path: list, configuration_path: list):
        super().__init__(builder, stage_id, name, description)
        self.storage = storage
        self.compressed_path = compressed_path
        self.configuration_path = configuration_path

    def run(self):
        
        if len(self.compressed_path) == 0:
            logging.error("No compressed path provided")
            self._failed = True
            self._completed = True
            return False

        if len(self.configuration_path) == 0:
            logging.error("No configuration path provided")
            self._failed = True
            self._completed = True
            return False

        compressed = self.compressed_path[0]
        configuration = self.configuration_path[0]

        try:
            self.storage.send_files(
                compressed_path=compressed,
                configuration_path=configuration
            )
        except Exception as e:
            logging.error("Failed to upload files", e)
            self._failed = True
            self._completed = True
            return
        
        self._completed = True

class UploadConfig(Stage):

    def __init__(self,builder:  MinecraftBuilder, stage_id: str, name: str, description: str, storage: Storage, configuration_path: list):
        super().__init__(builder, stage_id, name, description)
        self.storage = storage
        self.configuration_path = configuration_path

    def run(self):
        
        if len(self.configuration_path) == 0:
            logging.error("No configuration path provided")
            self._failed = True
            self._completed = True
            return False

        configuration = self.configuration_path[0]

        try:
            self.storage.send_configuration(
                configuration_path=configuration
            )
        except Exception as e:
            logging.error("Failed to upload files", e)
            self._failed = True
            self._completed = True
            return
        
        self._completed = True