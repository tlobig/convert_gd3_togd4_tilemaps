import re
from gd4_type_names import GD4Types
from parser_util import is_valid_target_version, is_valid_tile_map, header_line_to_dict, str_of_floats_to_list_of_floats
from collections.abc import Iterable
from UID_tools import UID
from tile_set import TileSet
class SceneWithTileMap:
    def __init__(self) -> None:
        self.lines = []
        pass

    # def

    def parse_tile_map(lines: Iterable[str],known_tilesets: TileSet):
        tm = SceneWithTileMap()
        id_to_tileset_dict = {}
        match_format = re.search(r'(^\[[\w\s=]+format=)2([\w\s=]*])',lines[0]) # match whole string but not format version
        if match_format:
            tm.lines.append(match_format.group(1)+"3"+match_format.group(2)+"\n")
        else:
            tm.lines.append(lines[0])
        index = 1
        while index < len(lines):
            line = lines[index]
            if line.startswith("[ext_resource"):
                match_ext_resource = re.search(r'^\[[\w\s_=\":\/.]+path=\"([\w\s_=\":\/.]+)\"\s*type=\"([\w\d]+)\"\s*id\=(\d+)]',line)
                if match_ext_resource:
                    res_path = match_ext_resource.group(1)
                    res_type = GD4Types.godot3_to_godot4_type_name(match_ext_resource.group(2))
                    res_id =  match_ext_resource.group(3)
                    if line.find('type="TileSet"') != -1:
                        match_path = re.search(r'path=\"([\w:\/\.]+)\"',line)
                        if match_path:
                            match_id = re.search(r'id=(\d+)',line)
                            if match_id:
                                id = int(match_id.group(1))
                                path = match_path.group(1)
                                if path in known_tilesets:
                                    id_to_tileset_dict[id] = known_tilesets[path]
                    tm.lines.append('[ext_resource type="{0}" path="{1}" id="{2}"]\n'.format(res_type,res_path,res_id))

            elif line.startswith("[node"):
                if line.find('type="TileMap"') != -1:                
                    tm.lines.append(line)
                    # continue parsing the tilemap until we find the end of it
                    # manipulating the running index is evil, don't do as I do, kids
                    res_id = None
                    while index + 1 < len(lines):
                        index += 1
                        line = lines[index]
                        if line.startswith("[node"):
                            index -= 1
                            break
                        elif line.startswith("cell_size"): # ignore value unused in Godot 4
                            continue
                        elif line.startswith("tile_set = ExtResource"):
                            res_id = int(line[len("tile_set = ExtResource("):line.rfind(")")])
                            tm.lines.append('tile_set = ExtResource("{0}")\n'.format(res_id))
                        elif line.startswith("format = 1"):
                            tm.lines.append('format = 2\n')
                        elif line.startswith("tile_data = PoolIntArray"):
                            if res_id != None:
                                tile_data_array = list(map(int,line[len("tile_data = PoolIntArray("):line.find(")")].split(",")))
                                tileset = id_to_tileset_dict[res_id]
                                tile_data = ", ".join(list(map(str,tileset.convert_gd3_to_gd4_tile_data(tile_data_array))))
                                tm.lines.append('layer_0/tile_data = PackedInt32Array( ' + tile_data + ')\n')
                        else:
                            tm.lines.append(line)
                else:
                    match_type = re.search(r'type=\"([\w\d]+)\"',line)
                    if match_type:
                        type_name = GD4Types.godot3_to_godot4_type_name(match_type.group(1))
                        match_everything_but_type = re.match(r'^(\[.*type=\")[\w\d]+(\".*$)',line)
                        if match_everything_but_type:
                            tm.lines.append(match_everything_but_type.group(1)+type_name+match_everything_but_type.group(2))
                    else:
                        tm.lines.append(line)
            else:
                tm.lines.append(line)
            index += 1
        return tm
