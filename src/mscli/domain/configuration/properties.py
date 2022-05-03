from abc import abstractmethod
import logging
import configparser
from typing import List

from ..entity.json_data import JSONData

class Properties(JSONData):

    @staticmethod
    def __properties_to_json__(lines: List[str]) -> dict:
        """
        Reads the properties from the file and returns a dictionary.
        """
        keys = {}
        for line in lines:
            line.lstrip()
            if not line.startswith('#'):
                line = line.replace('\n', '').replace('\r', '')
                keyvalue = line.split('=', 1)
                keys[keyvalue[0]] = keyvalue[1]
        return keys

    @staticmethod
    def __json_to_properties__(json: dict):
        """
        Writes the properties to the file.
        """
        for key, value in json.items():
            yield key + '=' + value + '\n'

    @abstractmethod
    def from_properties(self, properties_file: str):
        pass

    @abstractmethod
    def save(self, output_file: str):
        pass

    @abstractmethod
    def to_dict(self):
        pass