import boto3
import os

from ...domain.storage.storage import Storage
from ...domain.configuration.configuration import Configuration
from ...domain.credentials.credentials import Credentials
from ...domain.versions.provider import Provider

class S3Storage(Storage):
    
    compressed_name = "files.zip"
    configuration_name = "settings.json"

    def __init__(self, configuration: Configuration, credentials: Credentials, provider: Provider, id: str, override_aws_bucket: str = None, override_aws_prefix: str = None):
        super().__init__(configuration, credentials)
        self.provider = provider
        self.id = id
        self.override_aws_bucket = override_aws_bucket
        self.override_aws_prefix = override_aws_prefix

    def send_files(self, compressed_path: str, configuration_path: str):
    
        if not os.path.exists(compressed_path):
            raise Exception("Compressed file does not exist")

        if not os.path.exists(configuration_path):
            raise Exception("Configuration file does not exist")

        bucket, prefix = self.credentials.get_aws_bucket(), self.credentials.get_aws_prefix()

        if self.override_aws_bucket is not None:
            bucket = self.override_aws_bucket
        
        if self.override_aws_prefix is not None:
            prefix = self.override_aws_prefix

        sess = boto3.Session(
            aws_access_key_id=self.credentials.get_aws_access_key_id(),
            aws_secret_access_key=self.credentials.get_aws_secret_access_key(),
            region_name=self.credentials.get_aws_region()
        )

        s3 = sess.resource('s3')
        aws_key = f"{prefix if prefix is not None or prefix != '' else ''}/{self.provider.name}/{self.provider.version}/{self.id}"

        # Upload compressed file
        aws_compressed_key = f"{aws_key}/{self.compressed_name}"
        s3.Bucket(bucket).upload_file(compressed_path, aws_compressed_key)

        # Upload configuration file
        aws_configuration_key = f"{aws_key}/{self.configuration_name}"
        s3.Bucket(bucket).upload_file(configuration_path, aws_configuration_key)

        return aws_compressed_key, aws_configuration_key

    def send_configuration(self, configuration_path: str):
        
        if not os.path.exists(configuration_path):
            raise Exception("Configuration file does not exist")

        bucket, prefix = self.credentials.get_aws_bucket(), self.credentials.get_aws_prefix()

        if self.override_aws_bucket is not None:
            bucket = self.override_aws_bucket
        
        if self.override_aws_prefix is not None:
            prefix = self.override_aws_prefix

        sess = boto3.Session(
            aws_access_key_id=self.credentials.get_aws_access_key_id(),
            aws_secret_access_key=self.credentials.get_aws_secret_access_key(),
            region_name=self.credentials.get_aws_region()
        )

        s3 = sess.resource('s3')
        aws_key = f"{prefix if prefix is not None or prefix != '' else ''}/{self.provider.name}/{self.provider.version}/{self.id}"

        # Upload configuration file
        aws_configuration_key = f"{aws_key}/{self.configuration_name}"
        s3.Bucket(bucket).upload_file(configuration_path, aws_configuration_key)

        return aws_configuration_key

    def get_files(self, compressed_output: str):
        
        bucket, prefix = self.credentials.get_aws_bucket(), self.credentials.get_aws_prefix()

        if self.override_aws_bucket is not None:
            bucket = self.override_aws_bucket
        
        if self.override_aws_prefix is not None:
            prefix = self.override_aws_prefix

        sess = boto3.Session(
            aws_access_key_id=self.credentials.get_aws_access_key_id(),
            aws_secret_access_key=self.credentials.get_aws_secret_access_key(),
            region_name=self.credentials.get_aws_region()
        )

        s3 = sess.resource('s3')
        aws_key = f"{prefix if prefix is not None or prefix != '' else ''}/{self.provider.name}/{self.provider.version}/{self.id}"

        # Upload compressed file
        aws_compressed_key = f"{aws_key}/{self.compressed_name}"
        s3.Bucket(bucket).download_file(aws_compressed_key, compressed_output)

        if not os.path.exists(compressed_output):
            raise Exception("Compressed file does not exist")

    def get_settings(self, settings_output: str):
        
        bucket, prefix = self.credentials.get_aws_bucket(), self.credentials.get_aws_prefix()

        if self.override_aws_bucket is not None:
            bucket = self.override_aws_bucket
        
        if self.override_aws_prefix is not None:
            prefix = self.override_aws_prefix

        sess = boto3.Session(
            aws_access_key_id=self.credentials.get_aws_access_key_id(),
            aws_secret_access_key=self.credentials.get_aws_secret_access_key(),
            region_name=self.credentials.get_aws_region()
        )

        s3 = sess.resource('s3')
        aws_key = f"{prefix if prefix is not None or prefix != '' else ''}/{self.provider.name}/{self.provider.version}/{self.id}"

        aws_configuration_key = f"{aws_key}/{self.configuration_name}"
        s3.Bucket(bucket).download_file(aws_configuration_key, settings_output)
        
        if not os.path.exists(settings_output):
            raise Exception("Configuration file does not exist")
