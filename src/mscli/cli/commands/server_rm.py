__command__ = "server_rm"

import json
import os
import shutil

from typing import Optional, List
from mscli import __version__
from argparse import ArgumentParser
from datetime import datetime

from mscli.domain.credentials.credentials import Credentials
from mscli.domain.configuration.configuration import Configuration
from mscli.domain.versions.version import Version
from mscli.core.configuration.registry import MinecraftRegistry
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
        description="Export a Minecraft server."
    )

    parser.add_argument(
        'id',
        nargs=1,
        help="The server ID."
    )

    args = parser.parse_args(argv)
    
    id = args.id[0]

    print("[+] Removing server {}".format(id))

    registry_object = registry.get(id)
    
    # Remove files
    server_path = os.path.join(
        configuration.get_paths()["files"],
        registry_object.provider,
        registry_object.version,
        registry_object.id
    )

    if not os.path.isdir(server_path):
        print("[!] Server path does not exist.")
        return True

    # Ask to confirm
    print("[?] Are you sure you want to remove the server? [y/N]")

    if input().lower() != "y":
        print("[!] Cancelled.")
        return True

    # Remove files
    shutil.rmtree(server_path)

    if os.path.isdir(server_path):
        print("[!] Failed to remove server path.")
        return True

    # Remove from Registry
    registry.remove(registry_object=registry_object)

    print("[+] Server {} removed.".format(registry_object.id))

    return True