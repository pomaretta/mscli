import logging
import pathlib
import shutil

def remove_directory(path: str) -> None:
    """
    Remove a directory. If the directory does not exist, do nothing.
    """
    logging.debug("Removing directory: %s", path)
    shutil.rmtree(path, ignore_errors=False)

def create_directory(path: str) -> None:
    """
    Create a directory. If the directory already exists, do nothing.
    """
    logging.debug("Creating directory: %s", path)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)

def create_directories(*args) -> None:
    """
    Create directories. If the directories already exist, do nothing.
    """
    for path in args:
        create_directory(path)