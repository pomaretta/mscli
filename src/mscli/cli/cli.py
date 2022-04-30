import sys
import os

from mscli.domain.credentials.credentials import Credentials

from .util.run import run_subcommand
from argparse import ArgumentParser
from . import META_COMMANDS

from mscli.core.jvm.jvm import MinecraftJVM
from mscli.domain.configuration.configuration import Configuration
from mscli.domain.configuration.registry import Registry
from mscli.domain.jvm.jvm import JVMConfiguration
from mscli.domain.versions.version import Version, Versions

def main():

    parser = ArgumentParser()

    parser.add_argument(
        'command'
        ,nargs=1
        ,type=str
        ,help="The command to be executed."
    )

    parser.add_argument(
        'args'
        ,nargs="*"
        ,type=str
        ,help="The command arguments to be used by the subcommand."
    )

    # parser.add_argument(
    #     '--credentials',
    #     type=str,
    #     help="The path to the credentials file.",
    #     required=False
    # )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Create config
    config = None
    config_path = os.path.expanduser("~/.mscli/config/config.json")
    if not os.path.exists(
        config_path
    ):
        print("[!] No config file found. Creating one...")
        config = Configuration.create()
        Configuration.dump(config.json_data, config_path)
        print(f"[+] Config file created on {config_path}")
    else:
        config = Configuration(
            json_data=Configuration.load(config_path).json_data
        )

    # Create JVM
    jvm = None
    jvm_path = os.path.expanduser("~/.mscli/config/jvm.json")
    if not os.path.exists(
        jvm_path
    ):
        print("[!] No JVM file found. Creating one...")
        jvm = JVMConfiguration.create()
        JVMConfiguration.dump(jvm.json_data, jvm_path)
        print(f"[+] JVM file created on {jvm_path}")
    else:
        jvm = JVMConfiguration(
            json_data=JVMConfiguration.load(jvm_path).json_data
        )

    # Create Registry
    registry = None
    registry_path = os.path.expanduser("~/.mscli/config/registry.json")
    if not os.path.exists(
        registry_path
    ):
        print("[!] No registry file found. Creating one...")
        registry = Registry.create()
        Registry.dump(registry.json_data, registry_path)
        print(f"[+] Registry file created on {registry_path}")
    else:
        registry = Registry(
            json_data=Registry.load(registry_path).json_data
        )
    
    # Create Version
    versions = None
    versions_path = os.path.expanduser("~/.mscli/config/versions.json")
    if not os.path.exists(
        versions_path
    ):
        print("[!] No versions file found. Creating one...")
        versions = Versions.create()
        Version.dump(versions.json_data, versions_path)
        print(f"[+] Version file created on {versions_path}")
    else:
        versions = Versions(
            json_data=Versions.load(versions_path).json_data
        )

    # Get JRE
    jre = None
    if not "jre" in config.json_data:
        print("[!] No JRE found. Installing one...")
        jre = MinecraftJVM(
            configuration=config,
            jvm=jvm
        )
        jre.install(
            version='1.8',
            provider='liberica',
            dist=config.get_os(),
            arch=config.get_arch()
        )
        print(f"[+] Installed Java {'1.8'} from {'Liberica'} for {config.get_os()}_{config.get_arch()}")
    
    # Get credentials
    credentials = None
    credentials_path = os.path.expanduser("~/.mscli/config/credentials.json")
    if os.path.exists(credentials_path):
        credentials = Credentials(
            json_data=Credentials.load(credentials_path).json_data
        )
    else:
        print("[!] Running without credentials")

    argv = sys.argv[1:]
    args = parser.parse_args(argv)

    if not run_subcommand(
        subcommand=args.command[0].lower()
        ,subcommand_args=args.args
        ,pwd=os.getcwd()
        # KWARGS
        ,credentials=credentials
        ,configuration=config
        ,jvm=jvm
        ,registry=registry
        ,version=versions
    ):
        parser.print_help()