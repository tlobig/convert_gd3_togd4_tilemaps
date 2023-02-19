import re
from parser_util import is_valid_target_version, is_valid_tile_map, header_line_to_dict, str_of_floats_to_list_of_floats
from collections.abc import Iterable
from UID_tools import UID
from tile_set import TileSet
class SceneWithTileMap:
    def __init__(self) -> None:
        pass

    # def

    def parse_tile_map(lines: Iterable[str],known_tilesets: TileSet):
        tm = SceneWithTileMap()
        id_to_tileset_dict = {}
        index = 0
        while index < len(lines):
            line = lines[index]
            if line.find('type="TileSet"') != -1:
                match_path = re.search(r'path=\"([\w:\/\.]+)\"',line)
                if match_path:
                    match_id = re.search(r'id=(\d+)',line)
                    if match_id:
                        id = int(match_id.group(1))
                        path = match_path.group(1)
                        if path in known_tilesets:
                            id_to_tileset_dict[id] = known_tilesets[path]
                # continue parsing the tilemap until we find the end of it
                # manipulating the running index is evil, don't do as I do, kids
                while index + 1 < len(lines):
                    index += 1
                    line = lines[index]
                    if line.startswith("[node"):
                        pass
            else:
                pass
            index += 1
        return None
