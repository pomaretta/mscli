import hashlib
import logging
import shutil
import os
import tarfile

from ...domain.pipeline.stage import Stage
from ...domain.builders.builder import MinecraftBuilder
from ...shared.files import remove_directory, create_directories
from datetime import datetime

class CompressDirectory(Stage):

    exclude_dirs = [
        "logs", # NOTE: Not include logs in the compressed file
        "libraries", # NOTE: Not include libraries
        "versions", # NOTE: Not include versions in the compressed file
    ]
    exclude_files = [
        ".DS_Store" # NOTE: This is a MacOS file
    ]

    def __init__(self,builder:  MinecraftBuilder, stage_id: str, name: str, description: str, directory_path: list, output_path: str, output: list = None):
        super().__init__(builder, stage_id, name, description)
        self.directory_path = directory_path
        self.output_path = output_path
        self.output = output

    def run(self):
        
        if len(self.directory_path) == 0:
            logging.error("No directory path given")
            self._failed = True
            self._completed = True
            return False

        directory = self.directory_path[0]

        if not os.path.isdir(directory):
            logging.error("Directory does not exist")
            self._failed = True
            self._completed = True
            return False

        yy, mm, dd, HH, MM, ss = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S").split("-")

        output_compressed = os.path.join(
            self.output_path,
            f"build_{self.builder.provider.name}-{self.builder.provider.version}_{yy}-{mm}-{dd}-{HH}-{MM}-{ss}"
        )

        # TODO: Use tarfile to compress the directory
        tar = tarfile.open(output_compressed + ".tar.gz", "w:gz")
        for root, dirs, files in os.walk(directory, topdown=True):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            files[:] = [f for f in files if f not in self.exclude_files]
            for file in files:
                with open(os.path.join(root, file), "rb") as f:
                    # NOTE: Add the file to the tarfile
                    tar.addfile(
                        tarinfo=tarfile.TarInfo(os.path.join(root, file)),
                        fileobj=f.read()
                    )
        tar.close()

        if not os.path.exists(output_compressed + ".tar.gz"):
            logging.error("Failed to create compressed file")
            self._failed = True
            self._completed = True
            return False

        # Calculate checksum
        checksum = None

        with open(output_compressed + ".tar.gz", 'rb') as f:
            data = f.read()
            checksum = hashlib.md5(data).hexdigest()
            f.close()

        self._output.append(output_compressed + ".tar.gz")
        self._output.append(checksum)
        if self.output is not None:
            self.output.append(output_compressed + ".tar.gz")
            self.output.append(checksum)
        self._completed = True
        return True

class UncompressDirectory(Stage):

    def __init__(self,builder:  MinecraftBuilder, stage_id: str, name: str, description: str, compressed_path: list, output_path: str, output: list = None):
        super().__init__(builder, stage_id, name, description)
        self.compressed_path = compressed_path
        self.output_path = output_path
        self.output = output

    def run(self):
        
        if len(self.compressed_path) == 0:
            logging.error("No compressed path given")
            self._failed = True
            self._completed = True
            return False

        compressed_path = self.compressed_path[0]

        if not os.path.exists(compressed_path):
            logging.error("Compressed file does not exist")
            self._failed = True
            self._completed = True
            return False

        # shutil.unpack_archive(
        #     compressed_path,
        #     self.output_path,
        #     format='zip'
        # )
        # if not os.path.exists(self.output_path):
        #     logging.error("Failed to uncompress file")
        #     self._failed = True
        #     self._completed = True
        #     return False

        # Remove old data
        remove_directory(self.output_path)
        # Create new directory
        create_directories(self.output_path)

        # Unpack new data
        shutil.unpack_archive(
            compressed_path,
            self.output_path,
            format='gztar'
        )

        if not os.path.exists(self.output_path):
            logging.error("Failed to uncompress file")
            self._failed = True
            self._completed = True
            return False

        self._output.append(self.output_path)
        if self.output is not None:
            self.output.append(self.output_path)
        self._completed = True
        return True