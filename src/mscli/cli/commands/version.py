__command__ = "version"

from typing import Optional, List
from mscli import __version__

def main(
    argv: Optional[List[str]] = None
    ,pwd: str = None
    ,**kwargs
) -> bool:
    print("Currently installed version: {}".format(__version__))
    return True