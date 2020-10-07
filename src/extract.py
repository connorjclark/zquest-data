from struct import *
import sys
import math
from decode_wrapper import *
import io
import numpy as np

# https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zdefs.h#L155
ID_HEADER = b'HDR '
ID_RULES = b'RULE'
ID_STRINGS = b'STR '
ID_MISC = b'MISC'
ID_TILES = b'TILE'
ID_COMBOS = b'CMBO'
ID_CSETS = b'CSET'
ID_MAPS = b'MAP '
ID_DMAPS = b'DMAP'
ID_DOORS = b'DOOR'
ID_ITEMS = b'ITEM'
ID_WEAPONS = b'WPN '
ID_COLORS = b'MCLR'
ID_ICONS = b'ICON'
ID_GRAPHICSPACK = b'GPAK'
ID_INITDATA = b'INIT'
ID_GUYS = b'GUY '
ID_MIDIS = b'MIDI'
ID_CHEATS = b'CHT '
ID_SAVEGAME = b'SVGM'
ID_COMBOALIASES = b'CMBA'
ID_LINKSPRITES = b'LINK'
ID_SUBSCREEN = b'SUBS'
ID_ITEMDROPSETS = b'DROP'
ID_FAVORITES = b'FAVS'
ID_FFSCRIPT = b'FFSC'
ID_SFX = b'SFX '

# V_HEADER =  3
# V_RULES = 15
# V_STRINGS =  6
# V_MISC = 11
# V_TILES =  2
# V_COMBOS = 12
# V_CSETS =  4
# V_MAPS = 22
# V_DMAPS = 13
# V_DOORS =  1
# V_ITEMS = 45
# V_WEAPONS =  7
# V_COLORS =  3
# V_ICONS = 10
# V_GRAPHICSPACK =  1
# V_INITDATA = 19
# V_GUYS = 41
# V_MIDIS =  4
# V_CHEATS =  1
# V_SAVEGAME = 12
# V_COMBOALIASES =  3
# V_LINKSPRITES =  5
# V_SUBSCREEN =  6
# V_ITEMDROPSETS =  2
# V_FFSCRIPT = 13
# V_SFX =  7
# V_FAVORITES =  1

# CV_HEADER = 3
# CV_RULES = 1
# CV_STRINGS = 2
# CV_MISC = 7
# CV_TILES = 1
# CV_COMBOS = 1
# CV_CSETS = 1
# CV_MAPS = 9
# CV_DMAPS = 1
# CV_DOORS = 1
# CV_ITEMS =15
# CV_WEAPONS = 1
# CV_COLORS = 1
# CV_ICONS = 1
# CV_GRAPHICSPACK = 1
# CV_INITDATA =15
# CV_GUYS = 4
# CV_MIDIS = 3
# CV_CHEATS = 1
# CV_SAVEGAME = 5
# CV_COMBOALIASES = 1
# CV_LINKSPRITES = 1
# CV_SUBSCREEN = 3
# CV_ITEMDROPSETS = 1
# CV_FFSCRIPT = 1
# CV_SFX = 5
# CV_FAVORITES = 1

def assert_equal(expected, actual):
  if expected != actual:
    raise Exception(f'expected {expected} but got {actual}')
    
class Bytes:
  def __init__(self, f):
    self.f = f
    self.bytes_read = 0
  
  def has_bytes(self):
    more_bytes = self.f.read(1) != b''
    if more_bytes:
      self.f.seek(-1,1)
    return more_bytes
  
  def read(self, n):
    if n == 0:
      return []

    self.bytes_read += n
    return self.f.read(n)
  
  def read_byte(self):
    return unpack('B', self.read(1))[0]

  def read_int(self):
    return unpack('<H', self.read(2))[0]

  def read_long(self):
    return unpack('<I', self.read(4))[0]
  
  def read_array(self, word_size, length):
    if (word_size == 1):
      read = self.read_byte
    elif (word_size == 4):
      read = self.read_long
    return [read() for _ in range(length)]
  
  def read_str(self, n):
    return bytes(self.read(n))

  def debug(self, n):
    b = self.read(n)
    print('DEBUG')
    print(b)
    print(b.hex())
    for byte in b:
      print(byte)
    self.f.seek(-n, 1)


