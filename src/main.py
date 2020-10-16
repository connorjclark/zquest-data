import sys
import re
from extract import *
from PIL import Image

def slugify(value):
  value = str(value).strip().replace(' ', '_')
  return re.sub(r'(?u)[^-\w.]', '', value)


if __name__ == "__main__":
  path = sys.argv[1]
  with open(path, "rb") as f:
    b = Bytes(f)
    reader = ZeldaClassicReader(b)
    if path.endswith('.qst'):
      reader.read_qst()
    else:
      reader.read_zgp()

    print('num tiles', len(reader.tiles))
    print('num combos', len(reader.combos))

    with open('output/data.json', 'w') as file:
      file.write(reader.to_json())

    # Save Pallete files (for aseprite).
    cset_colors = reader.csets['cset_colors']
    for i in range(len(cset_colors)):
      colors = cset_colors[i]
      if all(r + g + b == 0 for (r, g, b, a) in colors):
        break

      gpl_text = 'GIMP Palette\nChannels: RGBA\n#\n' + '\n'.join([f'{r} {g} {b} {a} Untitled' for (r, g, b, a) in colors])
      with open(f'output/cset-{i}.gpl', 'w') as file:
        file.write(gpl_text)

    # Save images.

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
            cset_offset = tile[tile_offset] # 0-15
            x = spritesheet_x + tx
            y = spritesheet_y + ty

            EXPORT_WITH_CSET = None
            # EXPORT_WITH_CSET = 3
            if EXPORT_WITH_CSET is None:
              if (cset_offset == 0):
                pixels[x,y] = (0, 0, 0, 0)
              else:
                pixels[x,y] = (0, 0, cset_offset)
            else:
              if (cset_offset == 0):
                pixels[x,y] = (0, 0, 0, 0)
              else:
                color = cset_colors[EXPORT_WITH_CSET][cset_offset]
                pixels[x,y] = color

      img.save(f'output/tiles_{str(page_index).zfill(3)}.png')
      page_index += 1
