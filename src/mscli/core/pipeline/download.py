import urllib.request as request
import logging
import os

from ...domain.pipeline.stage import Stage
from ...domain.builders.builder import MinecraftBuilder

class DownloadBinaryFile(Stage):

    def __init__(self,builder:  MinecraftBuilder, stage_id: str, name: str, description: str, override_tmp: str = None, override_url: str = None, override_filename: str = None, output: list = None):
        super().__init__(builder, stage_id, name, description)
        self.override_tmp = override_tmp
        self.override_url = override_url
        self.override_filename = override_filename
        self.output = output

    def run(self):
        
        # Used Directories
        tmp = os.path.join(self.builder.configuration.get_paths()["files"], self.builder.provider.get_files().get_tmp())
        if self.override_tmp is not None:
            self.__log__(f"Overriding tmp directory with {self.override_tmp}")
            tmp = self.override_tmp

        # Url for download the file
        binary_url = self.builder.provider.url
        if self.override_url is not None:
            self.__log__(f"Overriding url with {self.override_url}")
            binary_url = self.override_url
        
        # Filename for the file
        download_filename = self.builder.provider.filename
        if self.override_filename is not None:
            self.__log__(f"Overriding filename with {self.override_filename}")
            download_filename = self.override_filename

        download_path = os.path.join(tmp, download_filename)

        # Download the file
        path, _ = request.urlretrieve(
            binary_url,
            download_path
        )

        if not os.path.exists(path):
            self._failed = True
            self.__log__(f"File not found on path: {path}", level=logging.ERROR)
            self._completed = True
            return

        self.__log__(f"Downloaded file to {path}")
        self._output.append(path)
        if self.output is not None:
            self.output.append(path)
        self._completed = True
        return
        
