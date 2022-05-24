import context
import math
from typing import Any, List
import os
import hashlib
from pathlib import Path

from zquest.extract import ZeldaClassicReader
from zquest.constants import combo_type_names

dir = os.path.dirname(__file__)
qst_path = os.path.join(dir, '../test_data/1st.qst')
reader = ZeldaClassicReader(qst_path)
reader.read_qst()

# Number of tiles in a screen
screen_width = 16
screen_height = 11

# Number of pixels in a screen
pos_width = screen_width * 16
pos_height = screen_height * 16

# Number of screens in a map
map_width = 16
map_height = 8

USE_SCREEN_83 = True
combos_to_not_modify = set()


def swap_bits(val, i, j):
    """
    Given an integer val, swap bits in positions i and j if they differ
    by flipping their values, i.e, select the bits to flip with a mask.
    Since v ^ 1 = 0 when v = 1 and 1 when v = 0, perform the flip using an XOR.
    """
    if not (val >> i) & 1 == (val >> j) & 1:
        mask = (1 << i) | (1 << j)
        val ^= mask
    return val


def to_index(x: int, y: int, w: int) -> int:
    return x + y * w


def to_xy(index: int, w: int) -> int:
    x = index % w
    y = math.floor(index / w)
    return x, y


def mirror_screen(y: int) -> int:
    return screen_height - y - 1


def mirror_screen_arr(arr: List[int]) -> List[int]:
    new_arr = []
    for index in arr:
        x, y = to_xy(index, screen_width)
        new_arr.append(to_index(x, screen_height - y - 1, screen_width))
    return new_arr


def mirror_posy(y: int) -> int:
    return pos_height - y - 16


def mirror_posy_arr(arr: List[int]) -> List[int]:
    new_arr = []
    for y in arr:
        new_arr.append(pos_height - y - 16)
    return new_arr


def mirror_1d(arr: List[int], w: int, h: int) -> List[int]:
    new_arr = []
    for index in arr:
        x, y = to_xy(index, screen_width)
        new_arr.append(to_index(x, h - y - 1, w))
    return new_arr


def mirror_2d(arr: List[Any], w: int, h: int) -> List[Any]:
    new_arr = arr.copy()
    for x in range(w):
        for y in range(h):
            new_arr[to_index(x, y, w)] = arr[to_index(x, h - y - 1, w)]
    return new_arr


def mirror_directional_array(arr: List[Any]) -> List[Any]:
    # up, down, left, right
    assert len(arr) == 4
    return [
        arr[mirror_direction(0)],
        arr[mirror_direction(1)],
        arr[mirror_direction(2)],
        arr[mirror_direction(3)],
    ]


def mirror_direction(val: int) -> int:
    # up, down, left, right
    if val == 0:
        return 1
    elif val == 1:
        return 0
    else:
        return val


def is_null_combo(index: int):
    if index >= len(reader.combos):
        return True

    tile = reader.combos[index].tile
    if tile == 0:
        return True

    if all(p == 0 for p in reader.tiles[tile].pixels):
        return True

    return False


for zc_map in reader.maps:
    # Screen 0x83 is the NES dungeon template screen, so let's use it
    # to mirror matching screen combos.
    tile_mappings = {}

    if USE_SCREEN_83:
        screen_83 = zc_map.screens[0x83]
        for x in range(screen_width):
            for y in range(screen_height):
                index_1 = to_index(x, y, screen_width)
                index_2 = to_index(x, screen_height - y - 1, screen_width)
                if is_null_combo(screen_83.data[index_1]) or is_null_combo(screen_83.data[index_2]):
                    continue

                tile_mappings[screen_83.data[index_1]] = screen_83.data[index_2]
                combos_to_not_modify.add(screen_83.data[index_1])

    zc_map.screens = mirror_2d(zc_map.screens, map_width, map_height)

    # Don't flip the 0x80 screens.
    for screen in zc_map.screens[0:map_width * map_height]:
        original_data = screen.data.copy()
        for x in range(screen_width):
            for y in range(screen_height):
                index = to_index(x, y, screen_width)
                to_value = tile_mappings.get(original_data[index])
                if to_value != None:
                    screen.data[index] = to_value

        screen.data = mirror_2d(screen.data, screen_width, screen_height)
        screen.cset = mirror_2d(screen.cset, screen_width, screen_height)
        screen.sflag = mirror_2d(screen.sflag, screen_width, screen_height)

        # swap up and down
        screen.flags2 = swap_bits(screen.flags2, 0, 1)
        # TODO: mirror side_warp_index
        if screen.side_warp_index != 0:
            raise Exception('Only quests that use just A warps can be mirrored')

        screen.side_warp_screen = mirror_1d(screen.side_warp_screen, map_width, map_height)
        screen.tile_warp_screen = mirror_1d(screen.tile_warp_screen, map_width, map_height)

        # top-left warp return squares have a special meaning for the test mode position
        # selection–and is 99.99% not really being used. So don't touch it in that case.
        if any(screen.warp_return_y):
            screen.warp_return_y = mirror_posy_arr(screen.warp_return_y)
        screen.item_y = mirror_posy(screen.item_y)
        screen.stair_y = mirror_posy(screen.stair_y)
        screen.warp_arrival_y = mirror_posy(screen.warp_arrival_y)
        if hasattr(screen, 'newitem_y'):
            screen.newitem_y = mirror_posy_arr(screen.newitem_y)

        screen.doors = mirror_directional_array(screen.doors)
        screen.path = list(map(mirror_direction, screen.path))
        screen.exit_dir = mirror_direction(screen.exit_dir)

        if screen.next_screen:
            screen.next_screen = mirror_screen(screen.next_screen)

        if hasattr(screen, 'ff'):
            for ff in screen.ff:
                if ff:
                    ff.y = mirror_posy(ff.y)

for i, combo in enumerate(reader.combos):
    if i in combos_to_not_modify:
        continue

    hor = combo.flip & 1 != 0
    ver = combo.flip & 2 != 0
    ver = not ver
    combo.flip = hor + (ver << 1)

    # top-left, bottom-left, top-right, bottom-right
    walk = [
        combo.walk & 1 != 0,
        combo.walk & 2 != 0,
        combo.walk & 4 != 0,
        combo.walk & 8 != 0,
    ]

    # Combos that are only walkable on the top half look very strange when
    # made to be only walkable on the bottom half... so ignore those.
    if walk[0] and walk[2] and not walk[1] and not walk[3]:
        pass
    else:
        walk = [walk[1], walk[0], walk[3], walk[2]]
        combo.walk = walk[0] + (walk[1] << 1) + (walk[2] << 2) + (walk[3] << 3)

    # Can't trigger these warps on the top half... so make it 100% walkable.
    type_name = combo_type_names[combo.type]
    if 'Cave' in type_name:
        combo.walk = 0

    # TODO: swap combo types like Conveyor Up <-> Conveyor Down

out_path = os.path.join(dir, '../output/1st-mirrored.qst')
reader.save_qst(out_path)

hash = hashlib.md5(Path(out_path).read_bytes()).hexdigest()
if hash != 'da49655ba43d28cdafebfb390319b1e4':
    raise Exception(f'hash has changed to {hash}')
