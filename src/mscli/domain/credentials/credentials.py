import os
from re import L
from ..entity.json_data import JSONData

class Credentials(JSONData):
    
    profile = None

    def __init__(self, json_data: dict = None, configuration_path: str = os.path.expanduser("~/.mscli/config/credentials.json")):
        super().__init__(json_data)
        self.configuration_path = configuration_path

    def __type__(self):
        if self.profile is None and not self.__profile_exists__(self.profile):
            raise Exception("Profile does not exist")
        return self.json_data["schema"] if self.profile is None else self.json_data["profiles"][self.profile]["schema"]

    def __validate_aws__(self):
        if self.profile is None:
            return "aws_access_key_id" in self.json_data and \
            "aws_secret_access_key" in self.json_data and \
            "aws_bucket" in self.json_data and \
            "aws_region" in self.json_data and \
            "aws_prefix" in self.json_data
        else:
            if not self.__profile_exists__(self.profile):
                raise Exception("Profile does not exist")
            return "aws_access_key_id" in self.json_data["profiles"][self.profile] and \
            "aws_secret_access_key" in self.json_data["profiles"][self.profile] and \
            "aws_bucket" in self.json_data["profiles"][self.profile] and \
            "aws_region" in self.json_data["profiles"][self.profile] and \
            "aws_prefix" in self.json_data["profiles"][self.profile]

    def __aws_schema__(self):
        data = {
            "schema": "aws",
            "aws_access_key_id": self.get_aws_access_key_id(),
            "aws_secret_access_key": self.get_aws_secret_access_key(),
            "aws_bucket": self.get_aws_bucket(),
            "aws_region": self.get_aws_region(),
            "aws_prefix": self.get_aws_prefix(),
        }
        if self.profile is not None:
            data["profile"] = self.profile
        return data

    def __validate_ftp__(self):
        if self.profile is None:
            return "username" in self.json_data and \
                "password" in self.json_data and \
                "hostname" in self.json_data
        else:
            if not self.__profile_exists__(self.profile):
                raise Exception("Profile does not exist")
            return "username" in self.json_data["profiles"][self.profile] and \
                "password" in self.json_data["profiles"][self.profile] and \
                "hostname" in self.json_data["profiles"][self.profile]

    def __ftp_schema__(self):
        data = {
            "schema": "ftp",
            "username": self.get_ftp_username(),
            "password": self.get_ftp_password(),
            "hostname": self.get_ftp_hostname(),
            "port": self.get_ftp_port(),
        }
        if self.profile is not None:
            data["profile"] = self.profile
        return data

    def __validate_sftp__(self):
        if self.profile is None:
            return "username" in self.json_data and \
                "hostname" in self.json_data and \
                ("password" in self.json_data or "private_key" in self.json_data)
        else:
            if not self.__profile_exists__(self.profile):
                raise Exception("Profile does not exist")
            return "username" in self.json_data["profiles"][self.profile] and \
                "hostname" in self.json_data["profiles"][self.profile] and \
                ("password" in self.json_data["profiles"][self.profile] or "private_key" in self.json_data["profiles"][self.profile])

    def __sftp_schema__(self):
        data = {
            "schema": "sftp",
            "username": self.get_sftp_username(),
            "password": self.get_sftp_password(),
            "hostname": self.get_sftp_hostname(),
            "port": self.get_sftp_port(),
            "private_key": self.get_sftp_private_key(),
            "private_key_pass": self.get_sftp_private_key_pass(),
        }
        if self.profile is not None:
            data["profile"] = self.profile
        return data

    def __profile_exists__(self, profile: str) -> bool:
        return profile in self.json_data["profiles"]

    def get_aws_access_key_id(self) -> str:
        if self.__type__() != "aws":
            raise Exception("Credentials type is not AWS")
        return self.json_data["aws_access_key_id"] if self.profile is None else self.json_data["profiles"][self.profile]["aws_access_key_id"]
    
    def get_aws_secret_access_key(self) -> str:
        if self.__type__() != "aws":
            raise Exception("Credentials type is not AWS")
        return self.json_data["aws_secret_access_key"] if self.profile is None else self.json_data["profiles"][self.profile]["aws_secret_access_key"]

    def get_aws_bucket(self) -> str:
        if self.__type__() != "aws":
            raise Exception("Credentials type is not AWS")
        return self.json_data["aws_bucket"] if self.profile is None else self.json_data["profiles"][self.profile]["aws_bucket"]

    def get_aws_region(self) -> str:
        if self.__type__() != "aws":
            raise Exception("Credentials type is not AWS")
        return self.json_data["aws_region"] if self.profile is None else self.json_data["profiles"][self.profile]["aws_region"]

    def get_aws_prefix(self) -> str:
        if self.__type__() != "aws":
            raise Exception("Credentials type is not AWS")
        return self.json_data["aws_prefix"] if self.profile is None else self.json_data["profiles"][self.profile]["aws_prefix"]    

    def get_ftp_username(self) -> str:
        if self.__type__()!= "ftp":
            raise Exception("Credentials type is not FTP")
        return self.json_data["username"] if self.profile is None else self.json_data["profiles"][self.profile]["username"]
    
    def get_ftp_password(self) -> str:
        if self.__type__()!= "ftp":
            raise Exception("Credentials type is not FTP")
        return self.json_data["password"] if self.profile is None else self.json_data["profiles"][self.profile]["password"]
    
    def get_ftp_hostname(self) -> str:
        if self.__type__()!= "ftp":
            raise Exception("Credentials type is not FTP")
        return self.json_data["hostname"] if self.profile is None else self.json_data["profiles"][self.profile]["hostname"]

    def get_ftp_port(self) -> int:
        if self.__type__()!= "ftp":
            raise Exception("Credentials type is not FTP")
        return self.json_data["port"] if "port" in self.json_data else 21 if self.profile is None else self.json_data["profiles"][self.profile]["port"] if "port" in self.json_data["profiles"][self.profile] else 21

    def get_sftp_username(self) -> str:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["username"] if self.profile is None else self.json_data["profiles"][self.profile]["username"]
    
    def get_sftp_hostname(self) -> str:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["hostname"] if self.profile is None else self.json_data["profiles"][self.profile]["hostname"]
    
    def get_sftp_port(self) -> int:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["port"] if "port" in self.json_data else 22 if self.profile is None else self.json_data["profiles"][self.profile]["port"] if "port" in self.json_data["profiles"][self.profile] else 22
    
    def get_sftp_password(self) -> str:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["password"] if "password" in self.json_data else None if self.profile is None else self.json_data["profiles"][self.profile]["password"] if "password" in self.json_data["profiles"][self.profile] else None
    
    def get_sftp_private_key(self) -> str:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["private_key"] if "private_key" in self.json_data else None if self.profile is None else self.json_data["profiles"][self.profile]["private_key"] if "private_key" in self.json_data["profiles"][self.profile] else None

    def get_sftp_private_key_pass(self) -> str:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["private_key_pass"] if "private_key_pass" in self.json_data else None if self.profile is None else self.json_data["profiles"][self.profile]["private_key_pass"] if "private_key_pass" in self.json_data["profiles"][self.profile] else None

    def get_schema(self):
        if self.__type__() == "aws":
            return self.__aws_schema__()
        elif self.__type__() == "ftp":
            return self.__ftp_schema__()
        elif self.__type__() == "sftp":
            return self.__sftp_schema__()
        else:
            raise Exception("Credentials type is not supported")

    def set_profile(self, profile: str):
        if not self.__profile_exists__(profile):
            raise Exception("Profile does not exist")
        self.profile = profile

    def validate(self) -> bool:
        if self.__type__() == "aws":
            return self.__validate_aws__()
        elif self.__type__() == "ftp":
            return self.__validate_ftp__()
        elif self.__type__() == "sftp":
            return self.__validate_sftp__()
        else:
            raise Exception("Credentials type is not supported")

    def __validate_aws_with_data__(self, data) -> bool:
        return "aws_access_key_id" in data and \
            "aws_secret_access_key" in data and \
            "aws_bucket" in data and \
            "aws_region" in data and \
            "aws_prefix" in data
            

    def __save_aws__(self, data):
        # Validate AWS
        if not self.__validate_aws_with_data__(data):
            raise Exception("AWS credentials are not valid")
        # Save AWS
        self.json_data["aws_access_key_id"] = data["aws_access_key_id"]
        self.json_data["aws_secret_access_key"] = data["aws_secret_access_key"]
        self.json_data["aws_bucket"] = data["aws_bucket"]
        self.json_data["aws_region"] = data["aws_region"]
        self.json_data["aws_prefix"] = data["aws_prefix"]
        self.json_data["schema"] = "aws"
        
    def __validate_ftp_with_data__(self, data):
        return "username" in data and \
            "password" in data and \
            "hostname" in data

    def __save_ftp__(self, data):
        if not self.__validate_ftp_with_data__(data):
            raise Exception("FTP credentials are not valid")
        self.json_data["username"] = data["username"]
        self.json_data["password"] = data["password"]
        self.json_data["hostname"] = data["hostname"]
        self.json_data["port"] = data["port"] if "port" in data else 21
        self.json_data["schema"] = "ftp"

    def __validate_sftp_with_data__(self, data):
        return "username" in data and \
            "hostname" in data and \
            ("password" in data or "private_key" in data)

    def __save_sftp__(self, data):
        if not self.__validate_sftp_with_data__(data):
            raise Exception("SFTP credentials are not valid")
        self.json_data["username"] = data["username"]
        self.json_data["hostname"] = data["hostname"]
        self.json_data["port"] = data["port"] if "port" in data else 22
        self.json_data["password"] = data["password"] if "password" in data else None
        self.json_data["private_key"] = data["private_key"] if "private_key" in data else None
        self.json_data["private_key_pass"] = data["private_key_pass"] if "private_key_pass" in data else None
        self.json_data["schema"] = "sftp"

    def save_data(self, schema: str, data: dict):
        if schema == "aws":
            self.__save_aws__(data)
        elif schema == "ftp":
            self.__save_ftp__(data)
        elif schema == "sftp":
            self.__save_sftp__(data)
        else:
            raise Exception("Credentials type is not supported")

    def upsert_profile(self, profile: str, data: dict):
        # Validate DATA
        if not "schema" in data:
            raise Exception("Credentials schema is not valid")
        schema_type = data["schema"]
        if schema_type == "aws" and not self.__validate_aws_with_data__(data):
            raise Exception("AWS credentials are not valid")
        if schema_type == "ftp" and not self.__validate_ftp_with_data__(data):
            raise Exception("FTP credentials are not valid")
        if schema_type == "sftp" and not self.__validate_sftp_with_data__(data):
            raise Exception("SFTP credentials are not valid")
        self.json_data["profiles"][profile] = data
        self.dump(
            data=self.json_data,
            configuration_file=self.configuration_path
        )

    def remove_profile(self, profile: str):
        if not self.__profile_exists__(profile):
            raise Exception("Profile does not exist")
        del self.json_data["profiles"][profile]
        self.dump(
            data=self.json_data,
            configuration_file=self.configuration_path
        )

    def current_profile(self):
        return self.profile
    
