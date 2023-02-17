#!/usr/bin/env python
import os, sys

class TileSet:
    def __init__(self) -> None:
        pass

class TileMap:
    def __init__(self) -> None:
        pass

def parse_params():
    source_dir = ""
    target_dir = ""
    try:
        source_dir = sys.argv[1]
    except:
        "advisable to add source path as first start parameter, will work from current working directory now"

    if source_dir == "": source_dir = os.getcwd()
    try:
        target_dir = sys.argv[2]
        # if not os.path.exists(target_dir):
    except:
        "no target dir given"
    return source_dir, target_dir

def walk_path(root_dir):
    tres = []
    tscn = []
    for root, dirs, files in os.walk(root_dir,topdown=True):
        dirs[:] = [d for d in dirs if d not in [".git"]]
        for f in files:
            if f.strip().lower().endswith(".tres"):
                tres.append(os.path.join(root,f))
            elif f.strip().lower().endswith(".tscn"):
                tscn.append(os.path.join(root,f))
    if len(tres) + len(tscn) == 0: print("found no files to convert, check current working directory or source path parameter")
    return([tres,tscn])

if __name__ == "__main__":
    source,target = parse_params()
    
    tres,tscn = walk_path(source)
    for t in tres:
        with open(t,"r") as source:
            lines = source.readlines()
            if lines[0].find('type="TileSet"') == -1:
                print("Skipping {0}, seems not to be a valid TileSet file".format(source.name))
                continue
            elif lines[0].find('format=2') == -1:
                print("Skipping {0}, seems not to be a Godot 3 TileSet".format(source.name))
                continue
            print("processing")
