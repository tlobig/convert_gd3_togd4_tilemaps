from collections.abc import Iterable

def is_valid_target_version(lines: Iterable[str]):
    if lines[0].find('format=2') == -1:
        return False
    else:
        return True

def is_valid_tile_set(lines: Iterable[str]):
    if lines[0].find('type="TileSet"') == -1:
        return False
    return is_valid_target_version(lines)


def is_valid_tile_map(lines: Iterable[str]):
    any_map = False
    for line in lines:
        if line.find('type="TileMap"') != -1:
            any_map = True
            break
    if not any_map:
        # print("Skipping {0}, seems not to be a valid TileMap file".format(
        #     source.name))
        return False
    return is_valid_target_version(lines)

def header_line_to_dict(line: str):
    # a dictionary comprehension to disentangle key="value" lines into a dictionary
    line = line.strip()
    return {l.split("=")[0]: l.split("=")[1] for l in line[line.find(" "):-1].split()}

def str_of_floats_to_list_of_floats(line: str):
    return list(map(float,line.split(",")))
    # return [float(s) for s in line.split(",")]        