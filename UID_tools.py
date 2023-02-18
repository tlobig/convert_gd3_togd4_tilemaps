import random
from ctypes import c_uint32
import datetime

class UID:
    # reimplementing parts of the UID system from Godot 4
    def init() -> None:
        UID.re_roll()
        UID.scene_unique_ids = set([""])

    def re_roll():
        UID.uid = random.getrandbits(16*8)
        UID.uid = UID.uid & 0x7FFFFFFFFFFFFFFF
        # UID.next_source_id = (UID.uid + (1)) % 1073741824

    def get_next_uid_as_text() -> str:
        UID.re_roll()  # this is not checking for collisions, but since we don't know of 
        # ANY resources other than the tilemaps and tilesets there is not way to guarantee no collisions happening
        return UID.uid_to_text(UID.uid)

    # def get_next_subid_as_text() -> str:
    #     # UID.next_source_id = (UID.next_source_id + 1) % 1073741824 # TODO this seems not the right way
    #     UID.re_roll()
    #     return UID.uid_to_text(UID.next_source_id)

    def uid_to_text(id: int) -> str:
        char_count: int = ord('z') - ord('a')
        base: int = char_count + (ord('9') - ord('0'))
        print(char_count, base)
        uid_txt = ""
        while id > 0:
            c = int(id % base)
            if c < char_count:
                uid_txt = chr(ord('a') + c) + uid_txt
            else:
                uid_txt = chr(ord('0') + (c - char_count)) + uid_txt
            id = int(id / base)
        return uid_txt

    def has_scene_unique_id(id:str) -> bool:
        return id in UID.scene_unique_ids

    def generate_scene_unique_id() -> str:
        while True:
            id = ""
            now = datetime.datetime.now()
            hash = UID.hash_murmur3_one_32(now.microsecond)
            hash = UID.hash_murmur3_one_32(now.year, hash)
            hash = UID.hash_murmur3_one_32(now.month, hash)
            hash = UID.hash_murmur3_one_32(now.day, hash)
            hash = UID.hash_murmur3_one_32(now.hour, hash)
            hash = UID.hash_murmur3_one_32(now.minute, hash)
            hash = UID.hash_murmur3_one_32(now.second, hash)
            hash = UID.hash_murmur3_one_32(random.getrandbits(32), hash)

            hash = int(hash)
            characters = 5
            char_count = ord('z') - ord('a')
            base = char_count + (ord('9') - ord('0'))
            for i in range(characters):
                c = hash % base
                if c < char_count:
                    id += chr(ord('a') + c)
                else:
                    id += chr(ord('0') + (c - char_count))
                hash = hash // base
            if not UID.has_scene_unique_id(id):
                break
        UID.scene_unique_ids.add(id)
        return id

    # HASH_MURMUR3_SEED 0x7F07C65
    def hash_murmur3_one_32(p_in: c_uint32, p_seed: c_uint32 = 0x7F07C65) -> c_uint32:
        p_in *= 0xcc9e2d51
        p_in = (p_in << 15) | (p_in >> 17)
        p_in *= 0x1b873593
        
        p_seed ^= p_in
        p_seed = (p_seed << 13) | (p_seed >> 19)
        p_seed = p_seed * 5 + 0xe6546b64
        
        return p_seed