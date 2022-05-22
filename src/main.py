import argparse
import struct
from PIL import Image
from zquest.extract import ZeldaClassicReader

parser = argparse.ArgumentParser()
parser.add_argument('input', type=str)
parser.add_argument('--save-midis', action='store_true', help='Extracts MIDI files and saves to output folder')
parser.add_argument('--save-tiles', action='store_true', help='Extracts tilesheets as PNG for a particular cset and saves to output folder')
parser.add_argument('--save-csets', action='store_true', help='Extracts csets as GPL files (ex: for use in Aseprite) and saves to output folder')
options = parser.parse_args()


def save_midi_file(zc_midi, tracks, path):
    tracks_with_data = []
    for track in tracks:
        if len(track) == 0:
            break
        tracks_with_data.append(track)

    midi_format = 0 if len(tracks_with_data) == 1 else 1
    args = [
        b'MThd',
        6,
        midi_format,
        len(tracks_with_data),
        zc_midi['divisions'],
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
        for i in range(len(reader.midis['tunes'])):
            zc_midi = reader.midis['tunes'][i]
            if 'title' in zc_midi:
                title = zc_midi['title']
                save_midi_file(
                    zc_midi, reader.midi_tracks[i], f'output/midi{i}.mid')

    with open('output/data.json', 'w') as file:
        file.write(reader.to_json())

    # Save Pallete files (for aseprite).
    if options.save_csets:
        cset_colors = reader.csets['cset_colors']
        for i in range(len(cset_colors)):
            colors = cset_colors[i]
            if all(r + g + b == 0 for (r, g, b, a) in colors):
                break

            gpl_text = 'GIMP Palette\nChannels: RGBA\n#\n' + \
                '\n'.join(
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
                        cset_offset = tile['pixels'][tile_offset]  # 0-15
                        x = spritesheet_x + tx
                        y = spritesheet_y + ty

                        EXPORT_WITH_CSET = None
                        # EXPORT_WITH_CSET = 3
                        if EXPORT_WITH_CSET is None:
                            if (cset_offset == 0):
                                pixels[x, y] = (0, 0, 0, 0)
                            else:
                                pixels[x, y] = (0, 0, cset_offset)
                        else:
                            if (cset_offset == 0):
                                pixels[x, y] = (0, 0, 0, 0)
                            else:
                                color = cset_colors[EXPORT_WITH_CSET][cset_offset]
                                pixels[x, y] = color

            img.save(f'output/tiles_{str(page_index).zfill(3)}.png')
            page_index += 1
