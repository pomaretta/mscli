__command__ = "server_create"

import os

from typing import Optional, List
from mscli import __version__
from argparse import ArgumentParser

from ..util.run import run_subcommand_with_prefix

def main(
    argv: Optional[List[str]] = None
    ,pwd: str = None
    ,**kwargs
) -> bool:
    
    parser = ArgumentParser()

    parser.add_argument(
        'command'
        ,nargs=1
        ,type=str
        ,help="The command to be executed."
    )

    parser.add_argument(
        'args'
        ,nargs="*"
        ,type=str
        ,help="The command arguments to be used by the subcommand."
    )
    
    args = parser.parse_args(argv)

    return run_subcommand_with_prefix(
        subcommand=args.command[0].lower()
        ,prefix='server_create'
        ,avialable_subcommands=[
            'forge',
            'vanilla'
        ]
        ,subcommand_args=args.args
        ,pwd=os.getcwd()
        # KWARGS
        ,**kwargs
    )