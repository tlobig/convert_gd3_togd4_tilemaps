
class GD4Types:
    def godot3_to_godot4_type_name(name:str) -> str:
        type_name_dict = {
            "Texture" : "Texture2D",
            "Sprite" : "Sprite2D"
        }
        if name in type_name_dict:
            return type_name_dict[name]
        else:
            return name