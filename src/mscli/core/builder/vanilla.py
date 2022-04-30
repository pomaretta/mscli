from datetime import datetime
import json
import os
import hashlib


from mscli.shared.files import create_directories

from ...domain.builders.builder import MinecraftBuilder
from ...domain.pipeline.pipeline import Pipeline
from ..configuration.server import VanillaServer
from ...domain.configuration.registry import RegistryObject

from ..pipeline.additions import AddMods, AddProperties, AddIcon, AddWorld
from ..pipeline.download import DownloadBinaryFile
from ..pipeline.run import RunMinecraftBinary, CheckUpdateAndRunning
from ..pipeline.install import ExtractForgeFile, WriteEULA
from ..pipeline.compress import CompressDirectory, UncompressDirectory
from ..pipeline.config import CreateConfig, UpdateConfigOnRun
from ..pipeline.upload import UploadConfig, UploadFiles
from ..pipeline.update import CheckSettings, GetServerFiles, GetServerSettings, ReplaceFile, MoveFile
from ..pipeline.registry import AddExistingObjectToRegistry, AddToRegistry, RunUpdateRegistry, UpdateRegistryObject
from ...domain.storage.storage import Storage
from ..pipeline.config import UpdateConfig
from ..storage.s3 import S3Storage
from ..storage.ftp import FTPStorage
from ..storage.sftp import SFTPStorage

