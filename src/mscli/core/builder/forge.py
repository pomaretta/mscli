from datetime import datetime
import json
import os
import hashlib

from mscli.shared.files import create_directories

from ...domain.builders.builder import MinecraftBuilder
from ...domain.pipeline.pipeline import Pipeline
from ..configuration.server import ForgeServer
from ...domain.configuration.registry import RegistryObject

from ..pipeline.additions import AddMods, AddProperties, AddIcon, AddWorld
from ..pipeline.download import DownloadBinaryFile
from ..pipeline.run import RunMinecraftBinary, CheckUpdateAndRunning
from ..pipeline.install import ExtractForgeFile, WriteEULA
from ..pipeline.compress import CompressDirectory, UncompressDirectory
from ..pipeline.config import CreateConfig, UpdateConfigOnRun
from ..pipeline.upload import UploadConfig, UploadFiles
from ..pipeline.update import CheckSettings, GetServerFiles, GetServerSettings, ReplaceFile
from ..pipeline.registry import AddExistingObjectToRegistry, AddToRegistry, RunUpdateRegistry, UpdateRegistryObject
from ...domain.storage.storage import Storage
from ..pipeline.config import UpdateConfig
from ..storage.s3 import S3Storage
from ..storage.ftp import FTPStorage
from ..storage.sftp import SFTPStorage

