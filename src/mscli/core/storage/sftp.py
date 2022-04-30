from datetime import datetime
import os

from ...domain.storage.storage import Storage
from ...domain.configuration.configuration import Configuration
from ...domain.credentials.credentials import Credentials
from ...domain.versions.provider import Provider

from pysftp import Connection, CnOpts

class SFTPStorage(Storage):

    cnopts = CnOpts()

    compressed_name = "files.zip"
    configuration_name = "settings.json"
    cwd = "mscli"

    def __init__(self, configuration: Configuration, credentials: Credentials, provider: Provider, id: str):
        super().__init__(configuration, credentials)
        self.provider = provider
        self.id = id
        self.cnopts.hostkeys = None  

    def __mkdir__(self, session: Connection, required_dir: str):
        required_dir = required_dir.split('/')[:-1]
        current_cwd = session.pwd
        for path_item in required_dir:
            if path_item.strip() == '':
                continue
            path_item = path_item.replace('/', '')
            try:
                session.cwd(path_item)
            except:
                session.mkdir(path_item)
                session.cwd(path_item)
        session.cwd(current_cwd)

    def send_files(self, compressed_path: str, configuration_path: str):
        
        if self.credentials.__type__() != "sftp":
            raise Exception("Credentials are not of type FTP")

        if not os.path.exists(compressed_path):
            raise Exception("Compressed file does not exist")

        if not os.path.exists(configuration_path):
            raise Exception("Configuration file does not exist")

        session = Connection(
            host=self.credentials.get_sftp_hostname(),
            username=self.credentials.get_sftp_username(),
            private_key=self.credentials.get_sftp_private_key(),
            private_key_pass=self.credentials.get_sftp_private_key_pass(),
            password=self.credentials.get_sftp_password(),
            port=self.credentials.get_sftp_port(),
            cnopts=self.cnopts
        )

        # Check if the mscli folder exists
        full_path = f"/{self.cwd}"
        if not session.exists(full_path):
            session.mkdir(full_path)
    
        # Today
        today = datetime.today()
        yy = today.year
        mm = "{:02d}".format(today.month)
        dd = "{:02d}".format(today.day)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        upload_path = f"{full_path}/{self.id}/year={yy}/month={mm}/day={dd}/{timestamp}_{self.compressed_name}"
        live_path = f"{full_path}/{self.id}/live/{self.compressed_name}"

        self.__mkdir__(session, upload_path)
        self.__mkdir__(session, live_path)

        # Store the compressed file on partition date
        session.put(compressed_path, upload_path)
        # Store the configuration file on live folder
        session.put(compressed_path, live_path)

        session.close()

        configuration_upload, _ = self.send_configuration(configuration_path)
    
        return upload_path, configuration_upload

    def send_configuration(self, configuration_path: str):
        
        if self.credentials.__type__() != "sftp":
            raise Exception("Credentials are not of type FTP")

        if not os.path.exists(configuration_path):
            raise Exception("Configuration file does not exist")

        session = Connection(
            host=self.credentials.get_sftp_hostname(),
            username=self.credentials.get_sftp_username(),
            private_key=self.credentials.get_sftp_private_key(),
            private_key_pass=self.credentials.get_sftp_private_key_pass(),
            password=self.credentials.get_sftp_password(),
            port=self.credentials.get_sftp_port(),
            cnopts=self.cnopts
        )

        # Check if the mscli folder exists
        full_path = f"/{self.cwd}"
        if not session.exists(full_path):
            session.mkdir(full_path)

        # Today
        today = datetime.today()
        yy = today.year
        mm = "{:02d}".format(today.month)
        dd = "{:02d}".format(today.day)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        upload_path = f"{full_path}/{self.id}/year={yy}/month={mm}/day={dd}/{timestamp}_{self.configuration_name}"
        live_path = f"{full_path}/{self.id}/live/{self.configuration_name}"

        self.__mkdir__(session, upload_path)
        self.__mkdir__(session, live_path)

        # Store the configuration file on partition date
        session.put(configuration_path, upload_path)
        # Store the configuration file on live folder
        session.put(configuration_path, live_path)

        # Close the session
        session.close()

        return upload_path, live_path

    def get_files(self, compressed_output: str):
        
        if self.credentials.__type__()!= "sftp":
            raise Exception("Credentials are not of type FTP")
        
        session = Connection(
            host=self.credentials.get_sftp_hostname(),
            username=self.credentials.get_sftp_username(),
            private_key=self.credentials.get_sftp_private_key(),
            private_key_pass=self.credentials.get_sftp_private_key_pass(),
            password=self.credentials.get_sftp_password(),
            port=self.credentials.get_sftp_port(),
            cnopts=self.cnopts
        )

        # Check if the mscli folder exists
        full_path = f"/{self.cwd}"
        if not session.exists(full_path):
            raise Exception("mscli folder does not exist")

        file_path = f"{full_path}/{self.id}/live/{self.compressed_name}"
        # Retrieve live file
        session.get(file_path, compressed_output)
        # Close the session
        session.close()
        
        if not os.path.exists(compressed_output):
            raise Exception("Compressed file does not exist")

    def get_settings(self, settings_output: str):
        
        if self.credentials.__type__()!= "sftp":
            raise Exception("Credentials are not of type FTP")
        
        session = Connection(
            host=self.credentials.get_sftp_hostname(),
            username=self.credentials.get_sftp_username(),
            private_key=self.credentials.get_sftp_private_key(),
            private_key_pass=self.credentials.get_sftp_private_key_pass(),
            password=self.credentials.get_sftp_password(),
            port=self.credentials.get_sftp_port(),
            cnopts=self.cnopts
        )

        # Check if the mscli folder exists
        full_path = f"/{self.cwd}"
        if not session.exists(full_path):
            raise Exception("mscli folder does not exist")
        
        file_path = f"{full_path}/{self.id}/live/{self.configuration_name}"
        
        # Get the configuration file
        session.get(file_path, settings_output)
        
        # Close the session
        session.close()
        
        if not os.path.exists(settings_output):
            raise Exception("Configuration file does not exist")