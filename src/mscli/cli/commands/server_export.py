__command__ = "server_export"

import json
import os
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

    print("[+] Exporting server {}".format(id))

    registry_object = registry.get(id)
    registry_object.path = ""
    
    dt = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    data = {
        "version": __version__,
        "aws_user_id": credentials.get_aws_access_key_id(),
        "creation": dt,
        "object": registry_object.to_json()
    }

    data_prefix = os.path.join(
        configuration.get_paths()["home"],
        "export"
    )

    create_directories(data_prefix)

    data_path = os.path.join(
        data_prefix,
        f"{id}_{dt}.json"
    )

    with open(data_path, "w") as f:
        f.write(json.dumps(data))
        f.close()

    if not os.path.exists(data_path):
        print("[!] Failed to export server.")
        return True

    print("[+] Exported server on {}".format(data_path))

    return True