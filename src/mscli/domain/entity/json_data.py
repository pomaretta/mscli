
from abc import abstractmethod
import logging
import json

class JSONData:
    
    def __init__(self, json_data):
        self.json_data = json_data

    @abstractmethod
    def validate(self) -> bool:
        pass

    @staticmethod
    def load(configuration_file: str):
        """
        Load data from a JSON file.
        """
        logging.info("Loading data from from %s", configuration_file)
        with open(configuration_file, 'r') as f:
            json_data = json.loads(f.read())
            f.close()
        return JSONData(
            json_data=json_data
        )

    @staticmethod
    def dump(data, configuration_file: str) -> bool:
        """
        Dump data to a JSON file.
        """
        logging.info("Dumping data to %s", configuration_file)
        try:
            with open(configuration_file, 'w') as f:
                f.write(json.dumps(data))
                f.close()
            return True
        except Exception as e:
            logging.error("Failed to dump data to %s", configuration_file)
            raise e
        