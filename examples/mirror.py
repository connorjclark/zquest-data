import sys

if 'unittest' in sys.modules.keys():
    from src.zquest.extract import ZeldaClassicReader
    from src.zquest.constants import combo_type_names
else:
    import context
    from zquest.extract import ZeldaClassicReader
    from zquest.constants import combo_type_names

import math
from typing import Any, List, Tuple


# Number of tiles in a screen
screen_width = 16
screen_height = 11

# Number of pixels in a screen
pos_width = screen_width * 16
pos_height = screen_height * 16

# Number of screens in a map
map_width = 16
map_height = 8


def mirror_xy_vertical(x: int, y: int, w: int, h: int) -> Tuple[int, int]:
    return x, h - y


def mirror_xy_horizontal(x: int, y: int, w: int, h: int) -> Tuple[int, int]:
    return w - x, y


def mirror_xy_both(x: int, y: int, w: int, h: int) -> Tuple[int, int]:
    return w - x, h - y


def set_mirror_mode(mode: str):
    global mirror_mode, mirror_xy, is_horizontal_mirror, is_vertical_mirror
    global directions, directions_mirrored, walkable_flags, walkable_flags_mirrored

    mirror_mode = mode
    is_horizontal_mirror = mirror_mode == 'horizontal' or mirror_mode == 'both'
    is_vertical_mirror = mirror_mode == 'vertical' or mirror_mode == 'both'

    match mirror_mode:
        case 'vertical': mirror_xy = mirror_xy_vertical
        case 'horizontal': mirror_xy = mirror_xy_horizontal
        case 'both': mirror_xy = mirror_xy_both

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
    if is_vertical_mirror and arr[0] and arr[2] and not arr[1] and not arr[3]:
        return flags

    arr = [
        arr[walkable_flags.index(walkable_flags_mirrored[0])],
        arr[walkable_flags.index(walkable_flags_mirrored[1])],
        arr[walkable_flags.index(walkable_flags_mirrored[2])],
        arr[walkable_flags.index(walkable_flags_mirrored[3])],
    ]
    return arr[0] + (arr[1] << 1) + (arr[2] << 2) + (arr[3] << 3)


def mirror_screen(index: int) -> int:
    x, y = mirror_xy(*to_xy(index, screen_width), map_width - 1, map_height - 1)
    return to_index(x, y, map_width)


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


def mirror_qst(mirror_mode: str, in_path: str, out_path: str):
    reader = ZeldaClassicReader(in_path)
    reader.read_qst()
    set_mirror_mode(mirror_mode)

    for zc_map in reader.maps:
        zc_map.screens = mirror_2d(zc_map.screens, map_width, map_height)

        # Don't flip the 0x80 screens.
        for screen in zc_map.screens[0:map_width * map_height]:
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
                screen.newitem_x, screen.newitem_y = mirror_pos_arr(
                    screen.newitem_x, screen.newitem_y)

            screen.doors = mirror_directional_array(screen.doors)
            screen.path = list(map(mirror_direction, screen.path))
            screen.exit_dir = mirror_direction(screen.exit_dir)

            if hasattr(screen, 'next_screen'):
                screen.next_screen = mirror_screen(screen.next_screen)

            if hasattr(screen, 'layer_screen'):
                screen.layer_screen = [0 if scr == 0 else mirror_screen(
                    scr) for scr in screen.layer_screen]

            if hasattr(screen, 'ff'):
                for ff in screen.ff:
                    if ff:
                        ff.x, ff.y = mirror_pos(ff.x, ff.y)

    for i, combo in enumerate(reader.combos):
        hor = combo.flip & 1 != 0
        ver = combo.flip & 2 != 0
        hor, ver = mirror_xy(hor, ver, 1, 1)
        combo.flip = hor + (ver << 1)

        combo.walk = mirror_walkable_flags(combo.walk)

        if is_vertical_mirror:
            # Can't trigger these warps on the top half... so make it 100% walkable.
            type_name = combo_type_names[combo.type]
            if 'Cave' in type_name:
                combo.walk = 0

        # TODO: swap combo types like Conveyor Up <-> Conveyor Down

    for door_set in reader.doors:
        for door, offset, sw, sh in iterate_door_set(door_set):
            mirror_doorset_grid(door, offset, sw, sh)

        if is_vertical_mirror:
            door_set.up, door_set.down = door_set.down, door_set.up
        if is_horizontal_mirror:
            door_set.left, door_set.right = door_set.right, door_set.left

    reader.save_qst(out_path)


def mirror_doorset_grid(door, door_offset, sw, sh):
    original_combos = door.combos.copy()
    for sx in range(sw):
        for sy in range(sh):
            door_index_1 = door_offset + to_index(sx, sy, sw)
            door_index_2 = door_offset + to_index(*mirror_xy(sx, sy, sw - 1, sh - 1), sw)
            door.combos[door_index_1] = original_combos[door_index_2]


def iterate_door_set(door_set):
    for i in range(9):
        sw = 2
        sh = 2
        offset = i * sw * sh
        yield door_set.up, offset, sw, sh
        yield door_set.down, offset, sw, sh

        sw = 2
        sh = 3
        offset = i * sw * sh
        yield door_set.left, offset, sw, sh
        yield door_set.right, offset, sw, sh


if __name__ == '__main__':
    mirror_qst(*sys.argv[1:4])
