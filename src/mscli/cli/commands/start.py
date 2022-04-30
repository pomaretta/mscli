__command__ = "start"

import os
import time

from typing import Optional, List
from mscli.core.jvm.jvm import MinecraftJVM

from mscli.domain.credentials.credentials import Credentials
from mscli.domain.configuration.configuration import Configuration
from mscli.domain.jvm.jvm import JVMConfiguration
from mscli.domain.versions.version import Versions
from mscli.core.builder.forge import ForgeBuilder
from mscli.core.builder.vanilla import VanillaBuilder
from mscli.core.configuration.registry import MinecraftRegistry

from subprocess import Popen
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

    command = pipeline._output[0]
    path = pipeline._output[1]
    old_cwd = os.getcwd()

    os.chdir(path)

    try:
        os.system(command)
    except KeyboardInterrupt:
        pass

    os.chdir(old_cwd)

    # process: Popen
    # process = pipeline._output[0]

    # exit_code = None
    # exit = False
    # while not exit:
    #     readable = True
    #     while process.stdout.readable():
    #         line = process.stdout.readline()
    #         print(line.decode('utf-8'))
    #         print(f"[*] Server running. {process.stdout.readable()}")

    #     print(f"MS {configuration.get_ip()}@{id} $ ", end='')
    #     command = input()
    #     if command == "exit" or command == "stop":
    #         process.stdin.write(command.encode('utf-8'))
    #         process.stdin.flush()
    #         process.kill()
    #         exit = True
    #     process.stdin.write(command.encode())
    #     process.stdin.flush()

    # TODO: Update cloud files.
    builder.postrun(id=id)

    return True