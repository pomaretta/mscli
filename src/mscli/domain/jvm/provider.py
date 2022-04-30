
from .dist import JVMDistribution

class JVMProvider:

    def __init__(self, name: str, dist: dict):
        self.name = name
        self.dist = dist

    def get_dists(self):
        for name, dist in self.dist.items():
            yield JVMDistribution(
                name=name,
                arch=dist,
            )

    def get_dist(self, name: str):
        for dist in self.get_dists():
            if dist.name == name:
                return dist
        return None