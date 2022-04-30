from datetime import datetime
import os

from ...domain.storage.storage import Storage
from ...domain.configuration.configuration import Configuration
from ...domain.credentials.credentials import Credentials
from ...domain.versions.provider import Provider

from ftplib import FTP

class FTPStorage(Storage):
    
    compressed_name = "files.zip"
    configuration_name = "settings.json"
    cwd = "mscli"

    def __init__(self, configuration: Configuration, credentials: Credentials, provider: Provider, id: str):
        super().__init__(configuration, credentials)
        self.provider = provider
        self.id = id

    def __mkdir__(self, session: FTP, required_dir: str):
        required_dir = required_dir.split('/')[:-1]
        current_cwd = session.pwd()
        for path_item in required_dir:
            if path_item.strip() == '':
                continue
            path_item = path_item.replace('/', '')
            try:
                session.cwd(path_item)
            except:
                session.mkd(path_item)
                session.cwd(path_item)
        session.cwd(current_cwd)

    def send_files(self, compressed_path: str, configuration_path: str):
        
        if self.credentials.__type__() != "ftp":
            raise Exception("Credentials are not of type FTP")

        if not os.path.exists(compressed_path):
            raise Exception("Compressed file does not exist")

        if not os.path.exists(configuration_path):
            raise Exception("Configuration file does not exist")

        session = FTP(
            host=self.credentials.get_ftp_hostname(),
            user=self.credentials.get_ftp_username(),
            passwd=self.credentials.get_ftp_password()
        )

        # Check if the mscli folder exists
        full_path = f"/{self.cwd}"
        try:
            full_path = session.mkd(self.cwd)
        except:
            pass

        # Open the compressed file
        compressed_file = open(compressed_path, "rb")
    
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
        session.storbinary(f"STOR {upload_path}", compressed_file)

        compressed_file = open(compressed_path, "rb")

        # Store the configuration file on live folder
        session.storbinary(f"STOR {live_path}", compressed_file)

        # Close the compressed file
        compressed_file.close()
        session.quit()

        self.send_configuration(configuration_path)
    
        return upload_path, live_path

    def send_configuration(self, configuration_path: str):
        
        if self.credentials.__type__() != "ftp":
            raise Exception("Credentials are not of type FTP")

        if not os.path.exists(configuration_path):
            raise Exception("Configuration file does not exist")

        session = FTP(
            host=self.credentials.get_ftp_hostname(),
            user=self.credentials.get_ftp_username(),
            passwd=self.credentials.get_ftp_password()
        )

        # Check if the mscli folder exists
        full_path = f"/{self.cwd}"
        try:
            full_path = session.mkd(self.cwd)
        except:
            pass

        # Today
        today = datetime.today()
        yy = today.year
        mm = "{:02d}".format(today.month)
        dd = "{:02d}".format(today.day)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        configuration_file = open(configuration_path, "rb")
        
        upload_path = f"{full_path}/{self.id}/year={yy}/month={mm}/day={dd}/{timestamp}_{self.configuration_name}"
        live_path = f"{full_path}/{self.id}/live/{self.configuration_name}"

        self.__mkdir__(session, upload_path)
        self.__mkdir__(session, live_path)

        # Store the configuration file on partition date
        session.storbinary(f"STOR {upload_path}", configuration_file)

        configuration_file = open(configuration_path, "rb")

        # Store the configuration file on live folder
        session.storbinary(f"STOR {live_path}", configuration_file)

        # Close the configuration file
        configuration_file.close()
        # Close the session
        session.quit()

        return upload_path, live_path

    def get_files(self, compressed_output: str):
        
        if self.credentials.__type__()!= "ftp":
            raise Exception("Credentials are not of type FTP")
        
        session = FTP(
            host=self.credentials.get_ftp_hostname(),
            user=self.credentials.get_ftp_username(),
            passwd=self.credentials.get_ftp_password()
        )

        # Check if the mscli folder exists
        full_path = f"/{self.cwd}"
        try:
            full_path = session.mkd(self.cwd)
        except:
            pass
            
        # Get the compressed file
        compressed_file = open(compressed_output, "wb")
        # Retrieve live file
        session.retrbinary(f"RETR {full_path}/{self.id}/live/{self.compressed_name}", compressed_file.write)
        compressed_file.close()
        
        # Close the session
        session.quit()
        
        if not os.path.exists(compressed_output):
            raise Exception("Compressed file does not exist")

    def get_settings(self, settings_output: str):
        
        if self.credentials.__type__()!= "ftp":
            raise Exception("Credentials are not of type FTP")
        
        session = FTP(
            host=self.credentials.get_ftp_hostname(),
            user=self.credentials.get_ftp_username(),
            passwd=self.credentials.get_ftp_password()
        )

        # Check if the mscli folder exists
        full_path = f"/{self.cwd}"
        try:
            full_path = session.mkd(self.cwd)
        except:
            pass
        
        # Get the configuration file
        configuration_file = open(settings_output, "wb")
        session.retrbinary(f"RETR {full_path}/{self.id}/live/{self.configuration_name}", configuration_file.write)
        configuration_file.close()
        
        # Close the session
        session.quit()
        
        if not os.path.exists(settings_output):
            raise Exception("Configuration file does not exist")