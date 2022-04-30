from abc import abstractmethod

from ..configuration.configuration import Configuration
from ..credentials.credentials import Credentials

class Storage:

    def __init__(self, configuration: Configuration, credentials: Credentials):
        self.configuration = configuration
        self.credentials = credentials
    
    @abstractmethod
    def send_files(self, compressed_path: str, configuration_path: str):
        pass
    
    @abstractmethod
    def send_configuration(self, configuration_path: str):
        pass

    @abstractmethod
    def get_files(self, compressed_output: str):
        pass

    @abstractmethod
    def get_settings(self, settings_output: str):
        pass