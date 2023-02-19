# unusable Godot 3 to Godot 4 TileSet/TileMap-converter

Warning, this thing is probably not for you. I just try to create a converter based on a sample from [https://github.com/GDQuest/godot-procedural-generation](https://github.com/GDQuest/godot-procedural-generation) in order to save some manual work. This thing is not done and I may abandon it.

The idea is to run the script gd_converter.py either in the project folder that should be ported or use source and target dirs as parameters. If you want to try it, make sure to have a back. The target directory may overwrite files. Can't repeat this enough, this is not production code. No liabilities whatsoever.

- Thomas

progress:

- most of the parsing of a tileset is implemented, known as missing:
  - autotile bitmask reading
  - texture offset (now called texture origin)
  - additional physics info on collision shapes, also shape transform
  
- writing tilesets:
  - figured out most of the uuid stuff, leaving it out for external resources since it's likely not gonna be correct anyway and Godot falls back on the path then
  - tilesets are already quite usable
  - autotiling information is still not preserved, but terrains are being prepared
  - collision shapes are preserved, but most additional physics information is ignored, shape transform also
