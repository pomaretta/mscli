
from abc import abstractmethod

from mscli.domain.versions.provider import Provider
from ..configuration.configuration import Configuration
from ..configuration.registry import Registry
from ..credentials.credentials import Credentials
from ..pipeline.pipeline import Pipeline

import logging
import subprocess
import shutil
import pathlib

class MinecraftBuilder:
    
    def __init__(self, configuration: Configuration, credentials: Credentials, registry: Registry, provider: Provider) -> None:        
        self.configuration = configuration
        self.credentials = credentials
        self.registry = registry
        self.provider = provider

    def __create_process__(self, *args, **kwargs) -> subprocess.Popen:
        """
        Create a process. If debug is enabled, log the command.
        """
        logging.debug("Running command: %s", str.join(' ', args))
        return subprocess.Popen(args=args, **kwargs)

    def __remove_directory__(self, path: str) -> None:
        """
        Remove a directory. If the directory does not exist, do nothing.
        """
        logging.debug("Removing directory: %s", path)
        shutil.rmtree(path, ignore_errors=False)

    def __create_directory__(self, path: str) -> None:
        """
        Create a directory. If the directory already exists, do nothing.
        """
        logging.debug("Creating directory: %s", path)
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

    def __create_directories__(self,*args) -> None:
        """
        Create directories. If the directories already exist, do nothing.
        """
        for path in args:
            self.__create_directory__(path)

    @abstractmethod
    def run(self, id: str) -> Pipeline:
        pass

    @abstractmethod
    def postrun(self, id: str):
        pass

    @abstractmethod
    def import_server(self, registry_object):
        pass

    @abstractmethod
    def update(self, registry_object):
        pass

    @abstractmethod
    def create(self):
        pass