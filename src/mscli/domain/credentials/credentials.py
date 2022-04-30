from ..entity.json_data import JSONData

class Credentials(JSONData):
    
    def __type__(self):
        return self.json_data["schema"]

    def __validate_aws__(self):
        return "aws_access_key_id" in self.json_data and \
            "aws_secret_access_key" in self.json_data and \
            "aws_bucket" in self.json_data and \
            "aws_region" in self.json_data and \
            "aws_prefix" in self.json_data

    def __aws_schema__(self):
        return {
            "schema": "aws",
            "aws_access_key_id": self.get_aws_access_key_id(),
            "aws_bucket": self.get_aws_bucket(),
            "aws_region": self.get_aws_region(),
            "aws_prefix": self.get_aws_prefix(),
        }

    def __validate_ftp__(self):
        return "username" in self.json_data and \
            "password" in self.json_data and \
            "hostname" in self.json_data

    def __ftp_schema__(self):
        return {
            "schema": "ftp",
            "username": self.get_ftp_username(),
            "hostname": self.get_ftp_hostname(),
            "port": self.get_ftp_port(),
        }

    def __validate_sftp__(self):
        return "username" in self.json_data and \
            "hostname" in self.json_data and \
            ("password" in self.json_data or "private_key" in self.json_data)

    def __sftp_schema__(self):
        return {
            "schema": "sftp",
            "username": self.get_sftp_username(),
            "hostname": self.get_sftp_hostname(),
            "port": self.get_sftp_port(),
        }

    def get_aws_access_key_id(self) -> str:
        if self.__type__() != "aws":
            raise Exception("Credentials type is not AWS")
        return self.json_data["aws_access_key_id"]
    
    def get_aws_secret_access_key(self) -> str:
        if self.__type__() != "aws":
            raise Exception("Credentials type is not AWS")
        return self.json_data["aws_secret_access_key"]

    def get_aws_bucket(self) -> str:
        if self.__type__() != "aws":
            raise Exception("Credentials type is not AWS")
        return self.json_data["aws_bucket"]

    def get_aws_region(self) -> str:
        if self.__type__() != "aws":
            raise Exception("Credentials type is not AWS")
        return self.json_data["aws_region"]

    def get_aws_prefix(self) -> str:
        if self.__type__() != "aws":
            raise Exception("Credentials type is not AWS")
        return self.json_data["aws_prefix"]    

    def get_ftp_username(self) -> str:
        if self.__type__()!= "ftp":
            raise Exception("Credentials type is not FTP")
        return self.json_data["username"]
    
    def get_ftp_password(self) -> str:
        if self.__type__()!= "ftp":
            raise Exception("Credentials type is not FTP")
        return self.json_data["password"]
    
    def get_ftp_hostname(self) -> str:
        if self.__type__()!= "ftp":
            raise Exception("Credentials type is not FTP")
        return self.json_data["hostname"]

    def get_ftp_port(self) -> int:
        if self.__type__()!= "ftp":
            raise Exception("Credentials type is not FTP")
        return self.json_data["port"] if "port" in self.json_data else 21

    def get_sftp_username(self) -> str:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["username"]
    
    def get_sftp_hostname(self) -> str:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["hostname"]
    
    def get_sftp_port(self) -> int:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["port"] if "port" in self.json_data else 22
    
    def get_sftp_password(self) -> str:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["password"] if "password" in self.json_data else None
    
    def get_sftp_private_key(self) -> str:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["private_key"] if "private_key" in self.json_data else None

    def get_sftp_private_key_pass(self) -> str:
        if self.__type__()!= "sftp":
            raise Exception("Credentials type is not SFTP")
        return self.json_data["private_key_pass"] if "private_key_pass" in self.json_data else None

    def get_schema(self):
        if self.__type__() == "aws":
            return self.__aws_schema__()
        elif self.__type__() == "ftp":
            return self.__ftp_schema__()
        elif self.__type__() == "sftp":
            return self.__sftp_schema__()
        else:
            raise Exception("Credentials type is not supported")

    def validate(self) -> bool:
        if self.__type__() == "aws":
            return self.__validate_aws__()
        elif self.__type__() == "ftp":
            return self.__validate_ftp__()
        elif self.__type__() == "sftp":
            return self.__validate_sftp__()
        else:
            raise Exception("Credentials type is not supported")
    
