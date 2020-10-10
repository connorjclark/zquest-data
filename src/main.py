import sys
from extract import *
from PIL import Image

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

    # Save images.

    # save 400 at a time
    tiles_per_row = 20
    rows_per_page = 13
    sprite_size = 16

    tile_index = 0
    page_index = 0
    while tile_index < len(reader.tiles):
      img = Image.new('RGB', (tiles_per_row * sprite_size, rows_per_page * sprite_size))
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

            cset_index = 0
            color_index = cset_index * 16 * 3 + cset_offset * 3
            r = reader.csets['color_data'][color_index + 0] * 4
            g = reader.csets['color_data'][color_index + 1] * 4
            b = reader.csets['color_data'][color_index + 2] * 4
            
            x = spritesheet_x + tx
            y = spritesheet_y + ty
            pixels[x,y] = (r, g, b)

      img.save(f'output/tiles_{page_index}.png')
      page_index += 1
