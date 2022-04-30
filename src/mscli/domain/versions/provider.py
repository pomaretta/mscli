from ..configuration.files import MinecraftFiles

class Provider:

    def __init__(self, name: str, version: str, jvm: str, url: str, filename: str, type: str, data: dict):
        self.name = name
        self.version = version
        self.jvm = jvm
        self.url = url
        self.filename = filename
        self.type = type
        self.data = data

        self.files = MinecraftFiles(
            provider=self.name,
            version=self.version,
            filename=self.filename
        )

    def get_files(self) -> MinecraftFiles:
        return self.files

    def __str__(self):
        return f"Provider{{name={self.name}, url={self.url}, filename={self.filename}, type={self.type}, files={self.files}}}"