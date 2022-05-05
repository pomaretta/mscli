from logging import Logger
from .stage import Stage

class Pipeline:

    def __init__(self, pipeline_id: str, name: str, stages: list = []):
        self.pipeline_id = pipeline_id
        self.name = name
        self.stages = stages
        self._completed = False
        self._failed = False
        self._output = []
    
    def add_stage(self, stage: Stage):
        stage.__set_pipeline__(self)
        self.stages.append(stage)

    def get_logs(self) -> Logger:
        for stage in self.stages:
            stage: Stage
            yield stage._logger

    def run(self) -> bool:
        for stage in self.stages:
            stage: Stage
            stage.run()
            if stage._failed:
                self._failed = True
                self._completed = True
                return False
        self._completed = True
        return True
