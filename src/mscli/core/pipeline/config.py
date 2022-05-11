import logging
import json
import os

from ...domain.pipeline.stage import Stage
from ...domain.builders.builder import MinecraftBuilder
from datetime import datetime

class CreateConfig(Stage):

    def __init__(self, builder: MinecraftBuilder, stage_id: str, name: str, description: str, id: str, xmx: int, xms: int, ip: str, checksum: list, output: list = None):
        super().__init__(builder, stage_id, name, description)
        self.id = id
        self.xmx = xmx
        self.xms = xms
        self.ip = ip
        self.checksum = checksum
        self.output = output

    def run(self):
        
        if len(self.checksum) == 0:
            logging.error("No checksum provided")
            self._failed = True
            self._completed = True
            return False

        self.checksum = self.checksum[1]

        # Config path
        config_path = os.path.join(self.builder.configuration.get_paths()["files"], self.builder.provider.get_files().get_config())

        config_data = {
            "id": self.id,
            "schema": self.builder.credentials.__type__(),
            "ip": self.ip,
            "jvm": {
                "xmx": self.xmx,
                "xms": self.xms
            },
            "mc": {
                "provider": self.builder.provider.name,
                "version": self.builder.provider.version
            },
            "lastmodified": datetime.utcnow().isoformat(),
            "createdat": datetime.utcnow().isoformat(),
            "checksum": self.checksum,
            "extra": {
                "schema": self.builder.credentials.get_schema()
            }
        }

        logging.info("Creating config file: %s", config_path)

        with open(config_path, "w") as f:
            f.write(json.dumps(config_data))
            f.close()

        if not os.path.exists(config_path):
            logging.error("Config file not found at: %s", config_path)
            self._failed = True
            self._completed = True
            return
        
        logging.info("Config file created at: %s", config_path)
        self._output.append(config_path)
        self._output.append(config_data)
        if self.output is not None:
            self.output.append(config_path)
            self.output.append(config_data)
        self._completed = True
        return True

class UpdateConfigOnRun(Stage):

    def __init__(self, builder, stage_id: str, name: str, description: str,  id: str, xmx: int, xms: int, ip: str, output: list = None):
        super().__init__(builder, stage_id, name, description)
        self.id = id
        self.xmx = xmx
        self.xms = xms
        self.ip = ip
        self.output = output

    def run(self):

        # Config path
        config_path = os.path.join(self.builder.configuration.get_paths()["files"], self.builder.provider.get_files().get_config())

        old_config_data = None
        with open(config_path, "r") as f:
            old_config_data = json.loads(f.read())
            f.close()

        new_config_data = {
            "id": self.id,
            "schema": old_config_data["schema"],
            "ip": self.ip,
            "jvm": {
                "xmx": self.xmx,
                "xms": self.xms
            },
            "mc": {
                "provider": self.builder.provider.name,
                "version": self.builder.provider.version
            },
            "lastmodified": datetime.utcnow().isoformat(),
            "createdat": old_config_data["createdat"],
            "checksum": old_config_data["checksum"],
            "extra": old_config_data["extra"]
        }

        logging.info("Creating config file: %s", config_path)

        with open(config_path, "w") as f:
            f.write(json.dumps(new_config_data))
            f.close()

        logging.info("Config file created at: %s", config_path)
        self._output.append(config_path)
        self._output.append(new_config_data)
        if self.output is not None:
            self.output.append(config_path)
            self.output.append(new_config_data)
        self._completed = True
        return

class UpdateConfig(Stage):

    def __init__(self, builder, stage_id: str, name: str, description: str,  id: str, xmx: int, xms: int, ip: str, checksum: list, output: list = None):
        super().__init__(builder, stage_id, name, description)
        self.id = id
        self.xmx = xmx
        self.xms = xms
        self.ip = ip
        self.checksum = checksum
        self.output = output

    def run(self):

        if len(self.checksum) == 0:
            logging.error("No checksum provided")
            self._failed = True
            self._completed = True
            return False

        self.checksum = self.checksum[1]

        # Config path
        config_path = os.path.join(self.builder.configuration.get_paths()["files"], self.builder.provider.get_files().get_config())

        old_config_data = None
        with open(config_path, "r") as f:
            old_config_data = json.loads(f.read())
            f.close()

        new_config_data = {
            "id": self.id,
            "schema": old_config_data["schema"],
            "ip": self.ip,
            "jvm": {
                "xmx": self.xmx,
                "xms": self.xms
            },
            "mc": {
                "provider": self.builder.provider.name,
                "version": self.builder.provider.version
            },
            "lastmodified": datetime.utcnow().isoformat(),
            "createdat": old_config_data["createdat"],
            "checksum": self.checksum,
            "extra": old_config_data["extra"]
        }

        logging.info("Creating config file: %s", config_path)

        with open(config_path, "w") as f:
            f.write(json.dumps(new_config_data))
            f.close()

        logging.info("Config file created at: %s", config_path)
        self._output.append(config_path)
        self._output.append(new_config_data)
        if self.output is not None:
            self.output.append(config_path)
            self.output.append(new_config_data)
        self._completed = True
        return