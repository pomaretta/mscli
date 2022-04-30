__command__ = "version"

import logging

from typing import Optional, List

from mscli.core.configuration.registry import MinecraftRegistry
from mscli.domain.configuration.configuration import Configuration
from mscli.domain.configuration.registry import RegistryObject
from mscli.domain.credentials.credentials import Credentials
from mscli.domain.versions.version import Version

def main(
    argv: Optional[List[str]] = None
    ,pwd: str = None
    ,**kwargs
) -> bool:

    if kwargs["credentials"] is None:
        print("[!] No credentials provided.")
        return True
    if kwargs["configuration"] is None:
        print("[!] No configuration provided.")
        return True
    if kwargs["registry"] is None:
        print("[!] No registry provided.")
        return True
    if kwargs["version"] is None:
        print("[!] No version provided.")
        return True

    credentials: Credentials
    configuration: Configuration
    registry: MinecraftRegistry
    version: Version

    credentials = kwargs["credentials"]
    configuration = kwargs["configuration"]
    registry = MinecraftRegistry(
        json_data=kwargs["registry"].json_data
    )
    version = kwargs["version"]

    if not credentials.validate():
        print("[!] Invalid credentials data.")
        return True
    if not configuration.validate():
        print("[!] Invalid configuration data.")
        return True
    if not registry.validate():
        print("[!] Invalid registry data.")
        return True
    if not version.validate():
        print("[!] Invalid version data.")
        return True

    logging.info("updating registry")
    registry.fetch(
        configuration=configuration
        ,credentials=credentials
    )

    print("{0:35s} {1:15s} {2:15s} {3:15s} {4:15s}".format("ID", "PROVIDER", "IP", "IS RUNNING", "NEEDS UPDATE"))

    for obj in registry.get_registry():
        obj: RegistryObject
        print(
            f"{obj.id:35s} {f'{obj.provider}/{obj.version}':15s} {obj.ip:15s} {str(obj.running):15s} {str(obj.update):15s}"
        )

    return True