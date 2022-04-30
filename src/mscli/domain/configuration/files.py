import os

class MinecraftFiles:

    def __init__(
        self, provider: str, version: str,
        filename: str
    ) -> None:
        
        self.id = None
        self.provider = provider
        self.version = version
        self.filename = filename
    
        self.prefix = os.path.join(
            self.provider,
            self.version
        )

        self.tmp = os.path.join(
            self.prefix,
            'tmp'
        )

        self.serverfiles = os.path.join(
            self.prefix,
            'files'
        )

        self.serversettings = os.path.join(
            self.prefix,
            'settings.json'
        )

    def set_id(self, id: str) -> None:
        self.id = id

    def get_root(self) -> str:
        return self.prefix
    
    def get_tmp(self) -> str:
        if self.id is None:
            return self.tmp
        else:
            return os.path.join(
                self.prefix,
                self.id,
                'tmp'
            )

    def get_src(self) -> str:
        if self.id is None:
            return self.serverfiles
        else:
            return os.path.join(
                self.prefix,
                self.id,
                'files'
            )
    
    def get_config(self) -> str:
        if self.id is None:
            return self.serversettings
        else:
            return os.path.join(
                self.prefix,
                self.id,
                'settings.json'
            )