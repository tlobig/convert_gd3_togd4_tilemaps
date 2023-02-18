#!/usr/bin/env python3
import os
import sys
import re

from collections.abc import Iterable

from UID_tools import UID

class TileSet:

    class Atlas:
        def __init__(self) -> None:
            self.name = ""
            self.gd3_atlas_dict = {}
            self.texture_region_size = [0,0]

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


class TileMap:
    def __init__(self) -> None:
        pass


def get_source_and_target_from_params():
    source_dir = ""
    target_dir = ""
    try:
        source_dir = sys.argv[1]
    except:
        print("\nhint: it is advisable to add source path as first start parameter, will work from current working directory now")

    if source_dir == "":
        source_dir = os.getcwd()

    try:
        target_dir = sys.argv[2]
        # if not os.path.exists(target_dir):
    except:
        print("\nhint: no target dir given, will add '_godot4' to source dir and use this for output")

    if target_dir == "":
        target_dir = os.path.join(source_dir + "_godot4")

    print("\n> will parse files in {0}".format(source_dir))
    print("> will write files to {0}".format(target_dir))

    return source_dir, target_dir


def is_valid_target_version(lines: Iterable[str]):
    if lines[0].find('format=2') == -1:
        print("Skipping {0}, seems not to be a Godot 3 file".format(
            source.name))
        return False
    else:
        return True


def is_valid_tile_set(lines: Iterable[str]):
    if lines[0].find('type="TileSet"') == -1:
        print("Skipping {0}, seems not to be a valid TileSet file".format(
            source.name))
        return False
    return is_valid_target_version(lines)


def is_valid_tile_map(lines: Iterable[str]):
    any_map = False
    for line in lines:
        if line.find('type="TileMap"') != -1:
            any_map = True
            break
    if not any_map:
        print("Skipping {0}, seems not to be a valid TileMap file".format(
            source.name))
        return False
    return is_valid_target_version(lines)


def walk_path(root_dir: str):
    tres = []
    tscn = []
    for root, dirs, files in os.walk(root_dir, topdown=True):
        dirs[:] = [d for d in dirs if d not in [".git"]]
        for f in files:
            if f.strip().lower().endswith(".tres"):
                tres.append(os.path.join(root, f))
            elif f.strip().lower().endswith(".tscn"):
                tscn.append(os.path.join(root, f))
    if len(tres) + len(tscn) == 0:
        print("found no files to convert, check current working directory or source path parameter")
    return ([tres, tscn])


def header_line_to_dict(line: str):
    # a dictionary comprehension to disentangle key="value" lines into a dictionary
    line = line.strip()
    return {l.split("=")[0]: l.split("=")[1] for l in line[line.find(" "):-1].split()}


def get_correct_type_name(name: str):
    if name == '"Texture"':
        name = '"Texture2D"'
    return name


def str_of_floats_to_list_of_floats(line: str):
    return [float(s) for s in line.split(",")]


def parse_godot3_tile_set(lines: Iterable[str]):
    tile_set = TileSet()
    rest_starts_at = 0
    # we wanna skip ahead during iteration, careful here
    for index in range(len(lines)):
        line = lines[index]

        if line.startswith("[ext_resource"):
            ext = header_line_to_dict(line)
            ext["type"] = get_correct_type_name(ext["type"])
            tile_set.ext_resources.append(ext)

        elif line.startswith("[sub_resource"):
            sub = header_line_to_dict(line)
            if sub["type"] == '"ConvexPolygonShape2D"':
                index += 1
                line = lines[index]
                sub["points"] = str_of_floats_to_list_of_floats(
                    line[line.find("(")+1:line.find(")")])
            print(sub)
            tile_set.sub_resources.append(sub)

        elif line.startswith("[resource]"):
            # process the rest differently
            rest_starts_at = index+1
            break
    # second part, parsing tile atlasses
    # cannot do this here, no indication of 'cell size' without a tilemap - tile_set.prepare_sub_resources(?,?)
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
                print(atlas.gd3_atlas_dict)
                atlas = TileSet.Atlas()
                atlas_id = int(id_prefix.groups()[0])
            if line.find("shapes = [ {") != -1:
                # expecting a few lines that are not prefixed with the id !
                # danger zone, manipulating the index again
                # this will ignore the autotiling information, needs to be implemented later
                index += 1
                while not re.search(r"(\d+)/", lines[index+1]):
                    index += 1
            else:
                key, value = line[line.find("/")+1:].split("=")
                atlas.gd3_atlas_dict[key.strip()] = value.strip()
    # add final atlas:
    tile_set.atlasses.append(atlas)
    print(tile_set.atlasses)
    return tile_set


def parse_godot3_tile_map(lines: Iterable[str]):
    tile_map = TileMap()
    return tile_map


def tileset_to_godot_4_tileset(ts: TileSet):
    lines = []
    ts.load_steps += len(ts.ext_resources) + len(ts.atlasses)
    lines.append(
        '[gd_resource type="TileSet" load_steps={0} format=3 uid="uid://{1}"]\n\n'.format(ts.load_steps,UID.get_next_uid_as_text()))
    for ext in ts.ext_resources:
        lines.append(
            '[ext_resource type={0} uid="uid://{3}" path={1} id={2}]\n\n'.format(ext["type"], ext["path"], ext["id"],UID.get_next_uid_as_text()))

    atlas: TileSet.Atlas
    for atlas in ts.atlasses:
        pass
        lines.append('[sub_resource type="TileSetAtlasSource" id="TileSetAtlasSource_{0}"]\n'.format(UID.generate_scene_unique_id()))
        lines.append('resource_name = {0}\n'.format(atlas.get("name"))) # name will just be empty if unused
        if atlas.has("texture"):
            texture_id = atlas.get("texture")
            texture_id = texture_id[texture_id.find("(")+1:texture_id.find(")")]
            lines.append('texture = ExtResource("{0}")\n'.format(texture_id))
        lines.append('texture_region_size = Vector2i({0}, {1})\n'.format(atlas.texture_region_size[0],atlas.texture_region_size[1]))
        # lines.append('{0}\n'.format(1))
        lines.append('\n')
    return lines


if __name__ == "__main__":
    UID.init()
    source_dir, target_dir = get_source_and_target_from_params()

    tres, tscn = walk_path(source_dir)
    tilesets, tilemaps = [], []

    print("\nparsing TileSets")
    for t in tres:
        with open(t, "r") as source:
            lines = source.readlines()
            if not is_valid_tile_set(lines):
                continue
            ts = parse_godot3_tile_set(lines)
            ts.rel_path = os.path.relpath(t, source_dir)
            tilesets.append(ts)

    print("\nparsing TileMaps")
    for t in tscn:
        with open(t, "r") as source:
            lines = source.readlines()
            if not is_valid_tile_map(lines):
                continue
            tilemaps.append(parse_godot3_tile_map(lines))

    print("\nparsing TileSets")
    os.makedirs(target_dir, exist_ok=True)
    for ts in tilesets:
        lines = tileset_to_godot_4_tileset(ts)
        target_file_name = os.path.join(target_dir, ts.rel_path)
        os.makedirs(os.path.dirname(target_file_name), exist_ok=True)
        with open(target_file_name, mode="w",) as o:
            print("- writing: " + target_file_name)
            o.writelines(lines)
