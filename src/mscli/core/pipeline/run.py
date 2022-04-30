import subprocess
import mcstatus
import logging
import os

from mscli.core.configuration.registry import MinecraftRegistry

from ...domain.pipeline.stage import Stage
from ...domain.builders.builder import MinecraftBuilder

class RunMinecraftBinary(Stage):

    def __init__(self,builder:  MinecraftBuilder, stage_id: str, name: str, description: str, files_path: str, binary_name: str, xmx: int, xms: int, output: list = None):
        super().__init__(builder, stage_id, name, description)
        self.files_path = files_path
        self.binary_name = binary_name
        self.xmx = xmx
        self.xms = xms
        self.output = output

    def run(self):
        
        logging.info("Running server")

        jvm_version = self.builder.provider.jvm
        
        file = os.path.join(
            self.files_path,
            self.binary_name
        )
        if not os.path.exists(file):
            logging.error("Binary file not found")
            self._failed = True
            self._completed = True
            return

        jvm_provider: dict = self.builder.configuration.get_jvms()['liberica']
        jre = None
        for n, d in jvm_provider.items():
            if n == jvm_version:
                jre = d['jvm_path']
                break

        if jre is None:
            logging.error("JRE not found")
            self._failed = True
            self._completed = True
            return

        command = f"{jre} -Xmx{self.xmx}M -Xms{self.xms}M -jar {file} nogui"

        # process = self.builder.__create_process__(
        #     jre,
        #     # '-Xmx',
        #     # f'{self.xmx}M',
        #     # '-Xms',
        #     # f'{self.xms}M',
        #     '-jar',
        #     file,
        #     'nogui',
        #     cwd=self.files_path,
        #     stdin=subprocess.PIPE,
        #     stdout=subprocess.PIPE,
        #     # stderr=subprocess.PIPE
        # )
    
        # self._output.append(process)
        # self._output.append(f"{jre} -jar {file} nogui")
        self._output.append(command)
        self._output.append(self.files_path)
        if self.output is not None:
            # self.output.append(process)
            # self.output.append(f"{jre} -jar {file} nogui")
            self.output.append(command)
            self.output.append(self.files_path)
        self._completed = True
        return

class CheckUpdateAndRunning(Stage):

    def __init__(self, builder, stage_id: str, name: str, description: str, id: str):
        super().__init__(builder, stage_id, name, description)
        self.id = id

    def run(self):

        # Update registry object
        registry: MinecraftRegistry = self.builder.registry
        registry.fetch_object(self.id, self.builder.configuration, self.builder.credentials)

        # Check if the server has to be updated
        obj = registry.get(registry_id=self.id)
        if obj.update:
            logging.error("Server has to be updated")
            self._failed = True
            self._completed = True
            return
        
        # Check if the server is running
        try:
            server = mcstatus.JavaServer.lookup(obj.ip)
            server.status()
            logging.error("Server is already running")
            self._failed = True
            self._completed = True
        except:
            pass

        self._completed = True
        return