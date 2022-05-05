import logging

from abc import abstractmethod

class Stage:

    def __init__(self,builder, stage_id: str, name: str, description: str):
        self.builder = builder
        self.stage_id = stage_id
        self.name = name
        self.description = description
        self._completed = False
        self._failed = False
        self._logger = logging.getLogger(__name__)
        self._output = []

    def __log__(self, message: str, *args,level: int = logging.INFO):
        """
        Logs a message with the stage name and stage id.
        """
        self._logger.log(level, f"{self.name}[{self.stage_id}]: {message}", *args)

    def __set_pipeline__(self, pipeline): 
        self.pipeline = pipeline

    def failed(self) -> bool:
        """
        Returns whether the stage failed.
        """
        return self._failed

    def completed(self) -> bool:
        """
        Returns whether the stage completed.
        """
        return self._completed

    def get_output(self) -> list:
        """
        Returns the output of the stage.
        """
        return self._output

    @abstractmethod
    def run(self):
        """
        Run the stage
        """
        pass