from datetime import datetime
from ...domain.configuration.properties import Properties
from ... import __version__

class Properties1122(Properties):
    
    _available_properties = [
        "generator_settings",
        "op_permission_level",
        "allow_nether",
        "level_name",
        "enable_query",
        "allow_flight",
        "prevent_proxy_connections",
        "server_port",
        "max_world_size",
        "level_type",
        "enable_rcon",
        "force_gamemode",
        "level_seed",
        "server_ip",
        "network_compression_threshold",
        "max_build_height",
        "spawn_npcs",
        "white_list",
        "spawn_animals",
        "snooper_enabled",
        "hardcore",
        "resource_pack_sha1",
        "online_mode",
        "resource_pack",
        "pvp",
        "difficulty",
        "enable_command_block",
        "player_idle_timeout",
        "gamemode",
        "max_players",
        "max_tick_time",
        "spawn_monsters",
        "generate_structures",
        "view_distance",
        "motd"
    ]

    # Default Settings (1.12.2)
    generator_settings = None
    op_permission_level = 4
    allow_nether = True
    level_name = "world"
    enable_query = False
    allow_flight = False
    prevent_proxy_connections = False
    server_port = 25565
    max_world_size = 29999984
    level_type = "DEFAULT"
    enable_rcon = False
    force_gamemode = False
    level_seed = None
    server_ip = None
    network_compression_threshold = 256
    max_build_height = 256
    spawn_npcs = True
    white_list = False
    spawn_animals = True
    snooper_enabled = True
    hardcore = False
    resource_pack_sha1 = None
    online_mode = True
    resource_pack = None
    pvp = True
    difficulty = 1
    enable_command_block = False
    player_idle_timeout = 0
    gamemode = 0
    max_players = 20
    max_tick_time = 60000
    spawn_monsters = True
    generate_structures = True
    view_distance = 10
    motd = "A Minecraft Server"

    def __init__(self, json_data):
        super().__init__(json_data)
        self.__load_properties__()

    def __load_properties__(self, json_data: dict = None):
        data = self.json_data
        if json_data is not None:
            data = json_data
        for k, value in data.items():
            k = k.replace("-", "_")
            setattr(self, k, value)

    @staticmethod
    def from_properties(properties_file: str):
        lines = None
        with open(properties_file, "r") as file:
            lines = file.readlines()
            file.close()
        json = Properties.__properties_to_json__(lines)
        return Properties1122(json_data=json)

    def save(self, output_file: str):
        with open(output_file, "w") as file:
            file.write("#Minecraft server properties\n")
            file.write("#Generated on " + str(datetime.now()) + "\n")
            file.write("#Using mscli version " + __version__ + " (https://www.github.com/pomaretta/mscli)" + "\n")
            for property in self._available_properties:
                v = getattr(self, property)
                if isinstance(v, bool):
                    v = "true" if v else "false"
                if v == None:
                    v = ""
                d = f"{property.replace('_', '-').replace('_d_', '.')}={v}\n"
                if property == "motd":
                    d = f"{property.replace('_', '-').replace('_d_', '.')}={repr(v.encode('utf-8'))}\n"
                file.write(
                    d
                )
            file.close()

class Properties118(Properties):
    
    _available_properties = [
        "enable_jmx_monitoring"
        ,"rcon_d_port"
        ,"gamemode"
        ,"enable_command_block"
        ,"enable_query"
        ,"level_name"
        ,"level_seed"
        ,"motd"
        ,"query_d_port"
        ,"pvp"
        ,"difficulty"
        ,"network_compression_threshold"
        ,"require_resource_pack"
        ,"max_tick_time"
        ,"use_native_transport"
        ,"max_players"
        ,"online_mode"
        ,"enable_status"
        ,"allow_flight"
        ,"broadcast_rcon_to_ops"
        ,"view_distance"
        ,"server_ip"
        ,"resource_pack_prompt"
        ,"allow_nether"
        ,"server_port"
        ,"enable_rcon"
        ,"sync_chunk_writes"
        ,"op_permission_level"
        ,"prevent_proxy_connections"
        ,"hide_online_players"
        ,"resource_pack"
        ,"entity_broadcast_range_percentage"
        ,"simulation_distance"
        ,"rcon_d_password"
        ,"player_idle_timeout"
        ,"force_gamemode"
        ,"rate_limit"
        ,"hardcore"
        ,"white_list"
        ,"broadcast_console_to_ops"
        ,"spawn_npcs"
        ,"spawn_animals"
        ,"function_permission_level"
        ,"text_filtering_config"
        ,"spawn_monsters"
        ,"enforce_whitelist"
        ,"resource_pack_sha1"
        ,"spawn_protection"
        ,"max_world_size"
    ]

    # Default Settings (1.18)
    enable_jmx_monitoring = False
    rcon_d_port = 25575
    gamemode = "survival"
    enable_command_block = False
    enable_query = False
    level_name = "world"
    level_seed = None
    motd = "A Minecraft Server"
    query_d_port = 25565
    pvp = True
    difficulty = "easy"
    network_compression_threshold = 256
    require_resource_pack = False
    max_tick_time = 60000
    use_native_transport = True
    max_players = 20
    online_mode = True
    enable_status = True
    allow_flight = False
    broadcast_rcon_to_ops = True
    view_distance = 10
    server_ip = None
    resource_pack_prompt = None
    allow_nether = True
    server_port = 25565
    enable_rcon = False
    sync_chunk_writes = True
    op_permission_level = 4
    prevent_proxy_connections = False
    hide_online_players = False
    resource_pack = None
    entity_broadcast_range_percentage = 100
    simulation_distance = 10
    rcon_d_password = None
    player_idle_timeout = 0
    force_gamemode = False
    rate_limit = 0
    hardcore = False
    white_list = False
    broadcast_console_to_ops = True
    spawn_npcs = True
    spawn_animals = True
    function_permission_level = 2
    text_filtering_config = None
    spawn_monsters = True
    enforce_whitelist = False
    resource_pack_sha1 = None
    spawn_protection = 16
    max_world_size = 29999984

    def __init__(self, json_data):
        super().__init__(json_data)
        self.__load_properties__()

    def __load_properties__(self, json_data: dict = None):
        data = self.json_data
        if json_data is not None:
            data = json_data
        for k, value in data.items():
            k = k.replace("-", "_").replace(".", "_d_")
            setattr(self, k, value)
   
    @staticmethod
    def from_properties(properties_file: str):
        lines = None
        with open(properties_file, "r") as file:
            lines = file.readlines()
            file.close()
        json = Properties.__properties_to_json__(lines)
        return Properties118(json_data=json)

    def save(self, output_file: str):
        with open(output_file, "w") as file:
            file.write("#Minecraft server properties\n")
            file.write("#Generated on " + str(datetime.now()) + "\n")
            file.write("#Using mscli version " + __version__ + " (https://www.github.com/pomaretta/mscli)" + "\n")
            for property in self._available_properties:
                v = getattr(self, property)
                if isinstance(v, bool):
                    v = "true" if v else "false"
                if v == None:
                    v = ""
                d = f"{property.replace('_', '-').replace('_d_', '.')}={v}\n"
                if property == "motd":
                    d = f"{property.replace('_', '-').replace('_d_', '.')}={repr(v.encode('utf-8'))}\n"
                file.write(
                    d
                )
            file.close()