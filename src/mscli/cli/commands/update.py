__command__ = "update"

import logging
from typing import Optional, List
from argparse import ArgumentParser
from mscli.core.builder.vanilla import VanillaBuilder
from mscli.domain.configuration.registry import RegistryObject

from mscli.domain.credentials.credentials import Credentials
from mscli.domain.configuration.configuration import Configuration
from mscli.domain.versions.version import Version
from mscli.core.builder.forge import ForgeBuilder
from mscli.core.configuration.registry import MinecraftRegistry

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

    # For each object
    for registry_object in registry.get_registry():
        registry_object: RegistryObject

        builder = None

        if registry_object.provider == "forge":
            builder = ForgeBuilder(
                configuration=configuration,
                credentials=credentials,
                registry=registry,
                provider=version.get_version(registry_object.version).get_provider(registry_object.provider)
            )
        elif registry_object.provider == "vanilla":
            builder = VanillaBuilder(
                configuration=configuration,
                credentials=credentials,
                registry=registry,
                provider=version.get_version(registry_object.version).get_provider(registry_object.provider)
            )
        else:
            print("[!] Invalid provider.")
            continue

        print("[+] Updating server {}".format(registry_object.id))

        failed = builder.update(registry_object=registry_object)

        if failed:
            print("[!] Failed to update server.")
            continue

        print("[+] Server {} updated.".format(registry_object.id))

    return True