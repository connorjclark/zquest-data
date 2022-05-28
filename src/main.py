import argparse
import os
import struct
from PIL import Image
from zquest.extract import ZeldaClassicReader

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('input', type=str)
parser.add_argument('--save-midis', action='store_true',
                    help='extracts MIDI files and saves to output folder')
parser.add_argument('--save-tiles', action='store_true',
                    help='extracts tilesheets as PNG for a particular cset and saves to output folder')
parser.add_argument('--cset', type=int, default=-1,
                    help='cset to use for --save-tiles. Set to -1 to save as raw index values')
parser.add_argument('--save-csets', action='store_true',
                    help='extracts csets as GPL files (ex: for use in Aseprite) and saves to output folder')
options = parser.parse_args()


def save_midi_file(midi, path):
    tracks_with_data = []
    for track in midi.tracks:
        if len(track) == 0:
            break
        tracks_with_data.append(track)

    midi_format = 0 if len(tracks_with_data) == 1 else 1
    args = [
        b'MThd',
        6,
        midi_format,
        len(tracks_with_data),
        midi.divisions,
    ]
    data = struct.pack('>4sLhhh', *args)

    for track in tracks_with_data:
        args = [
            b'MTrk',
            len(track),
        ]
        data += struct.pack('>4sL', *args)
        data += track

    with open(path, 'wb') as file:
        file.write(data)


if __name__ == "__main__":
    path = options.input
    reader = ZeldaClassicReader(path)
    if path.endswith('.qst'):
        reader.read_qst()
    else:
        reader.read_zgp()

    print('num tiles', len(reader.tiles))
    print('num combos', len(reader.combos))

    if options.save_midis:
        os.makedirs('output/midis', exist_ok=True)
        for i, midi in enumerate(reader.midis):
            if midi:
                save_midi_file(midi, f'output/midis/{i}-{midi.title}.mid')

    with open('output/data.json', 'w') as file:
        file.write(reader.to_json())

    # Save Pallete files (for aseprite).
    if options.save_csets:
        for i, colors in enumerate(reader.cset_colors):
            if all(r + g + b == 0 for (r, g, b, a) in colors):
                break

            gpl_text = 'GIMP Palette\nChannels: RGBA\n#\n' + '\n'.join(
                [f'{r} {g} {b} {a} Untitled' for (r, g, b, a) in colors])
            with open(f'output/cset-{i}.gpl', 'w') as file:
                file.write(gpl_text)

    # Save images.
    if options.save_tiles:
        # save 400 at a time
        tiles_per_row = 20
        rows_per_page = 13
        sprite_size = 16

        tile_index = 0
        page_index = 0

        if options.cset == -1:
            colors = [(0, 0, i) for i in range(16)]
            colors[0] = (0, 0, 0, 0)
        else:
            colors = reader.cset_colors[options.cset]

        while tile_index < len(reader.tiles):
            img = Image.new('RGBA', (tiles_per_row * sprite_size, rows_per_page * sprite_size))
            pixels = img.load()
            for index_in_page in range(tiles_per_row * rows_per_page):
                if tile_index >= len(reader.tiles):
                    break

                tile = reader.tiles[tile_index]
                tile_index += 1
                spritesheet_x = (index_in_page % tiles_per_row) * sprite_size
                spritesheet_y = int(index_in_page / tiles_per_row) * sprite_size

                for tx in range(sprite_size):
                    for ty in range(sprite_size):
                        tile_offset = tx + ty * sprite_size
                        cset_offset = tile.pixels[tile_offset]  # 0-15
                        x = spritesheet_x + tx
                        y = spritesheet_y + ty
                        pixels[x, y] = colors[cset_offset]

            img.save(f'output/tiles_{str(page_index).zfill(3)}.png')
            page_index += 1
