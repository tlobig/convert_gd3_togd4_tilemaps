import re
from parser_util import is_valid_target_version, is_valid_tile_map, is_valid_tile_set, header_line_to_dict, str_of_floats_to_list_of_floats
from collections.abc import Iterable
from UID_tools import UID

class TileSet:

    class Atlas:
        def __init__(self) -> None:
            self.name = ""
            self.gd3_atlas_dict = {}
            self.texture_region_size = [0,0]
            self.r_uid  = ""
            self.margin = [0,0]
            self.texture_id = None
            self.region = [0,0,0,0]
            self.tilemode = 0
            self.count_x = 1
            self.count_y = 1
            self.autotiles = {}

        def has(self,key : str) -> bool:
            return key in self.gd3_atlas_dict.keys()

        def get(self,key : str) -> bool:
            return self.gd3_atlas_dict[key] if self.has(key) else ""

    def __init__(self) -> None:
        self.ext_resources = []
        self.sub_resources = []
        self.load_steps = 0
        self.rel_path = ""
        self.atlasses = []
        self.colision_shapes = {}
        pass

    def prepare_sub_resources(self, tile_width, tile_height):
        for sub in self.sub_resources:
            if sub["type"] == '"ConvexPolygonShape2D"':
                points = sub["points"]
                # points are now based around the center
                points = [points[i] - (tile_width / 2.0 if i % 2 ==
                                       0 else tile_height / 2.0) for i in range(0, len(points))]
                self.colision_shapes[sub["id"]] = points

    def get_correct_type_name(name: str):
        if name == '"Texture"':
            name = '"Texture2D"'
        return name    

    def parse_godot3_tile_set(lines: Iterable[str]):
        tile_set = TileSet()
        rest_starts_at = 0
        # we wanna skip ahead during iteration, careful here
        for index in range(len(lines)):
            line = lines[index]

            if line.startswith("[ext_resource"):
                ext = header_line_to_dict(line)
                ext["type"] = TileSet.get_correct_type_name(ext["type"])
                tile_set.ext_resources.append(ext)

            elif line.startswith("[sub_resource"):
                sub = header_line_to_dict(line)
                if sub["type"] == '"ConvexPolygonShape2D"':
                    index += 1
                    line = lines[index]
                    sub["points"] = str_of_floats_to_list_of_floats(
                        line[line.find("(")+1:line.find(")")])
                tile_set.sub_resources.append(sub)

            elif line.startswith("[resource]"):
                # process the rest differently
                rest_starts_at = index+1
                break
        # second part, parsing tile atlasses
        atlas_id = 0
        atlas = TileSet.Atlas()
        for index in range(rest_starts_at, len(lines)):
            line = lines[index].strip()
            # match for an integer follow by a forward slash, i.e. 3/
            id_prefix = re.search(r"(\d+)/", line)
            if id_prefix:
                # id_prefix.groups()[0]
                if int(id_prefix.groups()[0]) != atlas_id:
                    # new atlas started
                    tile_set.atlasses.append(atlas)
                    (atlas.gd3_atlas_dict)
                    atlas = TileSet.Atlas()
                    atlas_id = int(id_prefix.groups()[0])
                if line.find("shapes = [ ") != -1:
                    # expecting a few lines that are not prefixed with the id !
                    # danger zone, manipulating the index again
                    # this will ignore the autotiling information, needs to be implemented later
                    autotile_info_string = [line.strip()]
                    while not re.search(r"(\d+)/", lines[index+1]):
                        autotile_info_string.append(lines[index+1].strip())
                        index += 1
                    
                else:
                    key, value = line[line.find("/")+1:].split("=")
                    atlas.gd3_atlas_dict[key.strip()] = value.strip()
        # add final atlas:
        tile_set.atlasses.append(atlas)
        return tile_set



    def is_godot3_tile_set(lines: Iterable[str]):
        return is_valid_tile_set(lines)

    def populate_data_fields(self):
        atlas: TileSet.Atlas
        for atlas in self.atlasses:
            atlas.r_uid = UID.generate_scene_unique_id()
            atlas.name = atlas.get("name") # name will just be empty if unused
            if atlas.has("texture"):
                texture_id = atlas.get("texture")
                texture_id = texture_id[texture_id.find("(")+1:texture_id.find(")")]
                atlas.texture_id = texture_id.strip()
            if atlas.has("tile_mode") and atlas.has("region"):
                atlas.tilemode = int(atlas.get("tile_mode"))
                atlas.region = list(map(int,re.findall(r"[\s\(,]{1}(\d+)",atlas.get("region"))))
                atlas.margin = [atlas.region[0],atlas.region[1]]
                if atlas.tilemode == 0: # single tile
                    atlas.texture_region_size = [atlas.region[2],atlas.region[3]]
                    atlas.count_x = 1
                    atlas.count_y = 1
                elif atlas.tilemode in [1,2] and atlas.has("autotile/tile_size"): # autotile or atlas
                    auto_tile_size = list(map(int,re.findall(r"[\s\(,]{1}(\d+)",atlas.get("autotile/tile_size"))))
                    atlas.texture_region_size = auto_tile_size
                    atlas.count_x = atlas.region[2] // atlas.texture_region_size[0]
                    atlas.count_y = atlas.region[3] // atlas.texture_region_size[1]
                
                
    def parse_tile_set(lines: Iterable[str]):
        ts = None
        if TileSet.is_godot3_tile_set(lines):
            ts = TileSet.parse_godot3_tile_set(lines)
            ts.populate_data_fields()
        return ts

    def get_lines_for_godot_4_tile_set(self):
        lines = []
        self.load_steps += len(self.ext_resources) + len(self.atlasses)
        lines.append(
            '[gd_resource type="TileSet" load_steps={0} format=3 uid="uid://{1}"]\n\n'.format(self.load_steps,UID.get_next_uid_as_text()))
        for ext in self.ext_resources:
            lines.append(
                '[ext_resource type={0} uid="uid://{3}" path={1} id={2}]\n\n'.format(ext["type"], ext["path"], ext["id"],UID.get_next_uid_as_text()))

        atlas: TileSet.Atlas
        for atlas in self.atlasses:
            lines.append('[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_{0}"]\n'.format(atlas.r_uid))
            lines.append('resource_name = {0}\n'.format(atlas.name))
            if atlas.texture_id != None:
                lines.append('texture = ExtResource("{0}")\n'.format(atlas.texture_id))
            if sum(atlas.margin) > 0:
                lines.append('margins = Vector2i({0}, {1})\n'.format(atlas.margin[0],atlas.margin[1]))
            lines.append('texture_region_size = Vector2i({0}, {1})\n'.format(atlas.texture_region_size[0],atlas.texture_region_size[1]))
            # lines.append('{0}\n'.format(1))
            for x_i in range(atlas.count_x):
                for y_i in range(atlas.count_y):
                    lines.append('{0}:{1}/0 = 0\n'.format(x_i,y_i))
            lines.append('\n')

        lines.append('[resource]\n')
        atlas_count = 0
        atlas: TileSet.Atlas
        for atlas in self.atlasses:
            lines.append('sources/{0} = SubResource("TileSetAtlasSource_{1}")\n'.format(atlas_count,atlas.r_uid))
            atlas_count += 1
        return lines