class VanillaBuilder(MinecraftBuilder):

    def __init__(self, configuration, credentials, registry, provider, server: VanillaServer = None) -> None:
        super().__init__(configuration, credentials, registry, provider)
        self.server = server

    def run(self, id: str):

        pipeline = Pipeline(
            pipeline_id='vanilla-run-pipeline',
            name='Vanilla Run Pipeline'
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
        
        # Get the command to run
        pipeline.add_stage(
            RunMinecraftBinary(
                self,
                stage_id='vanilla-run',
                name='Vanilla Run',
                description='Run the Vanilla binary',
                files_path=files_path,
                binary_name=self.provider.filename,
                xmx=settings["jvm"]["xmx"],
                xms=settings["jvm"]["xms"],
                output=pipeline._output
            )   
        )

        # Update registry
        pipeline.add_stage(
            RunUpdateRegistry(
                self,
                stage_id='vanilla-registry-update',
                name='Vanilla Registry Update',
                description='Update the Vanilla registry',
                registry_object=registry_object,
                running=True
            )
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
            pipeline_id='vanilla-postrun-pipeline',
            name='Vanilla Postrun Pipeline'
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
                stage_id='vanilla-compressor',
                name='Vanilla Compressor',
                description='Compress the Vanilla files',
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
                stage_id='vanilla-config',
                name='Vanilla Config',
                description='Update the Vanilla config file',
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
                stage_id='vanilla-uploader',
                name='Vanilla Uploader',
                description='Upload the Vanilla files',
                storage=storage,
                compressed_path=compressed_path,
                configuration_path=configuration_data
            )
        )

        # TODO: Update registry
        pipeline.add_stage(
            RunUpdateRegistry(
                self,
                stage_id='vanilla-registry',
                name='Vanila Registry',
                description='Register the Vanilla server',
                registry_object=registry_object,
                running=False
            )
        )

        pipeline.run()

    def import_server(self, registry_object: RegistryObject):
        
        pipeline = Pipeline(
            pipeline_id='vanilla-import-pipeline',
            name='Vanilla Import Pipeline'
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
                stage_id='vanilla-settings',
                name='Vanilla Settings',
                description='Get the Vanilla settings',
                storage=storage,
                output=config_path
            )
        )

        check_data = []

        pipeline.add_stage(
            CheckSettings(
                self,
                stage_id='vanilla-check-settings',
                name='Vanilla Check Settings',
                description='Check the Vanilla settings',
                cloud_settings=config_path,
                check_cloud=False,
                output=check_data
            )
        )

        files_path = []

        pipeline.add_stage(
            GetServerFiles(
                self,
                stage_id='vanilla-get-files',
                name='Vanilla Get Files',
                description='Get the Vanilla files',
                storage=storage,
                check_data=check_data,
                output=files_path
            )
        )

        # Uncompress files (reset files directory)
        pipeline.add_stage(
            UncompressDirectory(
                self,
                stage_id='vanilla-uncompressor',
                name='Vanilla Uncompressor',
                description='Uncompress the Vanilla files',
                compressed_path=files_path,
                output_path=src
            )
        )

        # Update config
        pipeline.add_stage(
            ReplaceFile(
                self,
                stage_id='vanilla-config',
                name='Vanilla Config',
                description='Update the Vanilla config file',
                old_file=cfg,
                new_file=config_path
            )
        )

        # Update registry
        # Register server to the server registry
        pipeline.add_stage(
            AddExistingObjectToRegistry(
                self,
                stage_id='vanilla-registry',
                name='Vanilla Registry',
                description='Register the Vanilla server',
                existing_object=registry_object,
                local_path=src
            )
        )

        pipeline.run()

    def update(self, registry_object: RegistryObject):
        
        pipeline = Pipeline(
            pipeline_id='vanilla-update',
            name='Vanilla Update'
        )

        # Set the ID
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
                stage_id='vanilla-settings',
                name='Vanilla Settings',
                description='Get the Vanilla settings',
                storage=storage,
                output=config_path
            )
        )

        check_data = []

        pipeline.add_stage(
            CheckSettings(
                self,
                stage_id='vanilla-check-settings',
                name='Vanilla Check Settings',
                description='Check the Vanilla settings',
                cloud_settings=config_path,
                output=check_data
            )
        )

        files_path = []

        # Download server files
        pipeline.add_stage(
            GetServerFiles(
                self,
                stage_id='Vanilla-files',
                name='Vanilla Files',
                description='Get the Vanilla files',
                storage=storage,
                check_data=check_data,
                output=files_path
            )
        )

        # Uncompress files (reset files directory)
        pipeline.add_stage(
            UncompressDirectory(
                self,
                stage_id='vanilla-uncompressor',
                name='Vanilla Uncompressor',
                description='Uncompress the Vanilla files',
                compressed_path=files_path,
                output_path=src
            )
        )

        # Update config
        pipeline.add_stage(
            ReplaceFile(
                self,
                stage_id='vanilla-config',
                name='Vanilla Config',
                description='Update the Vanilla config file',
                old_file=cfg,
                new_file=config_path
            )
        )

        # Update registry
        pipeline.add_stage(
            UpdateRegistryObject(
                self,
                stage_id='vanilla-registry',
                name='Vanilla Registry',
                description='Register the Vanilla server',
                existing_object=registry_object,
                config_path=cfg
            )
        )

        pipeline.run()

        return pipeline._failed

    def create(self):
        
        pipeline = Pipeline(
            pipeline_id='vanilla-create-pipeline',
            name='Vanilla Create Pipeline'
        )

        id = hashlib.md5(f"{self.provider.name}{self.provider.version}{datetime.now().isoformat()}".encode()).hexdigest()
        self.provider.get_files().set_id(id)

        tmp = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_tmp())
        src = os.path.join(self.configuration.get_paths()['files'], self.provider.files.get_src())

        create_directories(src, tmp)

        download_path = []

        pipeline.add_stage(
            DownloadBinaryFile(
                self,
                stage_id='vanilla-download',
                name='Vanilla Download',
                description='Download the Vanilla server',
                override_tmp=tmp,
                override_filename=self.provider.files.filename,
                output=download_path
            )
        )

        installed_path = []

        # Move .jar file to src
        pipeline.add_stage(
            MoveFile(
                self,
                stage_id='vanilla-move-jar',
                name='Vanilla Move Jar',
                description='Move the Vanilla server jar to the src directory',
                new_path=src,
                file=download_path,
                output=installed_path
            )
        )

        # Write EULA
        pipeline.add_stage(
            WriteEULA(
                self,
                stage_id='vanilla-write-eula',
                name='Vanilla Write EULA',
                description='Write the EULA file',
                input_path=installed_path
            )
        )

        # Add properties
        pipeline.add_stage(
            AddProperties(
                self,
                stage_id='vanilla-add-properties',
                name='Vanilla Add Properties',
                description='Add the properties file'
            )
        )

        # Add world
        pipeline.add_stage(
            AddWorld(
                self,
                stage_id='vanilla-add-world',
                name='Vanilla Add World',
                description='Add the world directory'
            )
        )

        # Add icon
        pipeline.add_stage(
            AddIcon(
                self,
                stage_id='vanilla-add-icon',
                name='Vanilla Add Icon',
                description='Add the icon file'
            )
        )

        compressed_data = []
        directory_path = [src]

        # Create ZIP
        pipeline.add_stage(
            CompressDirectory(
                self,
                stage_id='vanilla-compress',
                name='Vanilla Compress',
                description='Compress the server directory',
                directory_path=directory_path,
                output_path=tmp,
                output=compressed_data
            )
        )

        configuration_data = []

        # Create configuration
        pipeline.add_stage(
            CreateConfig(
                self,
                stage_id='vanilla-create-config',
                name='Vanilla Create Config',
                description='Create the configuration file',
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

        # Upload files
        pipeline.add_stage(
            UploadFiles(
                self,
                stage_id='vanilla-upload',
                name='Vanilla Upload',
                description='Upload the files to the storage',
                storage=storage,
                compressed_path=compressed_data,
                configuration_path=configuration_data,
            )
        )

        # Add to registry
        pipeline.add_stage(
            AddToRegistry(
                self,
                stage_id='vanilla-add-registry',
                name='Vanilla Add Registry',
                description='Add the server to the registry',
                id=id,
                local_path=installed_path,
                config_data=configuration_data
            )
        )

        pipeline.run()

        return id
