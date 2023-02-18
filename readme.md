# unusable Godot 3 to Godot 4 TileSet/TileMap-converter

Warning, this thing is probably not for you. I just try to create a converter based on a sample from [https://github.com/GDQuest/godot-procedural-generation](https://github.com/GDQuest/godot-procedural-generation) in order to save some manual work. This thing is not done and I may abandon it.

The idea is to run the script gd_converter.py either in the project folder that should be ported or use source and target dirs as parameters. If you want to try it, make sure to have a back. The target directory may overwrite files. Can't repeat this enough, this is not production code. No liabilities whatsoever.

- Thomas

progress:

- so far only the rudimentary parsing of a tileset is implemented, known as missing:
  - autotile bitmask reading
  - texture_region_size is a property of tileset now and used to be a cell_size, a property of tilemap, can't know it without parsing tilemaps
- writing tilesets:
  - figured out most of the uuid stuff, this project already sees refactoring to have it clean enough.
  - basic tilesets work now, autotiling and collision shapes are missing
