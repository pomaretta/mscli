__command__ = "server_import"

import json
import os
from typing import Optional, List
from mscli import __version__
from argparse import ArgumentParser
from datetime import datetime
from mscli.core.builder.forge import ForgeBuilder
from mscli.core.builder.vanilla import VanillaBuilder

from mscli.domain.credentials.credentials import Credentials
from mscli.domain.configuration.configuration import Configuration
from mscli.domain.versions.version import Version
from mscli.core.configuration.registry import MinecraftRegistry, RegistryObject
from mscli.shared.files import create_directories

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
    
    parser = ArgumentParser(
        description="Import a Minecraft server."
    )

    parser.add_argument(
        'import_file',
        nargs=1,
        help='The file to import.'
    )

    args = parser.parse_args(argv)
    
    file = args.import_file[0]

    if not os.path.exists(file):
        print("[!] File does not exist.")
        return True
    
    file_data = None
    with open(file, "r") as f:
        file_data = json.loads(f.read())
        f.close()
    
    if "version" not in file_data and \
        "aws_user_id" not in file_data and \
        "creation" not in file_data and \
        "object" not in file_data:
        print("[!] Invalid file.")
        return True
    
    object_id = file_data["object"]["id"]
    object_provider = file_data["object"]["provider"]
    object_version = file_data["object"]["version"]

    object_data = registry.get(object_id)
    if object_data is not None:
        print("[!] Object already exists.")
        return True

    builder = None
    if object_provider == "forge":
        builder = ForgeBuilder(
            configuration=configuration,
            credentials=credentials,
            registry=registry,
            provider=version.get_version(object_version).get_provider(object_provider)
        )
    elif object_provider == "vanilla":
        builder = VanillaBuilder(
            configuration=configuration,
            credentials=credentials,
            registry=registry,
            provider=version.get_version(object_version).get_provider(object_provider)
        )
    else:
        print("[!] Invalid provider.")
        return True

    builder.import_server(
        RegistryObject(
            **file_data["object"]
        )
    )

    print("[+] Server {} imported.".format(object_id))

    return True