class ForgeBuilder(MinecraftBuilder):

    def __init__(self, configuration, credentials, registry, provider, server: ForgeServer = None) -> None:
        super().__init__(configuration, credentials, registry, provider)
        self.server = server

    def run(self, id: str):
        
        pipeline = Pipeline(
            pipeline_id='forge-run-pipeline',
            name='Forge Run Pipeline'
        )

        # Set the id
        self.provider.get_files().set_id(id)

        files_path = os.path.join(
            self.configuration.get_paths()['files'],
            self.provider.get_files().get_src()
        )
        settings_path = os.path.join(
            self.configuration.get_paths()['files'],
            self.provider.get_files().get_config()
        )

        settings = None
        with open(settings_path, 'r') as file:
            settings = json.loads(file.read())
            file.close()
        
        registry_object = self.registry.get(id)
        
        # Check if the server is updated and is not running
        pipeline.add_stage(
            CheckUpdateAndRunning(
                self,
                stage_id='check-update-and-running',
                name='Check Update and Running',
                description='Check if server is running and update if needed',
                id=id
            )
        )

        pipeline.add_stage(
            RunMinecraftBinary(
                self,
                stage_id='forge-run',
                name='Forge Run',
                description='Run the Forge binary',
                files_path=files_path,
                binary_name=self.provider.data["forge_binary"],
                xmx=settings["jvm"]["xmx"],
                xms=settings["jvm"]["xms"],
                output=pipeline._output
            )   
        )

        # Update registry
        pipeline.add_stage(
            RunUpdateRegistry(
                self,
                stage_id='forge-registry-update',
                name='Forge Registry Update',
                description='Update the Forge registry',
                registry_object=registry_object,
                running=True
            )
        )

        # TODO: Create storage using credentials type
        storage: Storage = None
        if self.credentials.__type__() == "aws":
            storage = S3Storage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=registry_object.id
            )
        elif self.credentials.__type__() == "ftp":
            storage = FTPStorage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=registry_object.id
            )
        elif self.credentials.__type__() == "sftp":
            storage = SFTPStorage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=registry_object.id
            )

        configuration_path = []

        # Update config for other users
        pipeline.add_stage(
            UpdateConfigOnRun(
                self,
                stage_id='vanilla-config-update',
                name='Vanilla Config Update',
                description='Update the Vanilla config file',
                id=id,
                xmx=2048,
                xms=1024,
                ip=self.configuration.get_ip(),
                output=configuration_path
            )
        )

        # Upload new config
        pipeline.add_stage(
            UploadConfig(
                self,
                stage_id='vanilla-config-upload',
                name='Vanilla Config Upload',
                description='Upload the Vanilla config file',
                storage=storage,
                configuration_path=configuration_path
            )    
        )

        pipeline.run()

        return pipeline

    def postrun(self, id: str):

        pipeline = Pipeline(
            pipeline_id='forge-postrun-pipeline',
            name='Forge Postrun Pipeline'
        )

        # Set the id
        self.provider.get_files().set_id(id)
        src = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_src())
        tmp = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_tmp())

        storage: Storage = None
        if self.credentials.__type__() == "aws":
            storage = S3Storage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=id
            )
        elif self.credentials.__type__() == "ftp":
            storage = FTPStorage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=id
            )
        elif self.credentials.__type__() == "sftp":
            storage = SFTPStorage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=id
            )

        registry_object = self.registry.get(id)

        input_path = [src]
        compressed_path = []

        # TODO: Compress files
        pipeline.add_stage(
            CompressDirectory(
                self,
                stage_id='forge-compressor',
                name='Forge Compressor',
                description='Compress the Forge files',
                directory_path=input_path,
                output_path=tmp,
                output=compressed_path
            )
        )

        configuration_data = []

        # TODO: Update settings
        pipeline.add_stage(
            UpdateConfig(
                self,
                stage_id='forge-config',
                name='Forge Config',
                description='Update the Forge config file',
                id=id,
                xmx=2048,
                xms=1024,
                ip=self.configuration.get_ip(),
                checksum=compressed_path,
                output=configuration_data
            )
        )

        # TODO: Upload files
        pipeline.add_stage(
            UploadFiles(
                self,
                stage_id='forge-uploader',
                name='Forge Uploader',
                description='Upload the Forge files',
                storage=storage,
                compressed_path=compressed_path,
                configuration_path=configuration_data
            )
        )

        # TODO: Update registry
        pipeline.add_stage(
            RunUpdateRegistry(
                self,
                stage_id='forge-registry',
                name='Forge Registry',
                description='Register the Forge server',
                registry_object=registry_object,
                running=False
            )
        )

        pipeline.run()

    def import_server(self, registry_object: RegistryObject):
        
        pipeline = Pipeline(
            pipeline_id='forge-import-pipeline',
            name='Forge Import Pipeline'
        )

        # Set the id
        self.provider.get_files().set_id(registry_object.id)

        src = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_src())
        cfg = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_config())
        tmp = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_tmp())

        create_directories(src, tmp)

        storage: Storage = None
        if self.credentials.__type__() == "aws":
            storage = S3Storage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=registry_object.id
            )
        elif self.credentials.__type__() == "ftp":
            storage = FTPStorage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=registry_object.id
            )
        elif self.credentials.__type__() == "sftp":
            storage = SFTPStorage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=registry_object.id
            )

        config_path = []

        pipeline.add_stage(
            GetServerSettings(
                self,
                stage_id='forge-settings',
                name='Forge Settings',
                description='Get the Forge settings',
                storage=storage,
                output=config_path
            )
        )

        check_data = []

        pipeline.add_stage(
            CheckSettings(
                self,
                stage_id='forge-check-settings',
                name='Forge Check Settings',
                description='Check the Forge settings',
                cloud_settings=config_path,
                check_cloud=False,
                output=check_data
            )
        )

        files_path = []

        pipeline.add_stage(
            GetServerFiles(
                self,
                stage_id='forge-get-files',
                name='Forge Get Files',
                description='Get the Forge files',
                storage=storage,
                check_data=check_data,
                output=files_path
            )
        )

        # Uncompress files (reset files directory)
        pipeline.add_stage(
            UncompressDirectory(
                self,
                stage_id='forge-uncompressor',
                name='Forge Uncompressor',
                description='Uncompress the Forge files',
                compressed_path=files_path,
                output_path=src
            )
        )

        # Update config
        pipeline.add_stage(
            ReplaceFile(
                self,
                stage_id='forge-config',
                name='Forge Config',
                description='Update the Forge config file',
                old_file=cfg,
                new_file=config_path
            )
        )

        # Update registry
        # Register server to the server registry
        pipeline.add_stage(
            AddExistingObjectToRegistry(
                self,
                stage_id='forge-registry',
                name='Forge Registry',
                description='Register the Forge server',
                existing_object=registry_object,
                local_path=src
            )
        )

        pipeline.run()

    def update(self, registry_object: RegistryObject):
        
        pipeline = Pipeline(
            pipeline_id='forge-update-pipeline',
            name='Forge Update Pipeline',
        )

        # Set the id
        self.provider.get_files().set_id(registry_object.id)

        src = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_src())
        cfg = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_config())
        tmp = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_tmp())

        create_directories(src, tmp)

        storage: Storage = None
        if self.credentials.__type__() == "aws":
            storage = S3Storage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=registry_object.id
            )
        elif self.credentials.__type__() == "ftp":
            storage = FTPStorage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=registry_object.id
            )
        elif self.credentials.__type__() == "sftp":
            storage = SFTPStorage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=registry_object.id
            )

        config_path = []

        pipeline.add_stage(
            GetServerSettings(
                self,
                stage_id='forge-settings',
                name='Forge Settings',
                description='Get the Forge settings',
                storage=storage,
                output=config_path
            )
        )

        check_data = []

        pipeline.add_stage(
            CheckSettings(
                self,
                stage_id='forge-check-settings',
                name='Forge Check Settings',
                description='Check the Forge settings',
                cloud_settings=config_path,
                output=check_data
            )
        )

        files_path = []

        # Download server files
        pipeline.add_stage(
            GetServerFiles(
                self,
                stage_id='forge-files',
                name='Forge Files',
                description='Get the Forge files',
                storage=storage,
                check_data=check_data,
                output=files_path
            )
        )

        # Uncompress files (reset files directory)
        pipeline.add_stage(
            UncompressDirectory(
                self,
                stage_id='forge-uncompressor',
                name='Forge Uncompressor',
                description='Uncompress the Forge files',
                compressed_path=files_path,
                output_path=src
            )
        )

        # Update config
        pipeline.add_stage(
            ReplaceFile(
                self,
                stage_id='forge-config',
                name='Forge Config',
                description='Update the Forge config file',
                old_file=cfg,
                new_file=config_path
            )
        )

        # Update registry
        pipeline.add_stage(
            UpdateRegistryObject(
                self,
                stage_id='forge-registry',
                name='Forge Registry',
                description='Register the Forge server',
                existing_object=registry_object,
                config_path=cfg
            )
        )

        pipeline.run()

        return pipeline._failed

    def create(self):
        
        pipeline = Pipeline(
            pipeline_id='forge-create-pipeline',
            name='Forge Create Pipeline'
        )

        id = hashlib.md5(f"{self.provider.name}{self.provider.version}{datetime.now().isoformat()}".encode()).hexdigest()
        self.provider.get_files().set_id(id)

        tmp = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_tmp())
        src = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_src())

        # Initialize tmp directory
        self.__create_directories__(
            tmp, src
        )

        download_path = []

        # Get the forge binary on the TMP directory
        pipeline.add_stage(
            DownloadBinaryFile(
                self,
                stage_id='forge-downloader',
                name='Forge Downloader',
                description='Downloads the Forge binary file',
                override_tmp=tmp,
                override_filename=self.provider.data["installer"],
                output=download_path
            )
        )

        installed_path = []

        # Extract forge files into the files directory
        pipeline.add_stage(
            ExtractForgeFile(
                self,
                stage_id='forge-installer',
                name='Forge Installer',
                description='Install the Forge binary file',
                file_path=download_path,
                output_path=src,
                output=installed_path
            )
        )

        # Run one time for generate the EULA
        pipeline.add_stage(
            WriteEULA(
                self,
                stage_id='forge-eula',
                name='Forge EULA',
                description='Create the EULA path',
                input_path=installed_path
            )
        )

        # TODO: Add mods
        pipeline.add_stage(
            AddMods(
                self,
                stage_id='forge-mods',
                name='Forge Mods',
                description='Add the Forge mods'
            )
        )

        # TODO: Add properties
        pipeline.add_stage(
            AddProperties(
                self,
                stage_id='forge-properties',
                name='Forge Properties',
                description='Add the Forge properties'
            )
        )

        # TODO: Add world
        pipeline.add_stage(
            AddWorld(
                self,
                stage_id='forge-world',
                name='Forge World',
                description='Add the Forge world'
            )
        )

        # TODO: Add icon
        pipeline.add_stage(
            AddIcon(
                self,
                stage_id='forge-icon',
                name='Forge Icon',
                description='Add the Forge icon'
            )
        )

        compressed_data = []

        # TODO: Create ZIP
        pipeline.add_stage(
            CompressDirectory(
                self,
                stage_id='forge-compressor',
                name='Forge Compressor',
                description='Compress the Forge files',
                directory_path=installed_path,
                output_path=tmp,
                output=compressed_data
            )
        )

        configuration_data = []

        # TODO: Create config
        pipeline.add_stage(
            CreateConfig(
                self,
                stage_id='forge-config',
                name='Forge Config',
                description='Create the config file',
                id=id,
                xmx=2048,
                xms=1024,
                ip=self.configuration.get_ip(),
                checksum=compressed_data,
                output=configuration_data
            )
        )

        # Storage
        storage: Storage = None
        if self.credentials.__type__() == "aws":
            storage = S3Storage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=id
            )
        elif self.credentials.__type__() == "ftp":
            storage = FTPStorage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=id
            )
        elif self.credentials.__type__() == "sftp":
            storage = SFTPStorage(
                configuration=self.configuration,
                credentials=self.credentials,
                provider=self.provider,
                id=id
            )

        # TODO: Upload config and zip
        pipeline.add_stage(
            UploadFiles(
                self,
                stage_id='forge-uploader',
                name='Forge Uploader',
                description='Upload the Forge files',
                storage=storage,
                compressed_path=compressed_data,
                configuration_path=configuration_data
            )
        )

        # Register server to the server registry
        pipeline.add_stage(
            AddToRegistry(
                self,
                stage_id='forge-registry',
                name='Forge Registry',
                description='Register the Forge server',
                id=id,
                local_path=installed_path,
                config_data=configuration_data
            )
        )

        pipeline.run()

        return id
