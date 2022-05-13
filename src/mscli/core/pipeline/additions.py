import logging
import os
import shutil
import requests

from datetime import datetime
from ...domain.pipeline.stage import Stage

from ..configuration.server import ForgeServer
from ..configuration.mods import MinecraftMods, Mod

from ...shared.files import create_directories

class AddMods(Stage):

    def __add_mod__(self, mod: Mod, mods_folder: str, tmp_folder: str):
        logging.info(f"Adding mod {mod.name}")

        mod_path = os.path.join(
            tmp_folder,
            f"{mod.name}_{mod.version}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.jar"
        )

        # Download mod
        r = requests.get(mod.url)
        with open(mod_path, 'wb') as f:
            f.write(r.content)
            f.close()
    
        # Add to mods folder
        shutil.move(
            mod_path,
            os.path.join(mods_folder, os.path.basename(mod_path))
        )

    def run(self):
        
        server: ForgeServer = self.builder.server

        if server.get_mods() is None:
            logging.info("No mods to add.")
            self._completed = True
            return

        mods_folder = os.path.join(
            self.builder.configuration.get_paths()["files"],
            self.builder.provider.get_files().get_src(),
            'mods'
        )
        tmp_folder = os.path.join(
            self.builder.configuration.get_paths()["files"],
            self.builder.provider.get_files().get_tmp()
        )

        # Create mods folder
        create_directories(mods_folder)

        logging.info("Adding mods...")

        mods = server.get_mods()

        for mod in mods.get_mods():
            logging.info("Adding mod: " + mod.name)
            try:
                self.__add_mod__(mod, mods_folder=mods_folder, tmp_folder=tmp_folder)
            except Exception as e:
                logging.error(f"Failed to add mod {mod.name}")
                continue
                
        logging.info("Mods added.")
        self._completed = True
        return
        
class AddWorld(Stage):
    
    def run(self):
        
        server: ForgeServer = self.builder.server

        if server.get_world() is None:
            logging.info("No world to add.")
            self._completed = True
            return

        if not os.path.isdir(server.get_world()):
            logging.error("World path is not a directory.")
            self._failed = True
            self._completed = True
            return

        world_name = 'word'
        if server.get_properties() is not None:
            world_name = server.get_properties().level_name

        world_path = os.path.join(
            self.builder.configuration.get_paths()["files"],
            self.builder.provider.get_files().get_src(),
            world_name
        )

        # Copy folder
        shutil.copytree(
            server.get_world(),
            world_path
        )

        logging.info("World added.")
        self._completed = True
        return

class AddIcon(Stage):

    def run(self):
        
        server: ForgeServer = self.builder.server

        if server.get_icon() is None:
            logging.info("No icon to add.")
            self._completed = True
            return

        if not os.path.exists(server.get_icon()):
            logging.error("Icon path does not exist.")
            self._failed = True
            self._completed = True
            return

        icon_path = os.path.join(
            self.builder.configuration.get_paths()["files"],
            self.builder.provider.get_files().get_src(),
            'server-icon.png'
        )

        # Copy icon
        shutil.copyfile(
            server.get_icon(),
            icon_path
        )

        logging.info("Icon added.")
        self._completed = True
        return

class AddProperties(Stage):
    
    def run(self):
        
        server: ForgeServer = self.builder.server

        if server.get_properties() is None:
            logging.info("No properties to add.")
            self._completed = True
            return
        
        properties_path = os.path.join(
            self.builder.configuration.get_paths()["files"],
            self.builder.provider.get_files().get_src(),
            'server.properties'
        )

        logging.info("Adding properties...")

        properties = server.get_properties()
        properties.save(properties_path)

        if not os.path.exists(properties_path):
            logging.error("Failed to add properties.")
            self._failed = True
            self._completed = True
            return
        
        logging.info("Properties added.")
        self._completed = True
        return
