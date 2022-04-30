__command__ = "server"

import sys
import os

from typing import Optional, List
from mscli.cli.util.run import run_subcommand_with_prefix
from argparse import ArgumentParser

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
        ,prefix='server'
        ,avialable_subcommands=['import', 'run', 'create', 'update', 'export', 'rm']
        ,subcommand_args=args.args
        ,pwd=os.getcwd()
        # KWARGS
        ,**kwargs
    )