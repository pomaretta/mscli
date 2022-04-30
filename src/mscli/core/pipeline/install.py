import subprocess
import logging
import os

from ...domain.pipeline.stage import Stage
from ...domain.builders.builder import MinecraftBuilder

class ExtractForgeFile(Stage):

    def __init__(self,builder:  MinecraftBuilder, stage_id: str, name: str, description: str, file_path: list, output_path: str, output: list = None):
        super().__init__(builder, stage_id, name, description)
        self.file_path = file_path
        self.output_path = output_path
        self.output = output

    def run(self):
        
        logging.info("Installing Forge")
        
        if len(self.file_path) == 0:
            logging.error("No file path provided")
            self._failed = True
            self._completed = True
            return False
        
        file = self.file_path[0]

        if not os.path.exists(file):
            logging.error("Forge file not found")
            self._failed = True
            self._completed = True
            return

        jre = self.builder.configuration.get_jre()
        if jre is None:
            logging.error("JRE not found")
            self._failed = True
            self._completed = True
            return

        process = self.builder.__create_process__(
            jre,
            '-jar',
            file,
            '--installServer',
            cwd=self.output_path,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT
        )

        if process.wait() != 0:
            logging.error("Failed to install forge")
            self._failed = True
            self._completed = True
            return

        self._output.append(self.output_path)
        if self.output is not None:
            self.output.append(self.output_path)
        self._completed = True
        return

class WriteEULA(Stage):

    def __init__(self,builder:  MinecraftBuilder, stage_id: str, name: str, description: str, input_path: list):
        super().__init__(builder, stage_id, name, description)
        self.input_path = input_path

    def run(self):
        
        logging.info("Writting EULA")
        
        if len(self.input_path) == 0:
            logging.error("No file path provided")
            self._failed = True
            self._completed = True
            return False
        
        file = os.path.join(
            self.input_path[0],
            'eula.txt'
        )

        with open(file, 'w') as f:
            f.write('eula=true')
            f.close()
        
        self._completed = True
        return