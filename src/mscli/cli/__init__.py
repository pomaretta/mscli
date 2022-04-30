"""
Minecraft Server Command Line Interface
"""

# AVAILABLE COMMANDS
META_COMMANDS = [
    # "create", # Create a new server
    "update", # Update an existing server
    "start", # Start a server
    # "ls", # List servers
    # "rm" # Remove a server    
    "version", # Print the version of mscli
    "server", # Run a server command
    "credentials", # Manage credentials
    "ps", # List running servers
]

from .cli import main