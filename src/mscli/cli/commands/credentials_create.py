__command__ = "credentials_create"

import os

from typing import Optional, List
from mscli import __version__
from argparse import ArgumentParser

from mscli.domain.credentials.credentials import Credentials
from mscli.domain.configuration.configuration import Configuration
from mscli.domain.versions.version import Version
from mscli.core.configuration.registry import MinecraftRegistry

def main(
    argv: Optional[List[str]] = None
    ,pwd: str = None
    ,**kwargs
) -> bool:
    
    if kwargs["configuration"] is None:
        print("[!] No configuration provided.")
        return True
    if kwargs["registry"] is None:
        print("[!] No registry provided.")
        return True
    if kwargs["version"] is None:
        print("[!] No version provided.")
        return True

    configuration: Configuration
    registry: MinecraftRegistry
    version: Version

    configuration = kwargs["configuration"]
    registry = MinecraftRegistry(
        json_data=kwargs["registry"].json_data
    )
    version = kwargs["version"]

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
        description="Create a new Credentials."
    )

    parser.add_argument(
        'credentials',
        nargs=1,
        help='The credentials file to create.'
    )

    args = parser.parse_args(argv)

    credentials_file = args.credentials[0]

    if not os.path.exists(credentials_file):
        print("[!] Credentials file does not exist.")
        return True

    credentials = Credentials(
        json_data=Credentials.load(
            configuration_file=credentials_file
        ).json_data
    )

    if not credentials.validate():
        print("[!] Invalid credentials data.")
        return True
    
    # Ask to confirm
    print("[?] Are you sure you want to create the credentials? [y/N]")

    if input().lower() != "y":
        print("[!] Cancelled.")
        return True
    
    # Create credentials
    credentials_path = os.path.join(
        configuration.get_paths()["config"],
        'credentials.json'
    )

    credentials.dump(
        data=credentials.json_data,
        configuration_file=credentials_path
    )

    print("[+] Credentials created on {}".format(credentials_path))

    return True