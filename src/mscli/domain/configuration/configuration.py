import logging
import os
import platform
import urllib.request

from ...shared.files import create_directories
from ..entity.json_data import JSONData
from datetime import datetime
from ... import __version__

class Configuration(JSONData):

    def __init__(self, json_data):
        super().__init__(json_data)
        for _, path in self.get_paths().items():
            create_directories(path)

    def get_paths(self):
        return {
            "home": self.json_data['path'],
            "jvm": os.path.join(self.json_data['path'], "jvm"),
            "config": os.path.join(self.json_data['path'], "config"),
            "log": os.path.join(self.json_data['path'], "log"),
            "cache": os.path.join(self.json_data['path'], "cache"),
            "files": os.path.join(self.json_data['path'], "files"),
        }

    def get_config_file(self) -> str:
        return os.path.join(self.get_paths()['config'], "config.json")

    def get_timestamp(self) -> str:
        return self.json_data['timestamp']

    def get_version(self) -> str:
        return self.json_data['version']

    def get_os(self) -> str:
        return self.json_data['os']
    
    def get_arch(self) -> str:
        return self.json_data['arch']

    def get_path(self) -> str:
        return self.json_data['path']

    def get_ip(self) -> str:
        return self.json_data['ip']

    def validate(self) -> bool:
        return "timestamp" in self.json_data and \
            "os" in self.json_data and \
            "arch" in self.json_data and \
            "version" in self.json_data and \
            "path" in self.json_data and \
            "ip" in self.json_data

    def get_jre(self) -> str:
        if not "jre" in self.json_data:
            return None
        return self.json_data['jre']

    def get_jre_from_version(self, provider: str, version: str) -> dict:
        jvm = self.get_version(provider, version)
        if jvm is None:
            return None
        return jvm['jvm_path']

    def get_version(self, provider: str, version: str) -> dict:
        if not "jvm" in self.json_data:
            return None
        if not provider in self.json_data['jvm']:
            return None
        if not version in self.json_data['jvm'][provider]:
            return None
        return self.json_data['jvm'][provider][version]

    def get_versions(self, provider: str) -> dict:
        if not "jvm" in self.json_data:
            return None
        if not provider in self.json_data['jvm']:
            return None
        return self.json_data['jvm'][provider]

    def get_jvms(self) -> dict:
        if not "jvm" in self.json_data:
            return None
        return self.json_data['jvm']

    def is_jvm_installed(self, provider: str, version: str) -> dict:
        if not "jvm" in self.json_data:
            return False
        if not provider in self.json_data['jvm']:
            return False
        if not version in self.json_data['jvm'][provider]:
            return False
        return self.json_data['jvm'][provider][version]['installed']

    def register_jvm(self, 
        version: str,
        provider: str,
        dist: str,
        arch: str,
        home_path: str,
        jvm_path: str,
        installed: bool,
    ):
        if not "jvm" in self.json_data:
            self.json_data['jvm'] = {}
        if not provider in self.json_data['jvm']:
            self.json_data['jvm'][provider] = {}
        if not version in self.json_data['jvm'][provider]:
            self.json_data['jvm'][provider][version] = {}
        self.json_data['jvm'][provider][version] = {
            "dist": dist,
            "arch": arch,
            "home_path": home_path,
            "jvm_path": jvm_path,
            "installed": installed,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "creation": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.json_data['jre'] = jvm_path

    @staticmethod
    def create(
        default_path: str = os.path.expanduser("~/.mscli"),
    ):
        """
        Create a new configuration file with default version data.
        """
        logging.info("Creating new configuration.")
        return Configuration(
            json_data={
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "os": "osx" if platform.system().lower() == "darwin" else platform.system().lower(),
                "arch": "x86" if platform.machine().lower() == "amd64" else "arm",
                "version": __version__,
                "path": default_path,
                "ip": urllib.request.urlopen("https://api.ipify.org").read().decode("utf-8"),
            }
        )