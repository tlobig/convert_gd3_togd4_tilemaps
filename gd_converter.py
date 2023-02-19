#!/usr/bin/env python3
import os
import sys
import re

from UID_tools import UID

from tile_set import TileSet
from tile_map import SceneWithTileMap



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


# def parse_godot3_tile_map(lines: Iterable[str]):
#     tile_map = TileMap()
#     return tile_map





if __name__ == "__main__":
    UID.init()
    source_dir, target_dir = get_source_and_target_from_params()

    tres, tscn = walk_path(source_dir)
    tilesets, tilemaps = {}, []

    print("\nparsing TileSets")
    for t in tres:
        with open(t, "r") as source:
            lines = source.readlines()
            ts = TileSet.parse_tile_set(lines)
            if ts != None:
                ts.rel_path = os.path.relpath(t, source_dir)
                # tilesets.append(ts)
                tilesets["res://"+ts.rel_path.replace("\\","/")] = ts
            else:
                print("Skipping {0}, seems not to be a valid source TileSet".format(source.name))

    print("\nparsing TileMaps")
    for t in tscn:
        with open(t, "r") as source:
            lines = source.readlines()
            tm = SceneWithTileMap.parse_tile_map(lines,tilesets)
            if tm != None:
                tm.rel_path = os.path.relpath(t, source_dir)
                tilemaps.append(tm)
            else:
                print("Skipping {0}, seems not to be a valid Godot 3 Scene with a TileMap".format(source.name))

    print("\nwriting TileSets")
    os.makedirs(target_dir, exist_ok=True)
    for ts in tilesets.values():
        lines = ts.get_lines_for_godot_4_tile_set()
        target_file_name = os.path.join(target_dir, ts.rel_path)
        os.makedirs(os.path.dirname(target_file_name), exist_ok=True)
        with open(target_file_name, mode="w",) as o:
            print("- writing: " + target_file_name)
            o.writelines(lines)

    print("\nwriting Scenes with TileMaps")
    for tm in tilemaps:
        lines = tm.lines
        target_file_name = os.path.join(target_dir, tm.rel_path)
        os.makedirs(os.path.dirname(target_file_name), exist_ok=True)
        with open(target_file_name, mode="w",) as o:
            print("- writing: " + target_file_name)
            o.writelines(lines)
