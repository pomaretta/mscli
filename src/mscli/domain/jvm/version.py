from .provider import JVMProvider

class JVMVersion:
    
    name: str
    providers: list

    def __init__(self, name: str, providers: list):
        self.name = name
        self.providers = providers
    
    def get_providers(self):
        for provider, data in self.providers.items():
            yield JVMProvider(
                name=provider,
                dist=data
            )
    
    def get_provider(self, name: str):
        for provider in self.get_providers():
            if provider.name == name:
                return provider
        return None