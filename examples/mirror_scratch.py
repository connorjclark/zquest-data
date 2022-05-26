# Not 100% sure if dmap xoff/cont stuff can be ignored

def as_str(raw: bytes):
    if raw.find(b'\x00') != -1:
        return raw[0:raw.index(b'\x00')].decode('utf-8', errors='ignore').strip()
    else:
        return raw.decode('utf-8', errors='ignore').strip()


for dmap in reader.dmaps:
    if as_str(dmap.name) == '' and as_str(dmap.title) == '':
        continue

    def dmap_to_xy(val):
        val += dmap.xoff
        x = val % map_width
        y = math.floor(val / map_width)
        return x, y

    def dmap_to_index(x, y):
        index = x + y * map_width
        return index - dmap.xoff

    # xoff = dmap.xoff
    # x, y = dmap_to_xy(dmap.cont)
    # if x != 0:
    #     print(x,y, dmap.cont)
    #     y = map_height - y - 1
    #     print(x,y, dmap_to_index(x, y))
    # dmap.cont = dmap_to_index(x, y)

    # print(dmap.xoff)
    # x, y = to_xy(dmap.xoff, map_width)
    # y = map_height - y - 1
    # print('original', dmap.xoff, to_xy(dmap.xoff, map_width))
    # dmap.xoff = to_index(x, y, map_width)
    # print(dmap.xoff, to_xy(dmap.xoff, map_width))

    # dmap.xoff


# The following was the first attempt of trying to flip door combo sets.
# A simpler approach was found, by using the template screen 0x83 to
# create a combo mapping for mirroring.
# But, just in case in the future I want to mirror non-1st quests,
# keep this code in limbo, because it could be that custom quests
# don't bother to setup a dungeon template room (also, this is only
# valid for NES dungeons).
# Note: this isn't 100% working yet.

# ......
def subgrid_matches(door, door_offset, x, y, sw, sh):
    for sx in range(sw):
        for sy in range(sh):
            index = to_index(x + sx, y + sy, screen_width)
            if original_data[index] != door.combos[door_offset + sx + sy * sw]:
                return False
    return True


def find_matching_subgrids(door, door_offset, sw, sh):
    for x in range(screen_width - (sw - 1)):
        for y in range(screen_height - (sh - 1)):
            if subgrid_matches(door, door_offset, x, y, sw, sh):
                yield x, y


def mirror_matching_subgrids(screen, door, door_offset, sw, sh):
    for x, y in find_matching_subgrids(door, door_offset, sw, sh):
        for sx in range(sw):
            for sy in range(sh):
                screen_index = to_index(x + sx, y + sy, screen_width)
                door_index = to_index(*mirror_xy(sx, sy, sw - 1, sh - 1), sw)
                screen.data[screen_index] = door.combos[door_offset + door_index]
                screen.cset[screen_index] = door.csets[door_offset + door_index]


def replace_matching_subgrids(screen, door, door_offset, with_door, with_door_offset, sw, sh):
    for x, y in find_matching_subgrids(door, door_offset, sw, sh):
        for sx in range(sw):
            for sy in range(sh):
                screen_index = to_index(x + sx, y + sy, screen_width)
                door_index = to_index(*mirror_xy(sx, sy, sw - 1, sh - 1), sw)
                screen.data[screen_index] = with_door.combos[with_door_offset + door_index]
                screen.cset[screen_index] = with_door.csets[with_door_offset + door_index]


# .......
tile_mappings = {}

OPEN_DOOR_OFFSET = 0
WALL_OFFSET_VER = 28
BOMB_OFFSET_VER = 32
WALL_OFFSET_HOR = 43


def replace_matching_subgrids_2(door, to_door, door_offset, sw, sh):
    for sx in range(sw):
        for sy in range(sh):
            door_index = to_index(sx, sy, sw)
            tile_mappings[door.combos[door_offset + door_index]
                          ] = to_door.combos[door_offset + door_index]


def mirror_matching_subgrids_2(door, to_door, door_offset, sw, sh):
    for sx in range(sw):
        for sy in range(sh):
            door_index_1 = to_index(sx, sy, sw)
            door_index_2 = to_index(*mirror_xy(sx, sy, sw - 1, sh - 1), sw)
            tile_mappings[door.combos[door_offset + door_index_1]
                          ] = to_door.combos[door_offset + door_index_2]


