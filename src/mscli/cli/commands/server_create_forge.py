__command__ = "server_create_forge"

from typing import Optional, List
from mscli import __version__
from argparse import ArgumentParser
from mscli.core.jvm.jvm import MinecraftJVM

from mscli.domain.credentials.credentials import Credentials
from mscli.domain.configuration.configuration import Configuration
from mscli.domain.jvm.jvm import JVMConfiguration
from mscli.domain.versions.version import Version, Versions
from mscli.core.builder.forge import ForgeBuilder
from mscli.core.configuration.registry import MinecraftRegistry
from mscli.core.configuration.server import ForgeServer
from mscli.core.configuration.properties import Properties1122
from mscli.core.configuration.mods import MinecraftMods

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
    if kwargs["jvm"] is None:
        print("[!] No jvm provided.")
        return True

    credentials: Credentials
    configuration: Configuration
    registry: MinecraftRegistry
    version: Versions
    jvm: JVMConfiguration

    credentials = kwargs["credentials"]
    configuration = kwargs["configuration"]
    registry = MinecraftRegistry(
        json_data=kwargs["registry"].json_data
    )
    version = kwargs["version"]
    jvm = kwargs["jvm"]

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
    if not jvm.validate():
        print("[!] Invalid jvm data.")
        return True
    
    parser = ArgumentParser(
        description="Create a Minecraft server."
    )

    # TODO: The server version
    parser.add_argument(
        'version',
        nargs=1,
        help='The version of the server to create.'
    )

    # TODO: Add support for custom server properties.
    parser.add_argument(
        'properties',
        nargs="?",
        default=None,
        help="The properties to use for the server."
    )

    # TODO: Add support for Mods
    parser.add_argument(
        'mods',
        nargs="?",
        default=None,
        help="The mods to use for the server."
    )

    # TODO: Add support for custom server icon.
    parser.add_argument(
        'icon',
        nargs="?",
        default=None,
        help="The icon to use for the server."
    )

    # TODO: Add support for custom world.
    parser.add_argument(
        'world',
        nargs="?",
        default=None,
        help="The world to use for the server."
    )
    
    args = parser.parse_args(argv)
    version_name = args.version[0]
    
    if args.properties.lower() == "none":
        args.properties = None
    if args.mods.lower() == "none":
        args.mods = None
    if args.icon.lower() == "none":
        args.icon = None
    if args.world.lower() == "none":
        args.world = None

    provider = None
    for v in version.get_versions():
        if v.name == version_name:
            provider = v.get_provider('forge')
            break

    if provider is None:
        print("[!] Could not find the version.")
        return True

    version_exists = False
    for v in jvm.get_versions():
        if v.name == provider.jvm:
            version_exists = True
            break
    if not version_exists:
        print("[!] Could not find the version on JVMs.")
        return True

    # Parse properties
    properties = None
    if version_name == "1.12.2":
        properties = Properties1122(
            json_data=Properties1122.load(args.properties).json_data if args.properties is not None else None
        )
    else:
        print("[!] No properties support for this version.")
        return True

    mods = None
    if args.mods is not None:
        mods = MinecraftMods(
            json_data=MinecraftMods.load(args.mods).json_data
        )

    server = ForgeServer(
        properties=properties,
        icon=args.icon,
        world=args.world,
        mods=mods
    )


    builder = ForgeBuilder(
        configuration=configuration,
        credentials=credentials,
        registry=registry,
        provider=provider,
        server=server
    )

    print("[+] Creating server...")

    

    # Check if the version exists on the configuration
    jvm_provider: dict = configuration.get_jvms()['liberica']
    jvm_provider_path: str = None
    for n, d in jvm_provider.items():
        if n == provider.jvm:
            jvm_provider_path = d['jvm_path']
            break

    if jvm_provider_path is None:
        print("[!] Could not find the JVM provider on the installed JVMs.")

        # Install the JVM
        jre = MinecraftJVM(
            configuration=configuration,
            jvm=jvm
        )
        
        jre.install(
            version=version_name,
            provider='liberica',
            dist=configuration.get_os(),
            arch=configuration.get_arch()
        )

        print(f"[+] Installed JVM for {version_name}.")

    id = builder.create()

    print("[+] Server created.")
    print("[+] Server ID: {}".format(id))

    return True