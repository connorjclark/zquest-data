import sys
from extract import *
from PIL import Image

if __name__ == "__main__":
  path = sys.argv[1]
  with open(path, "rb") as f:
    b = Bytes(f)
    r = ZeldaClassicReader(b)
    if path.endswith('.qst'):
      r.read_qst()
    else:
      r.read_zgp()

    print('num tiles', len(r.tiles))
    print('num combos', len(r.combos))

    # save 400 at a time
    tiles_per_row = 20
    rows_per_page = 13
    sprite_size = 16

    tile_index = 0
    page_index = 0
    while tile_index < len(r.tiles):
      img = Image.new('RGB', (tiles_per_row * sprite_size, rows_per_page * sprite_size))
      pixels = img.load()
      for tile_index_offset in range(tiles_per_row * rows_per_page):
        index = tile_index + tile_index_offset
        if index >= len(r.tiles):
          break

        tile = r.tiles[index]
        spritesheet_x = (tile_index_offset % tiles_per_row) * sprite_size
        spritesheet_y = int(tile_index_offset / tiles_per_row) * sprite_size

        for tx in range(sprite_size):
          for ty in range(sprite_size):
            tile_offset = tx + ty * sprite_size
            color_index = tile[tile_offset]
            color = int(color_index / 25 * 256)
            
            x = spritesheet_x + tx
            y = spritesheet_y + ty
            pixels[x,y] = (color, color, color)
        
        tile_index += 1

      img.save(f'output/tiles_{page_index}.png')
      page_index += 1
