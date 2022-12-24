import argparse
import pathlib
import logging
from pprint import pprint
from zquest.extract import ZeldaClassicReader

# Number of tiles in a screen
screen_width = 16
screen_height = 11

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--input-file', type=str)
parser.add_argument('--input-folder', type=str)
parser.add_argument('-log',
                    '--loglevel',
                    default='warning',
                    help='Provide logging level. Example --loglevel debug, default=warning')

options = parser.parse_args()
if options.input_file and options.input_folder:
    raise Exception('must only provide one of input_file or input_folder')

logging.basicConfig(level=options.loglevel.upper())


def to_index(x: int, y: int, w: int) -> int:
    return x + y * w


def bit(flags: bytes, index: int) -> bool:
    byte_index = int(index // 8)
    bit_index = index % 8
    return (flags[byte_index] & (1 << bit_index)) != 0


def get_qst_stats(in_path: str):
    reader = ZeldaClassicReader(in_path)
    reader.read_qst()

    quest_rules = reader.get_quest_rules().get_values()

    most_unique_combos_on_screen = {'val': 0, 'screen': None}
    num_enemies = 0
    num_ff = 0
    num_screen_flags = 0
    num_screen_items = 0
    num_valid_screens = 0
    screen_flags = {}

    for map_index, map in enumerate(reader.maps):
        for screen_index, screen in enumerate(map.screens):
            if not screen.valid:
                continue

            num_valid_screens += 1
            num_enemies += len([x for x in screen.enemies if x != 0])
            if hasattr(screen, 'ff'):
                num_ff += len([x for x in screen.ff if x != None])

            if hasattr(screen, 'has_item') and screen.has_item:
                num_screen_items += 1

            for flag in (f for f in screen.sflag if f != 0):
                num_screen_flags += 1
                if flag not in screen_flags:
                    screen_flags[flag] = 0
                screen_flags[flag] += 1

            num_unique_combos = len(set(screen.data))
            if num_unique_combos > most_unique_combos_on_screen['val']:
                most_unique_combos_on_screen['val'] = num_unique_combos
                most_unique_combos_on_screen['screen'] = (map_index, screen_index)

    return {
        'most_unique_combos_on_screen': most_unique_combos_on_screen,
        'num_combos': len(reader.combos),
        'num_dmaps': len([dmap for dmap in reader.dmaps if dmap.name.strip() != '' or dmap.title.strip() != '']),
        'num_enemies': num_enemies,
        'num_ff': num_ff,
        'num_maps': len(reader.maps),
        'num_screen_flags': num_screen_flags,
        'num_screen_items': num_screen_items,
        'num_valid_screens': num_valid_screens,
        'quest_rules': quest_rules,
        'screen_flags': screen_flags,
    }


if options.input_file:
    stats = get_qst_stats(options.input_file)
    pprint(stats)
elif options.input_folder:
    for input_file in pathlib.Path(options.input_folder).glob('**/*.qst'):
        print(input_file)
        stats = get_qst_stats(input_file.as_posix())
        pprint(stats)