class ZeldaClassicReader:
  def __init__(self, b):
    self.b = b


  # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L11817
  def read_qst(self):
    # read the header and decompress the data
    # https://github.com/ArmageddonGames/ZeldaClassic/blob/023dd17eaf6a969f47650cb6591cedd0baeaab64/src/zsys.cpp#L676

    # preambles = [
    #   b'AG Zelda Classic Quest File',
    #   b'AG ZC Enhanced Quest File',
    #   b'Zelda Classic Quest File',
    # ]
    # assert_equal(preamble, self.b.read(len(preamble)))

    rest_of_data = self.b.f.read()
    for method in reversed(range(5)):
      err, decoded = py_decode(rest_of_data, len(rest_of_data), method)
      if err == 0:
        break
      elif err == 5:
        # decoding error, try with a different method.
        continue
      else:
        raise Exception(f'error decoding: {err}')
    
    # print(decoded[0], decoded[1], decoded[2], decoded[3])
    # print(decoded[0:120])
    assert_equal(0, err)
    
    # seed = np.int32(self.b.read_byte() << 24)
    # seed += np.int8(self.b.read_byte() & 255) << np.int32(16)
    # seed += np.int8(self.b.read_byte() & 255) << np.int32(8)
    # seed += np.int8(self.b.read_byte() & 255)
    
    # enc_mask = [np.int32(x) for x in [0x4C358938,0x91B2A2D1,0x4A7C1B87,0xF93941E6,0xFD095E94]]
    # method = len(enc_mask) - 1
    # seed ^= enc_mask[method]
    
    # tog = np.int32(0)
    # r = np.int32(0)
    # c1 = np.int16(0)
    # c2 = np.int16(0)
    # rand = Rand007_2(seed)
    
    # # read all the encoded data at once
    # rest_of_data = self.b.f.read()
    # # last 4 bytes are checksum
    # encoded, checksum = rest_of_data[:len(rest_of_data)-4], rest_of_data[len(rest_of_data)-4:]
    
    # # decode
    # decoded = bytearray(len(encoded))
    # i = 0
    # for c in encoded:
    #   c = np.int8(c)
    #   if i % 100000 == 0:
    #     print(i / len(encoded) * 100)

    #   if tog:
    #     c -= np.int8(r)
    #   else:
    #     r = rand.next(method)
    #     c ^= np.int8(r)
      
    #   tog ^= np.int32(1)
    #   c &= np.int8(255)
    #   c1 += c
    #   c2 = (c2 << np.int16(4)) + (c2 >> np.int32(12)) + c
      
    #   decoded[i] = c + 128
    #   i += 1
    
    # # checksums
    # check1 = np.int16(checksum[0]) << np.int16(8)
    # check1 += np.int16(checksum[1] & 255)
    
    # check2 = np.int16(checksum[2]) << np.int16(8)
    # check2 += np.int16(checksum[3] & 255)
    
    # r = rand.next(method)
    # check1 ^= np.int16(r)
    # check2 -= np.int16(r)
    # check1 &= np.int16(0xFFFF)
    # check2 &= np.int16(0xFFFF)
    # assert_equal(check1, c1)
    # assert_equal(check2, c2)

    # remake the byte reader with the decoded data
    header_start = decoded.find(b"HDR")
    self.b = Bytes(io.BytesIO(decoded[header_start:]))

    # actually read the file now
    while self.b.has_bytes():
      self.read_section()

  # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L5414
  def read_zgp(self):
    id, version, cversion = self.read_section_header()
    assert_equal(ID_GRAPHICSPACK, id) 

    while self.b.has_bytes():
      self.read_section()
    

  # https://github.com/ArmageddonGames/ZeldaClassic/blob/bdac8e682ac1eda23d775dacc5e5e34b237b82c0/src/zq_class.cpp#L6189
  # https://github.com/ArmageddonGames/ZeldaClassic/blob/20f9807a8e268172d0bd2b0461e417f1588b3882/src/qst.cpp#L2005
  # zdefs.h
  def read_header(self, version, cversion):
    # p_iputw = 2 bytes = b.read_int()

    version = self.b.read_int()
    build = self.b.read_byte()
    pw_hash = self.b.read_str(16)
    internal = self.b.read_int()
    quest_number = self.b.read_byte()
    version = self.b.read_str(9)
    min_version = self.b.read_str(9)
    title = self.b.read_str(65)
    author = self.b.read_str(65)
    use_keyfile = self.b.read_byte()

    # ...

    print('internal', internal)
    print('quest_number', quest_number)
    print('version', version)
    print('min_version', min_version)
    print('title', title)
    print('author', author)


  def read_section_header(self):
    id = self.b.read(4)
    version = self.b.read_int()
    cversion = self.b.read_int()
    return (id, version, cversion)
  
  
  def read_section(self):
    id, version, cversion = self.read_section_header()
    size = self.b.read_long()
    print('read_section', id, size, version, cversion)

    bytes_read_start = self.b.bytes_read
    
    sections = {
      ID_HEADER: self.read_header,
      ID_TILES: self.read_tiles,
      ID_COMBOS: self.read_combos,
      ID_CSETS: self.read_csets,
    }

    if id in sections:
      sections[id](version, cversion)
    else:
      self.b.read(size)
      print('unknown section', id)
    
    remaining = size - (self.b.bytes_read - bytes_read_start)
    if remaining != 0:
      print('section did not consume expected number of bytes. remaining:', remaining)
      self.b.read(remaining)

  
  # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zdefs.h#L1370
  # def tfbit_bits(self, tfbit):
  #   print(tfbit)
  #   sizes = [-1, 4, 8, 16, 24, 32, -1]
  #   return sizes[tfbit]


  # https://github.com/ArmageddonGames/ZeldaClassic/blob/b56ba20bc6be4a8e4bf01c7c681238d545069baf/src/tiles.cpp#L2579
  def tilesize(self, format):
    if format == 5:
      return 1024
    if format == 4:
      return 768
    if format >= 1 and format <= 3:
      return 64 << format
    
    return 256

  def read_gpak(self, version, cversion):
    pass


  # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L9184
  def read_tiles(self, version, cversion):
    if version > 1:
      tiles_used = self.b.read_long()
    else:
      tiles_used = self.b.read_int()

    num_pixels = 16 * 16
    tiles = []
    for _ in range(tiles_used):
      tile_format = self.b.read_byte()

      if tile_format == 0:
        break
      elif tile_format == 1:
        # 1 byte per 2 pixels
        data_length = int(num_pixels / 2)
        data = self.b.read_array(1, data_length)
        pixels = []
        for val in data:
          pixels.append(val & 0xF)
          pixels.append((val >> 4) & 0xF)
      elif tile_format == 2:
        # 1 byte per pixel
        pixels = self.b.read_array(1, num_pixels)
      else:
        raise Exception(f'unexpected format {tile_format}')
      
      tiles.append(pixels)
    
    self.tiles = tiles

  
  # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L9184
  def read_combos(self, version, cversion):
    all_descriptors = [
      # TODO: determine which versions each key was added in.
      {'version': 0, 'key': 'tile', 'read': lambda: self.b.read_long() if version >= 11 else self.b.read_int()},
      {'version': 0, 'key': 'flip', 'read': lambda: self.b.read_byte()},
      {'version': 0, 'key': 'walk', 'read': lambda: self.b.read_byte()},
      {'version': 0, 'key': 'type', 'read': lambda: self.b.read_byte()},
      {'version': 0, 'key': 'csets', 'read': lambda: self.b.read_byte()},
      {'version': 0, 'key': 'frames', 'read': lambda: self.b.read_byte()},
      {'version': 0, 'key': 'speed', 'read': lambda: self.b.read_byte()},
      {'version': 0, 'key': 'nextcombo', 'read': lambda: self.b.read_int()},
      {'version': 0, 'key': 'nextcset', 'read': lambda: self.b.read_byte()},
      {'version': 0, 'key': 'flag', 'read': lambda: self.b.read_byte()},
      {'version': 0, 'key': 'skipanim', 'read': lambda: self.b.read_byte()},
      {'version': 0, 'key': 'nexttimer', 'read': lambda: self.b.read_int()},
      {'version': 0, 'key': 'skipanimy', 'read': lambda: self.b.read_byte()},
      {'version': 0, 'key': 'animflags', 'read': lambda: self.b.read_byte()},
      # Not tested.
      # {'version': 0, 'key': 'attributes', 'read': lambda: self.b.read_array(4, NUM_COMBO_ATTRIBUTES)},
      # {'version': 0, 'key': 'usrflags', 'read': lambda: self.b.read_long()},
      # {'version': 0, 'key': 'triggerflags', 'read': lambda: self.b.read_array(4, 3)},
      # {'version': 12, 'key': 'triggerlevel', 'read': lambda: self.b.read_long()},
    ]
    descriptors = [x for x in all_descriptors if version >= x['version']]
    
    combos = []
    num_combos = self.b.read_int()
    for _ in range(num_combos):
      combo = {}
      for descriptor in descriptors:
        combo[descriptor['key']] = descriptor['read']()
      combos.append(combo)
    
    self.combos = combos
  
  # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L8880
  def read_csets(self, version, cversion):
    ## TODO: github source doesn't go back far enough
    return
    
    # https://github.com/ArmageddonGames/ZeldaClassic/blob/0fddc19a02ccf62c468d9201dd54dcb834b764ca/src/colors.h#L47
    newerpsTOTAL = (6701<<4)*3
    MAXLEVELS = 512
    PALNAMESIZE = 17
    palnames_length = MAXLEVELS * PALNAMESIZE
    
    color_data = self.b.read(newerpsTOTAL)
    palnames = self.b.read(palnames_length)
    palcycles = self.b.read_int()
    
    cycles = []
    for _ in range(palcycles):
      cycles.push({
        'first': self.b.read_array(1, 4),
        'count': self.b.read_array(1, 4),
        'speed': self.b.read_array(1, 4),
      })
