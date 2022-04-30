import logging
from posixpath import join
import shutil
import os

from ...domain.configuration.configuration import Configuration
from ...domain.jvm.jvm import JVMConfiguration
from ...shared.files import create_directories, remove_directory
from urllib.request import urlretrieve

class MinecraftJVM:

    def __init__(self, configuration:  Configuration, jvm: JVMConfiguration):
        self.configuration = configuration
        self.jvm = jvm

    def install(self, version: str, provider: str, dist: str, arch: str):
        # Get the version
        jvm_version = self.jvm.get_version(version)
        jvm_provider = jvm_version.get_provider(provider)
        jvm_dist = jvm_provider.get_dist(dist)
        jvm_arch = jvm_dist.get_arch(arch)

        jvm_path = os.path.join(
            self.configuration.get_path(),
            'jvm',
            jvm_provider.name,
            jvm_version.name
        )
        tmp_path = os.path.join(
            self.configuration.get_path(),
            'jvm',
            'tmp'
        )

        # Create the directory
        create_directories(jvm_path, tmp_path)

        compressed_path = os.path.join(tmp_path, os.path.basename(jvm_arch.url))

        # Download the JVM Compressed File
        urlretrieve(jvm_arch.url, compressed_path)

        if not os.path.exists(compressed_path):
            logging.error(f'Failed to download JVM on {compressed_path}')
            raise Exception('Failed to download JVM')
    
        # Extract the JVM
        logging.info(f'Extracting JVM {compressed_path} on {jvm_path}')

        if os.path.basename(jvm_arch.url).endswith('.zip'):
            shutil.unpack_archive(compressed_path, jvm_path, format='zip')
        elif os.path.basename(jvm_arch.url).endswith('.tar.gz'):
            shutil.unpack_archive(compressed_path, jvm_path, format='tar')
        else:
            logging.error(f'Unknown JVM archive format {os.path.basename(jvm_arch.url)}')
            raise Exception('Unknown JVM archive format')
        
        # Remove tmp directory
        remove_directory(tmp_path)

        # Register JVM
        self.configuration.register_jvm(
            version=jvm_version.name,
            provider=jvm_provider.name,
            dist=jvm_dist.name,
            arch=jvm_arch.name,
            home_path=os.path.join(
                jvm_path,
                os.listdir(jvm_path)[0]
            ),
            jvm_path=os.path.join(
                jvm_path,
                os.listdir(jvm_path)[0],
                'bin',
                'java'
            ),
            installed=True
        )

        try:
            os.chmod(os.path.join(
                jvm_path,
                os.listdir(jvm_path)[0],
                'bin',
                'java'), 
                0o755
            )
        except Exception as e:
            logging.info("Encountered incompatible OS for chmod")

        Configuration.dump(self.configuration.json_data, self.configuration.get_config_file())