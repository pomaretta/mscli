from typing import List
from importlib import import_module
from .. import META_COMMANDS

def run_subcommand(
    subcommand: str
    ,subcommand_args: List[str] = None
    ,pwd: str = None
    ,**kwargs
):
    """
    Run the given command.
    """

    subcommand_args = subcommand_args or []

    if subcommand not in META_COMMANDS:
        return False

    module = import_module(
        "mscli.cli.commands.{}".format(subcommand)
        ,__package__
    )
    
    return module.main(
        argv=subcommand_args
        ,pwd=pwd
        ,**kwargs
    )

def run_subcommand_with_prefix(
    subcommand: str
    ,prefix: str
    ,avialable_subcommands: List[str]
    ,subcommand_args: List[str] = None
    ,pwd: str = None
    ,**kwargs
):
    """
    Run the given command.
    """

    subcommand_args = subcommand_args or []

    if subcommand not in avialable_subcommands:
        return False

    module = import_module(
        "mscli.cli.commands.{}_{}".format(prefix,subcommand)
        ,__package__
    )
    
    return module.main(
        argv=subcommand_args
        ,pwd=pwd
        ,**kwargs
    )