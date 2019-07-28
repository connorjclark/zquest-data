import sys
from extract import *
from helloworld import *

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
    num_sprites_to_render_side = 20  
    img = Image.new('RGB', (num_sprites_to_render_side*16,num_sprites_to_render_side*16))
    pixels = img.load() 
    for tile_index in range(num_sprites_to_render_side*num_sprites_to_render_side):
      tile = r.tiles[tile_index]
      spritesheet_x = (tile_index % num_sprites_to_render_side) * 16
      spritesheet_y = int(tile_index / num_sprites_to_render_side) * 16
      
      for tx in range(16):
        for ty in range(16):
          tile_offset = tx + ty * 16
          color_index = tile[tile_offset]
          color = int(color_index / 25 * 256)
          
          x = spritesheet_x + tx
          y = spritesheet_y + ty
          pixels[x,y] = (color, color, color)
        
    img.show()
