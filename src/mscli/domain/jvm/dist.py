
from .arch import JVMArch

class JVMDistribution:

    def __init__(self, name: str, arch: dict):
        self.name = name
        self.arch = arch

    def get_archs(self):
        for name, arch in self.arch.items():
            yield JVMArch(
                name=name,
                url=arch['url'],
                checksum=arch['checksum'],
            )

    def get_arch(self, name: str):
        for arch in self.get_archs():
            if arch.name == name:
                return arch
        return None