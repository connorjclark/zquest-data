import context
import math
from typing import Any, List, Tuple
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

# TODO https://hoten.cc/zc/create/?quest=local/1st-mirrored.qst&map=2&screen=125


def mirror_xy_vertical(x: int, y: int, w: int, h: int) -> Tuple[int, int]:
    return x, h - y


def mirror_xy_horizontal(x: int, y: int, w: int, h: int) -> Tuple[int, int]:
    return w - x, y


def mirror_xy_both(x: int, y: int, w: int, h: int) -> Tuple[int, int]:
    return w - x, h - y


mirror_mode = 'vertical'
match mirror_mode:
    case 'vertical': mirror_xy = mirror_xy_vertical
    case 'horizontal': mirror_xy = mirror_xy_horizontal
    case 'both': mirror_xy = mirror_xy_both


def is_vertical_mirror():
    return mirror_mode == 'vertical' or mirror_mode == 'both'


# up, down, left, right
directions = [
    (0, 1),
    (0, -1),
    (-1, 0),
    (1, 0),
]
directions_mirrored = [mirror_xy(x, y, 0, 0) for x, y in directions]
assert len(set(directions_mirrored)) == 4

# top-left, bottom-left, top-right, bottom-right
walkable_flags = [
    (-1, 1),
    (-1, -1),
    (1, 1),
    (1, -1),
]
walkable_flags_mirrored = [mirror_xy(x, y, 0, 0) for x, y in walkable_flags]
assert len(set(walkable_flags_mirrored)) == 4


def set_bit(val: int, index: int, x: int) -> int:
    mask = 1 << index
    val &= ~mask
    if x:
        val |= mask
    return val


def to_index(x: int, y: int, w: int) -> int:
    return x + y * w


def to_xy(index: int, w: int) -> int:
    x = index % w
    y = math.floor(index / w)
    return x, y


def mirror_direction(dir: int) -> int:
    # damn python is cool
    return directions.index(directions_mirrored[dir])


def mirror_directional_array(arr: List[Any]) -> List[Any]:
    assert len(arr) == 4
    return [
        arr[mirror_direction(0)],
        arr[mirror_direction(1)],
        arr[mirror_direction(2)],
        arr[mirror_direction(3)],
    ]


def mirror_walkable_flags(flags: int) -> int:
    arr = [
        flags & 1 != 0,
        flags & 2 != 0,
        flags & 4 != 0,
        flags & 8 != 0,
    ]

    # Combos that are only walkable on the top half look very strange when
    # made to be only walkable on the bottom half... so ignore those.
    if is_vertical_mirror() and arr[0] and arr[2] and not arr[1] and not arr[3]:
        return flags

    arr = [
        arr[walkable_flags.index(walkable_flags_mirrored[0])],
        arr[walkable_flags.index(walkable_flags_mirrored[1])],
        arr[walkable_flags.index(walkable_flags_mirrored[2])],
        arr[walkable_flags.index(walkable_flags_mirrored[3])],
    ]
    return arr[0] + (arr[1] << 1) + (arr[2] << 2) + (arr[3] << 3)


def mirror_screen(index: int) -> int:
    x, y = mirror_xy(*to_xy(index, screen_width), screen_width - 1, screen_height - 1)
    return to_index(x, y, screen_width)


def mirror_screen_arr(arr: List[int]) -> List[int]:
    return [mirror_screen(index) for index in arr]


def mirror_pos(x: int, y: int) -> Tuple[int, int]:
    return mirror_xy(x, y, pos_width - 16, pos_height - 16)


def mirror_pos_arr(x_arr: List[int], y_arr: List[int]) -> Tuple[List[int], List[int]]:
    new_x_arr = []
    new_y_arr = []
    for x, y in zip(x_arr, y_arr):
        x, y = mirror_pos(x, y)
        new_x_arr.append(x)
        new_y_arr.append(y)
    return new_x_arr, new_y_arr


def mirror_1d(arr: List[int], w: int, h: int) -> List[int]:
    new_arr = []
    for index in arr:
        x, y = mirror_xy(*to_xy(index, w), w - 1, h - 1)
        new_arr.append(to_index(x, y, w))
    return new_arr


def mirror_2d(arr: List[Any], w: int, h: int) -> List[Any]:
    new_arr = arr.copy()
    for x in range(w):
        for y in range(h):
            new_x, new_y = mirror_xy(x, y, w - 1, h - 1)
            new_arr[to_index(x, y, w)] = arr[to_index(new_x, new_y, w)]
    return new_arr


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
                new_x, new_y = mirror_xy(x, y, screen_width - 1, screen_height - 1)
                index_1 = to_index(x, y, screen_width)
                index_2 = to_index(new_x, new_y, screen_width)
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

        udlr_flags = mirror_directional_array([
            screen.flags2 & 1 != 0,
            screen.flags2 & 2 != 0,
            screen.flags2 & 4 != 0,
            screen.flags2 & 8 != 0,
        ])
        flags2 = screen.flags2
        for i, x in enumerate(udlr_flags):
            flags2 = set_bit(flags2, i, x)
        screen.flags2 = flags2

        # TODO: mirror side_warp_index
        if screen.side_warp_index != 0:
            raise Exception('Only quests that use just A warps can be mirrored')

        screen.side_warp_screen = mirror_1d(screen.side_warp_screen, map_width, map_height)
        screen.tile_warp_screen = mirror_1d(screen.tile_warp_screen, map_width, map_height)

        # top-left warp return squares have a special meaning for the test mode position
        # selection–and is 99.99% not really being used. So don't touch it in that case.
        if any(screen.warp_return_x) or any(screen.warp_return_y):
            screen.warp_return_x, screen.warp_return_y = mirror_pos_arr(
                screen.warp_return_x, screen.warp_return_y)

        screen.item_x, screen.item_y = mirror_pos(screen.item_x, screen.item_y)
        screen.stair_x, screen.stair_y = mirror_pos(screen.stair_x, screen.stair_y)
        screen.warp_arrival_x, screen.warp_arrival_y = mirror_pos(
            screen.warp_arrival_x, screen.warp_arrival_y)
        if hasattr(screen, 'newitem_y'):
            screen.newitem_x, screen.newitem_y = mirror_pos_arr(screen.newitem_x, screen.newitem_y)

        screen.doors = mirror_directional_array(screen.doors)
        screen.path = list(map(mirror_direction, screen.path))
        screen.exit_dir = mirror_direction(screen.exit_dir)

        if screen.next_screen:
            screen.next_screen = mirror_screen(screen.next_screen)

        if hasattr(screen, 'ff'):
            for ff in screen.ff:
                if ff:
                    ff.x, ff.y = mirror_pos(ff.x, ff.y)

for i, combo in enumerate(reader.combos):
    if i in combos_to_not_modify:
        continue

    hor = combo.flip & 1 != 0
    ver = combo.flip & 2 != 0
    hor, ver = mirror_xy(hor, ver, 1, 1)
    combo.flip = hor + (ver << 1)

    combo.walk = mirror_walkable_flags(combo.walk)

    if is_vertical_mirror():
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