for door_set in reader.doors:
    # for i in range(len(door_set.up.combos)):
    # for i in range(4):
    #     tile_mappings[door_set.up.combos[i]] = door_set.down.combos[i]
    #     tile_mappings[door_set.down.combos[i]] = door_set.up.combos[i]

    # for i in range(4):
    #     i += WALL_OFFSET_VER
    #     tile_mappings[door_set.up.combos[i]] = door_set.down.combos[i]
    #     tile_mappings[door_set.down.combos[i]] = door_set.up.combos[i]

    # print(door_set.down.combos)
    # print(door_set.up.combos)
    # print(tile_mappings)

    # combos_to_not_modify.update(door_set.up.combos)
    # combos_to_not_modify.update(door_set.down.combos)
    # combos_to_not_modify.update(door_set.left.combos)
    # combos_to_not_modify.update(door_set.right.combos)

    # replace_matching_subgrids_2(door_set.up, door_set.down, OPEN_DOOR_OFFSET, 2, 2)
    # replace_matching_subgrids_2(door_set.down, door_set.up, OPEN_DOOR_OFFSET, 2, 2)
    # replace_matching_subgrids_2(door_set.up, door_set.down, WALL_OFFSET_VER, 2, 2)
    # replace_matching_subgrids_2(door_set.down, door_set.up, WALL_OFFSET_VER, 2, 2)

    # mirror_matching_subgrids_2(door_set.left, door_set.right, OPEN_DOOR_OFFSET, 2, 3)
    # mirror_matching_subgrids_2(door_set.right, door_set.left, OPEN_DOOR_OFFSET, 2, 3)
    # mirror_matching_subgrids_2(door_set.left, door_set.right, WALL_OFFSET_HOR, 2, 3)
    # mirror_matching_subgrids_2(door_set.right, door_set.left, WALL_OFFSET_HOR, 2, 3)
    pass

# (inside map.screens loop) /end


original_data = screen.data.copy()

# Door combo sets are >1x1 groups of tiles that need specific handling when
# mirroring. Locate usages of these combo sets by finding matching subgrids
# and then mirror the subgrid.
# This is done before mirroring all the screen tiles as if there were 1x1
# logical tiles.

# TODO: also swap door set up,down

# original_data = screen.data.copy()
for door_set in reader.doors:
    # replace_matching_subgrids(
    #     screen, door_set.up, OPEN_DOOR_OFFSET, door_set.down, OPEN_DOOR_OFFSET, 2, 2)
    # replace_matching_subgrids(
    #     screen, door_set.down, OPEN_DOOR_OFFSET, door_set.up, OPEN_DOOR_OFFSET, 2, 2)
    # replace_matching_subgrids(screen, door_set.up,
    #                         WALL_OFFSET_VER, door_set.down, WALL_OFFSET_VER, 2, 2)
    # replace_matching_subgrids(screen, door_set.down,
    #                         WALL_OFFSET_VER, door_set.up, WALL_OFFSET_VER, 2, 2)
    # replace_matching_subgrids(screen, door_set.up,
    #                         BOMB_OFFSET_VER, door_set.down, BOMB_OFFSET_VER, 2, 2)
    # replace_matching_subgrids(screen, door_set.down,
    #                         BOMB_OFFSET_VER, door_set.up, BOMB_OFFSET_VER, 2, 2)

    # replace_matching_subgrids(
    #     screen, door_set.left, OPEN_DOOR_OFFSET, door_set.right, OPEN_DOOR_OFFSET, 2, 3)
    # replace_matching_subgrids(
    #     screen, door_set.right, OPEN_DOOR_OFFSET, door_set.left, OPEN_DOOR_OFFSET, 2, 3)
    # replace_matching_subgrids(
    #     screen, door_set.left, WALL_OFFSET_HOR, door_set.right, WALL_OFFSET_HOR, 2, 3)
    # replace_matching_subgrids(
    #     screen, door_set.right, WALL_OFFSET_HOR, door_set.left, WALL_OFFSET_HOR, 2, 3)
    pass

original_data = screen.data
for door_set in reader.doors:
    # mirror_matching_subgrids(screen, door_set.left, OPEN_DOOR_OFFSET, 2, 3)
    # mirror_matching_subgrids(screen, door_set.right, OPEN_DOOR_OFFSET, 2, 3)
    # mirror_matching_subgrids(screen, door_set.up, OPEN_DOOR_OFFSET, 2, 2)
    # mirror_matching_subgrids(screen, door_set.down, OPEN_DOOR_OFFSET, 2, 2)
    # mirror_matching_subgrids(screen, door_set.up, WALL_OFFSET_VER, 2, 2)
    # mirror_matching_subgrids(screen, door_set.down, WALL_OFFSET_VER, 2, 2)
    # mirror_matching_subgrids(screen, door_set.left, WALL_OFFSET_HOR, 2, 3)
    # mirror_matching_subgrids(screen, door_set.right, WALL_OFFSET_HOR, 2, 3)
    pass

for door_set in reader.doors:
combos_to_not_flip.update(door_set.up.combos)
combos_to_not_flip.update(door_set.down.combos)
combos_to_not_flip.update(door_set.left.combos)
combos_to_not_flip.update(door_set.right.combos)
