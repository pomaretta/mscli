import logging
import hashlib
import json
import os

from ...domain.pipeline.stage import Stage
from ...domain.builders.builder import MinecraftBuilder
from ...domain.storage.storage import Storage
from datetime import datetime

class GetServerSettings(Stage):

    configuration_name = "settings.json"

    def __init__(self,builder:  MinecraftBuilder, stage_id: str, name: str, description: str, storage: Storage, output: list = []):
        super().__init__(builder, stage_id, name, description)
        self.storage = storage
        self.output = output

    def run(self):
        
        settings_path = os.path.join(
            self.builder.configuration.get_paths()["files"],
            self.builder.provider.get_files().get_tmp(),
            f"settings_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        )

        try:
            self.storage.get_settings(settings_output=settings_path)
        except Exception as e:
            logging.error(e)
            self._failed = True
            self._completed = True
            return

        self._output.append(settings_path)
        if self.output is not None:
            self.output.append(settings_path)
        self._completed = True

class GetServerFiles(Stage):

    files_name = "files.zip"

    def __init__(self,builder:  MinecraftBuilder, stage_id: str, name: str, description: str, storage: Storage, check_data: list, output: list = []):
        super().__init__(builder, stage_id, name, description)
        self.storage = storage
        self.check_data = check_data
        self.output = output

    def run(self):
        
        if len(self.check_data) == 0:
            logging.error("No check data provided")
            self._failed = True
            self._completed = True
            return

        check_data = self.check_data[0]
        files_path = os.path.join(
            self.builder.configuration.get_paths()["files"],
            self.builder.provider.get_files().get_tmp(),
            f"files_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.zip"
        )

        try:
            self.storage.get_files(compressed_output=files_path)
        except Exception as e:
            logging.error(e)
            self._failed = True
            self._completed = True
            return

        if not os.path.exists(files_path):
            logging.error("File not found")
            self._failed = True
            self._completed = True
            return

        checksum = None
        with open(files_path, 'rb') as f:
            data = f.read()
            checksum = hashlib.md5(data).hexdigest()
            f.close()
        
        if checksum != check_data["checksum"]:
            logging.error("Checksum does not match")
            self._failed = True
            self._completed = True
            return

        self._output.append(files_path)
        if self.output is not None:
            self.output.append(files_path)
        self._completed = True

class ReplaceFile(Stage):

    def __init__(self, builder: MinecraftBuilder, stage_id: str, name: str, description: str, old_file: str, new_file: list):
        super().__init__(builder, stage_id, name, description)
        self.old_file = old_file
        self.new_file = new_file

    def run(self):
        
        if len(self.new_file) == 0:
            logging.error("No old file provided")
            self._failed = True
            self._completed = True
            return

        new_file = self.new_file[0]
        if not os.path.exists(new_file):
            logging.error("File not found")
            self._failed = True
            self._completed = True
            return
        
        os.replace(new_file, self.old_file)

        self._completed = True
        return

class MoveFile(Stage):

    def __init__(self, builder, stage_id: str, name: str, description: str, new_path: str, file: list, output: list = None):
        super().__init__(builder, stage_id, name, description)
        self.new_path = new_path
        self.file = file
        self.output = output
    
    def run(self):
        
        if len(self.file) == 0:
            logging.error("No file provided")
            self._failed = True
            self._completed = True
            return
    
        file = self.file[0]

        if not os.path.isdir(self.new_path):
            logging.error("Path does not exist")
            self._failed = True
            self._completed = True
            return
        
        new_file_path = os.path.join(
            self.new_path
            ,os.path.basename(file)
        )
        os.replace(
            file,
            new_file_path
        )

        if not os.path.exists(new_file_path):
            logging.error("New created file not found")
            self._failed = True
            self._completed = True
            return

        self._output.append(self.new_path)
        if self.output is not None:
            self.output.append(self.new_path)
        self._completed = True
        return


class CheckSettings(Stage):

    configuration_name = "settings.json"

    def __init__(self,builder:  MinecraftBuilder, stage_id: str, name: str, description: str, cloud_settings: list, check_cloud: bool = True, output: list = []):
        super().__init__(builder, stage_id, name, description)
        self.cloud_settings = cloud_settings
        self.check_cloud = check_cloud
        self.output = output

    def run(self):
        
        if len(self.cloud_settings) == 0:
            logging.error("No cloud settings found")
            self._failed = True
            self._completed = True
            return

        cloud_settings = self.cloud_settings[0]
        settings_path = os.path.join(
            self.builder.configuration.get_paths()["files"],
            self.builder.provider.get_files().get_config()
        )

        local_data, cloud_data = None, None
        if self.check_cloud:
            with open(settings_path, 'r') as f:
                local_data = json.loads(f.read())
                f.close()
        with open(cloud_settings, 'r') as f:
            cloud_data = json.loads(f.read())
            f.close()

        local_lastmodified = None
        if self.check_cloud:
            local_lastmodified = datetime.fromisoformat(
                local_data["lastmodified"]
            )
        cloud_lastmodified = datetime.fromisoformat(
            cloud_data['lastmodified']
        )

        if self.check_cloud and cloud_lastmodified == local_lastmodified:
            logging.info("Cloud settings are equal to local settings")
            self._output.append({
                "ip": cloud_data['ip'],
                "lastmodified": cloud_data['lastmodified'],
                "checksum": cloud_data["checksum"],
                "newer": False
            })
            if self.output is not None:
                self.output.append(self._output[0])
            self._failed = True
            self._completed = True

        if self.check_cloud and cloud_lastmodified < local_lastmodified:
            logging.error("Local settings are newer than cloud settings")
            self._output.append({
                "ip": local_data['ip'],
                "lastmodified": local_data['lastmodified'],
                "checksum": local_data["checksum"],
                "newer": False
            })
            if self.output is not None:
                self.output.append(self._output[0])
            self._failed = True
            self._completed = True
            return

        logging.info("Cloud settings are newer than local settings")
        self._output.append({
            "ip": cloud_data['ip'],
            "lastmodified": cloud_data['lastmodified'],
            "checksum": cloud_data["checksum"],
            "newer": True
        })
        if self.output is not None:
            self.output.append(self._output[0])
        self._completed = True
        return
