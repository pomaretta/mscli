__command__ = "start"

import os
import sys
import threading
import time

from typing import Optional, List
from queue import SimpleQueue
from mscli.core.jvm.jvm import MinecraftJVM

from mscli.domain.credentials.credentials import Credentials
from mscli.domain.configuration.configuration import Configuration
from mscli.domain.jvm.jvm import JVMConfiguration
from mscli.domain.versions.version import Versions
from mscli.core.builder.forge import ForgeBuilder
from mscli.core.builder.vanilla import VanillaBuilder
from mscli.core.configuration.registry import MinecraftRegistry
from mscli.core.jvm.server import MinecraftServer

from ..cmd import MSCLIPrompt

from argparse import ArgumentParser

def main(
    argv: Optional[List[str]] = None
    ,pwd: str = None
    ,**kwargs
) -> bool:

    parser = ArgumentParser(
        description="Runs the Minecraft server."
    )

    parser.add_argument(
        'id',
        type=str,
        nargs=1,
        help="The id of the server to run."
    )

    args = parser.parse_args(argv)

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

    id = args.id[0]

    registry_object = registry.get(id)
    if registry_object is None:
        print("[!] Server {} not found.".format(id))
        return True

    # TODO: Run server.
    builder = None

    provider = version.get_version(registry_object.version).get_provider(registry_object.provider)
    if registry_object.provider == "forge":
        builder = ForgeBuilder(
            configuration=configuration,
            credentials=credentials,
            registry=registry,
            provider=provider
        )
    elif registry_object.provider == "vanilla":
        builder = VanillaBuilder(
            configuration=configuration,
            credentials=credentials,
            registry=registry,
            provider=provider
        )
    else:
        print("[!] Invalid provider.")
        return True

    version_exists = False
    for v in jvm.get_versions():
        if v.name == provider.jvm:
            version_exists = True
            break
    if not version_exists:
        print("[!] Could not find the version on JVMs.")
        return True

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
            version=provider.jvm,
            provider='liberica',
            dist=configuration.get_os(),
            arch=configuration.get_arch()
        )

        print(f"[+] Installed JVM for {registry_object.version}.")

    if registry_object.update:
        print(f"[+] Updating server {registry_object.id}.")
        failed = builder.update(
            registry_object=registry_object
        )
        if failed:
            print(f"[!] Failed to update server {registry_object.id}.")
            return True

    pipeline = builder.run(id=id)

    if pipeline._failed:
        print("[!] Failed to run server.")
        return True

    server: MinecraftServer
    server = pipeline._output[0]

    thread = threading.Thread(
        target=print_output,
        args=[server]
    )
    thread.start()
    
    while server.is_running():
        try:
            # Non-blocking input using input
            command = input()
        except KeyboardInterrupt:
            server.kill()
            break
        if command is None:
            continue
        if server.is_running():
            server.send(command)
        time.sleep(0.1)

    server.process.kill()
    server.process.terminate()
    print(f"[!] Server {id} killed with exit code {server.process.returncode}.")

    # TODO: Update cloud files.
    builder.postrun(id=id)

    return True

def print_output(server: MinecraftServer):
    while server.is_running():
        line = server.process.stdout.readline()
        if line is None:
            continue
        print(line.decode('utf-8'), end='')