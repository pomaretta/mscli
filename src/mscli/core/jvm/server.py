import subprocess

from ...domain.configuration.configuration import Configuration
from ...domain.configuration.server import Server

class MinecraftServer:

    def __init__(self, process: subprocess.Popen, configuration: Configuration, server: Server) -> None:
        self.process = process
        self.configuration = configuration
        self.server = server

    def is_running(self) -> bool:
        return self.process.poll() is None

    def send(self, input: str) -> None:
        if not self.is_running():
            raise RuntimeError("Minecraft server is not running")
        self.process.stdin.write("{}\n".format(input).encode('utf-8'))
        self.process.stdin.flush()

    def pid(self):
        return self.process.pid

    def kill(self):
        self.process.kill()
    
    def terminate(self):
        self.process.terminate()