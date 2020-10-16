from struct import *
import sys
import json
import math
from decode_wrapper import *
from pretty_json import *
import io
import os
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

class Version:
  def __init__(self, zelda_version=None, build=None):
    self.zelda_version = zelda_version
    self.build = build
  
  def __str__(self):
    parts = []
    if self.zelda_version != None:
      parts.append(f'zelda_version = {hex(self.zelda_version)}')
    if self.build != None:
      parts.append(f'build = {self.build}')
    return ', '.join(parts)
  
  def _cmp(self, other):
    if self.zelda_version == None or other.zelda_version == None:
      if self.zelda_version != None or other.zelda_version != None:
        raise 'Invalid input'
    
    if self.build == None or other.build == None:
      if self.build != None or other.build != None:
        raise 'Invalid input'
    
    if self.zelda_version > other.zelda_version:
      return 1
    elif self.zelda_version < other.zelda_version:
      return -1
    
    if self.build > other.build:
      return 1
    elif self.build < other.build:
      return -1
    
    return 0
  
  def __eq__(self, other):
    return self._cmp(other) == 0

  def __ge__(self, other):
    return self._cmp(other) >= 0

  def __gt__(self, other):
    return self._cmp(other) > 0
  
  def __le__(self, other):
    return self._cmp(other) <= 0

  def __lt__(self, other):
    return self._cmp(other) < 0


class Bytes:
  def __init__(self, f):
    self.f = f
    self.bytes_read = 0

    f.seek(0, os.SEEK_END)
    self.length = f.tell()
    f.seek(0)
  
  def has_bytes(self):
    more_bytes = self.f.read(1) != b''
    if more_bytes:
      self.f.seek(-1,1)
    return more_bytes

  def peek(self):
    byte = self.f.read(1)
    if byte != b'':
      self.f.seek(-1,1)
    return byte
  
  def read(self, n):
    if n == 0:
      return b''

    data = self.f.read(n)
    self.bytes_read += n
    return data
  
  def read_byte(self):
    return unpack('B', self.read(1))[0]

  def read_int(self):
    return unpack('<H', self.read(2))[0]

  def read_long(self):
    return unpack('<I', self.read(4))[0]
  
  def read_array(self, word_size, length):
    if (word_size == 1):
      read = self.read_byte
    elif (word_size == 2):
      read = self.read_int
    elif (word_size == 4):
      read = self.read_long
    return [read() for _ in range(length)]
  
  def read_str(self, n):
    raw = self.read(n)
    if raw.find(b'\x00') != -1:
      return raw[0:raw.index(b'\x00')].decode('utf-8', errors='ignore')
    else:
      return raw.decode('utf-8', errors='ignore')

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
        print('decoding failed, trying different method')
        continue
      else:
        raise Exception(f'error decoding: {err}.')

    if err != 0:
      raise Exception('Could not decode file')
    print('decoded file successfully')

    f = open('./output/decoded.data', 'wb')
    f.write(decoded)
    f.close()

    # remake the byte reader with the decoded data
    header_start = decoded.find(b'HDR')
    if header_start == -1:
      raise Exception('could not find HDR section')
    self.b = Bytes(io.BytesIO(decoded[header_start:]))

    # actually read the file now
    while self.b.has_bytes():
      self.read_section()

  # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L5414
  def read_zgp(self):
    id, section_version, section_cversion = self.read_section_header()
    assert_equal(ID_GRAPHICSPACK, id) 

    while self.b.has_bytes():
      self.read_section()


  # https://github.com/ArmageddonGames/ZeldaClassic/blob/bdac8e682ac1eda23d775dacc5e5e34b237b82c0/src/zq_class.cpp#L6189
  # https://github.com/ArmageddonGames/ZeldaClassic/blob/20f9807a8e268172d0bd2b0461e417f1588b3882/src/qst.cpp#L2005
  # zdefs.h
  def read_header(self, section_bytes, section_version, section_cversion):
    # p_iputw = 2 bytes = b.read_int()

    zelda_version = section_bytes.read_int()
    build = section_bytes.read_byte()
    pw_hash = section_bytes.read_str(16)
    internal = section_bytes.read_int()
    quest_number = section_bytes.read_byte()
    version = section_bytes.read_str(9)
    min_version = section_bytes.read_str(9)
    title = section_bytes.read_str(65)
    author = section_bytes.read_str(65)
    use_keyfile = section_bytes.read_byte()

    self.version = Version(zelda_version, build)
    print(self.version)
    # ...

    print('internal', internal)
    print('quest_number', quest_number)
    print('zelda_version', zelda_version)
    print('min_version', min_version)
    print('title', title)
    print('author', author)


  def read_section_header(self):
    id = self.b.read(4)
    section_version = self.b.read_int()
    section_cversion = self.b.read_int()
    return (id, section_version, section_cversion)
  
  
  def read_section(self):
    id, section_version, section_cversion = self.read_section_header()
    size = self.b.read_long()

    if size > 0:
      print(id, size)

    sections = {
      ID_HEADER: self.read_header,
      ID_TILES: self.read_tiles,
      ID_COMBOS: self.read_combos,
      ID_CSETS: self.read_csets,
      ID_DMAPS: self.read_dmaps,
      ID_MAPS: self.read_maps,
      ID_GUYS: self.read_guys,
      ID_WEAPONS: self.read_weapons,
      ID_LINKSPRITES: self.read_link_sprites,
    }

    if size > self.b.length - self.b.bytes_read:
      print('section size is bigger than rest of data, clamping')
      size = self.b.length - self.b.bytes_read

    section_bytes = Bytes(io.BytesIO(self.b.read(size)))
    if id in sections:
      print('read_section', id, size, section_version, section_cversion)
      sections[id](section_bytes, section_version, section_cversion)
      remaining = size - section_bytes.bytes_read
      if remaining != 0:
        print('section did not consume expected number of bytes. remaining:', remaining)
    else:
      # print('unknown section', id, size)
      pass

  
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

  def read_gpak(self, section_version, section_cversion):
    pass


  # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zq_class.cpp#L9184
  def read_tiles(self, section_bytes, section_version, section_cversion):
    # ZC250MAXTILES = 32760
    # NEWMAXTILES = 214500

    if self.version >= Version(zelda_version=0x254, build=41):
      tiles_used = section_bytes.read_long()
    else:
      tiles_used = section_bytes.read_int()

    tiles = []
    while section_bytes.has_bytes():
      tile_format = 1
      if self.version > Version(zelda_version=0x211, build=4):
        tile_format = section_bytes.read_byte()

      pixels = section_bytes.read_array(1, self.tilesize(tile_format))

      if tile_format == 0:
        # ?
        # pass
        break
      elif tile_format == 1:
        # 1 byte per 2 pixels
        pixels_expanded = []
        for val in pixels:
          pixels_expanded.append(val & 0xF)
          pixels_expanded.append((val >> 4) & 0xF)
        pixels = pixels_expanded
      elif tile_format == 2:
        # 1 byte per pixel
        pass
      else:
        raise Exception(f'unexpected format {tile_format}')
      
      tiles.append(pixels)

    self.tiles = tiles

  
  # https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/qst.cpp#L13150
  def read_combos(self, section_bytes, section_version, section_cversion):
    all_descriptors = [
      # TODO: determine which versions each key was added in.
      {'version': 0, 'key': 'tile', 'read': lambda: section_bytes.read_long() if section_version >= 11 else section_bytes.read_int()},
      {'version': 0, 'key': 'flip', 'read': lambda: section_bytes.read_byte()},
      {'version': 0, 'key': 'walk', 'read': lambda: section_bytes.read_byte()},
      {'version': 0, 'key': 'type', 'read': lambda: section_bytes.read_byte()},
      {'version': 0, 'key': 'csets', 'read': lambda: section_bytes.read_byte()},
      {'version': 0, 'key': 'frames', 'read': lambda: section_bytes.read_byte()},
      {'version': 0, 'key': 'speed', 'read': lambda: section_bytes.read_byte()},
      {'version': 0, 'key': 'nextcombo', 'read': lambda: section_bytes.read_int()},
      {'version': 0, 'key': 'nextcset', 'read': lambda: section_bytes.read_byte()},
      {'version': 0, 'key': 'flag', 'read': lambda: section_bytes.read_byte()},
      {'version': 0, 'key': 'skipanim', 'read': lambda: section_bytes.read_byte()},
      {'version': 0, 'key': 'nexttimer', 'read': lambda: section_bytes.read_int()},
      {'version': 0, 'key': 'skipanimy', 'read': lambda: section_bytes.read_byte()},
      {'version': 0, 'key': 'animflags', 'read': lambda: section_bytes.read_byte()},
      # Not tested.
      # {'version': 0, 'key': 'attributes', 'read': lambda: section_bytes.read_array(4, NUM_COMBO_ATTRIBUTES)},
      # {'version': 0, 'key': 'usrflags', 'read': lambda: section_bytes.read_long()},
      # {'version': 0, 'key': 'triggerflags', 'read': lambda: section_bytes.read_array(4, 3)},
      # {'version': 12, 'key': 'triggerlevel', 'read': lambda: section_bytes.read_long()},
    ]
    descriptors = [x for x in all_descriptors if self.version.zelda_version >= x['version']]
    
    combos = []
    num_combos = section_bytes.read_int()
    for _ in range(num_combos):
      combo = {}
      for descriptor in descriptors:
        combo[descriptor['key']] = descriptor['read']()
      combos.append(combo)
    
    self.combos = combos
  
  # https://github.com/ArmageddonGames/ZeldaClassic/blob/bdac8e682ac1eda23d775dacc5e5e34b237b82c0/src/qst.cpp#L15411
  def read_csets(self, section_bytes, section_version, section_cversion):
    # https://github.com/ArmageddonGames/ZeldaClassic/blob/0fddc19a02ccf62c468d9201dd54dcb834b764ca/src/colors.h#L47
    newerpsTOTAL = (6701<<4)*3
    MAXLEVELS = 512
    PALNAMESIZE = 17
    
    color_data = section_bytes.read_array(1, newerpsTOTAL)

    palnames = []
    for _ in range(MAXLEVELS):
      palnames.append(section_bytes.read_str(PALNAMESIZE))

    palcycles = section_bytes.read_int()
    
    cycles = []
    for _ in range(palcycles):
      cycles.append({
        'first': section_bytes.read_array(1, 3),
        'count': section_bytes.read_array(1, 3),
        'speed': section_bytes.read_array(1, 3),
      })
    
    i = 0
    cset_colors = []
    while i < len(color_data):
      colors = []
      for _ in range(16):
        r = color_data[i] * 4
        i += 1
        g = color_data[i] * 4
        i += 1
        b = color_data[i] * 4
        i += 1
        a = 0 if _ == 0 else 255
        colors.append((r, g, b, a))
      
      if all(r + g + b == 0 for (r, g, b, a) in colors):
        break
      
      cset_colors.append(colors)

    self.csets = {
      'color_data': color_data,
      'palnames': palnames,
      'cycles': cycles,
      'cset_colors': cset_colors,
    }
  
  def read_dmaps(self, section_bytes, section_version, section_cversion):
    num_dmaps = section_bytes.read_int()

    for _ in range(num_dmaps):
      map_ = section_bytes.read_byte()

      if section_version <= 4:
        level = section_bytes.read_byte()
      else:
        level = section_bytes.read_int()
      
      xoff = section_bytes.read_byte()
      
      compass = section_bytes.read_byte()
      
      if section_version > 8:
        color = section_bytes.read_int()
      else:
        color = section_bytes.read_byte()
      
      midi = section_bytes.read_byte()
      
      cont = section_bytes.read_byte()
      
      type_ = section_bytes.read_byte()

      grid = section_bytes.read_array(1, 8)

      if self.version < Version(zelda_version=0x192, build=41):
        raise 'TODO'

      name = section_bytes.read_str(21)
      title = section_bytes.read_str(21)
      intro = section_bytes.read_str(73)

      minimap = []
      for __ in range(4):
        entry = {}
        if section_version >= 11:
          entry['tile'] = section_bytes.read_long()
        else:
          entry['tile'] = section_bytes.read_int()
        entry['cset'] = section_bytes.read_byte()
        minimap.append(entry)

      if section_version > 1:
        tmusictrack = section_bytes.read_byte()
        active_subscreen = section_bytes.read_byte()
        passive_subscreen = section_bytes.read_byte()
      
      if section_version > 2:
        di = section_bytes.read_array(1, 32)
      
      if section_version >= 6:
        flags = section_bytes.read_long()
      elif section_version > 3:
        temp = section_bytes.read_byte()
      else:
        raise 'TODO'
      
      if section_version < 7:
        raise 'TODO'
      
      if section_version < 8:
        raise 'TODO'
      
      if section_version < 8:
        raise 'TODO'
      
      if self.version > Version(zelda_version=0x192, build=41):
        padding = section_bytes.read_byte()
      
      if section_version >= 10:
        sideview = section_bytes.read_byte()
      
      if section_version >= 12:
        script = section_bytes.read_int()
        section_bytes.read_array(4, 8)
      
      if section_version >= 13:
        section_bytes.read_array(1, 8 * 65)
      
      if section_version >= 14:
        section_bytes.read_int()
        section_bytes.read_int()
        section_bytes.read_array(4, 8)
        section_bytes.read_array(1, 8 * 65)
  
  def read_maps(self, section_bytes, section_version, section_cversion):
    def read_screen():
      screen = {}
      screen['valid'] = section_bytes.read_byte()
      screen['guy'] = section_bytes.read_byte()
      screen['str'] = section_bytes.read_int()
      screen['room'] = section_bytes.read_byte()
      screen['item'] = section_bytes.read_byte()
      screen['hasitem'] = section_bytes.read_byte()

      screen['tilewarptype'] = [section_bytes.read_byte()]
      if self.version > Version(zelda_version=0x211, build=7):
        screen['tilewarptype'].extend(section_bytes.read_array(1, 3))
      
      if self.version > Version(zelda_version=0x192, build=153):
        screen['door_combo_set'] = section_bytes.read_int()

      screen['warpreturnx'] = [section_bytes.read_byte()]
      if self.version > Version(zelda_version=0x211, build=7):
        screen['warpreturnx'].extend(section_bytes.read_array(1, 3))

      screen['warpreturny'] = [section_bytes.read_byte()]
      if self.version > Version(zelda_version=0x211, build=7):
        screen['warpreturny'].extend(section_bytes.read_array(1, 3))
        if section_version >= 18:
          screen['warpreturnc'] = section_bytes.read_int()
        else:
          screen['warpreturnc'] = section_bytes.read_byte()
      
      screen['stairx'] = section_bytes.read_byte()
      screen['stairy'] = section_bytes.read_byte()
      screen['itemx'] = section_bytes.read_byte()
      screen['itemy'] = section_bytes.read_byte()

      if section_version > 15:
        screen['color'] = section_bytes.read_int()
      else:
        screen['color'] = section_bytes.read_byte()
      
      screen['enemyflags'] = section_bytes.read_byte()
      screen['doors'] = section_bytes.read_array(1, 4)

      if section_version <= 11:
        raise 'TODO'
      else:
        tilewarpdmap = section_bytes.read_array(2, 4)
      
      screen['tilewarpscr'] = [section_bytes.read_byte()]
      if self.version > Version(zelda_version=0x211, build=7):
        screen['tilewarpscr'].extend(section_bytes.read_array(1, 3))
      
      if section_version >= 15:
        screen['tilewarpoverlayflags'] = section_bytes.read_byte()
      
      screen['exitdir'] = section_bytes.read_byte()

      screen['enemies'] = []
      for k in range(10):
        if self.version < Version(zelda_version=0x192, build=10):
          screen['enemies'].append(section_bytes.read_byte())
        else:
          screen['enemies'].append(section_bytes.read_int())
        
        if section_version < 9:
          raise 'TODO'

      screen['pattern'] = section_bytes.read_byte()
      
      screen['sidewarptype'] = [section_bytes.read_byte()]
      if self.version > Version(zelda_version=0x211, build=7):
        screen['sidewarptype'].extend(section_bytes.read_array(1, 3))
      
      if section_version >= 15:
        screen['sidewarpoverlayflags'] = section_bytes.read_byte()
      
      screen['warparrivalx'] = section_bytes.read_byte()
      screen['warparrivaly'] = section_bytes.read_byte()
      screen['path'] = section_bytes.read_array(1, 4)
      
      screen['sidewarpscr'] = [section_bytes.read_byte()]
      if self.version > Version(zelda_version=0x211, build=7):
        screen['sidewarpscr'].extend(section_bytes.read_array(1, 3))
      
      if section_version <= 11:
        raise 'TODO'
      else:
        screen['sidewarpdmap'] = section_bytes.read_array(2, 4)
      
      if self.version > Version(zelda_version=0x211, build=7):
        screen['sidewarpindex'] = section_bytes.read_byte()
      
      screen['undercombo'] = section_bytes.read_int()
      screen['undercset'] = section_bytes.read_byte()
      screen['catchall'] = section_bytes.read_int()
      screen['flags'] = section_bytes.read_byte()
      screen['flags2'] = section_bytes.read_byte()
      screen['flags3'] = section_bytes.read_byte()

      if self.version > Version(zelda_version=0x211, build=1):
        screen['flags4'] = section_bytes.read_byte()
      
      if self.version > Version(zelda_version=0x211, build=7):
        screen['flags5'] = section_bytes.read_byte()
        screen['noreset'] = section_bytes.read_int()
        screen['nocarry'] = section_bytes.read_int()
      
      if self.version > Version(zelda_version=0x211, build=9):
        screen['flags6'] = section_bytes.read_byte()
      
      if section_version > 5:
        screen['flags7'] = section_bytes.read_byte()
        screen['flags8'] = section_bytes.read_byte()
        screen['flags9'] = section_bytes.read_byte()
        screen['flags10'] = section_bytes.read_byte()
        screen['csensitive'] = section_bytes.read_byte()
      
      if section_version < 14:
        raise 'TODO'
      else:
        screen['oceansfx'] = section_bytes.read_byte()
        screen['bosssfx'] = section_bytes.read_byte()
        screen['secretsfx'] = section_bytes.read_byte()
      
      if section_version < 15:
        raise 'TODO'
      else:
        screen['holdupsfx'] = section_bytes.read_byte()
      
      if self.version > Version(zelda_version=0x192, build=97):
        screen['layermap'] = section_bytes.read_array(1, 6)
        screen['layerscreen'] = section_bytes.read_array(1, 6)
      else:
        raise 'TODO'
      
      # if self.version > Version(zelda_version=0x192, build=149):
      #   screen['layermap'] = section_bytes.read_array(1, 6)

      if self.version > Version(zelda_version=0x192, build=149):
        screen['layeropacity'] = section_bytes.read_array(1, 6)
      
      if self.version > Version(zelda_version=0x192, build=153):
        if self.version == Version(zelda_version=0x192, build=153):
          screen['padding'] = section_bytes.read_byte()
        screen['timedwarptics'] = section_bytes.read_int()
      
      # extras = 0
      # screen['extras'] = section_bytes.read_array(1, extras)

      if self.version > Version(zelda_version=0x211, build=2):
        screen['nextmap'] = section_bytes.read_byte()
        screen['nextscr'] = section_bytes.read_byte()
      
      # if self.version > Version(zelda_version=0x192, build=2):

      if self.version < Version(zelda_version=0x192, build=137):
        num_secretcombos = 20
      elif self.version < Version(zelda_version=0x192, build=154):
        num_secretcombos = 256
      else:
        num_secretcombos = 128
      if self.version < Version(zelda_version=0x192, build=154):
        screen['secretcombo'] = section_bytes.read_array(1, num_secretcombos)
      else:
        screen['secretcombo'] = section_bytes.read_array(2, 128)

      if self.version > Version(zelda_version=0x192, build=153):
        screen['secretcset'] = section_bytes.read_array(1, 128)
        screen['secretflag'] = section_bytes.read_array(1, 128)
      
      map_size = 16 * 11
      screen['data'] = section_bytes.read_array(2, map_size)

      if self.version > Version(zelda_version=0x192, build=20):
        screen['sflag'] = section_bytes.read_array(1, map_size)
      
      if self.version > Version(zelda_version=0x192, build=97):
        screen['cset'] = section_bytes.read_array(1, map_size)
      
      if section_version > 4:
        screen['screen_midi'] = section_bytes.read_int()
      
      if section_version >= 17:
        screen['lens_layer'] = section_bytes.read_byte()
      
      if section_version > 6:
        screen['numff'] = section_bytes.read_long()
        screen['ff'] = []
        MAXFFCS = 32
        for m in range(MAXFFCS):
          ff = {}
          if (screen['numff'] >> m) & 1:
            ff['data'] = section_bytes.read_int()
            ff['cset'] = section_bytes.read_byte()
            ff['delay'] = section_bytes.read_int()

            if section_version < 9:
              raise 'TODO'
            else:
              ff['x'] = section_bytes.read_long()
              ff['y'] = section_bytes.read_long()
              ff['xdelta'] = section_bytes.read_long()
              ff['ydelta'] = section_bytes.read_long()
              ff['xdelta2'] = section_bytes.read_long()
              ff['ydelta2'] = section_bytes.read_long()
            
            ff['link'] = section_bytes.read_byte()
            
            if section_version > 7:
              ff['width'] = section_bytes.read_byte()
              ff['height'] = section_bytes.read_byte()
              ff['flags'] = section_bytes.read_long()
            
            if section_version > 9:
              ff['script'] = section_bytes.read_int()
            
            if section_version > 10:
              ff['initd'] = section_bytes.read_array(4, 8)
              ff['inita'] = [section_bytes.read_byte() * 10000, section_bytes.read_byte() * 10000]

          screen['ff'].append(ff)
      
      if section_version < 13:
        raise 'TODO'
      
      if section_version >= 19 and self.version.zelda_version > 0x253:
        screen['npcstrings'] = section_bytes.read_array(4, 10)
        screen['new_items'] = section_bytes.read_array(2, 10)
        screen['new_item_x'] = section_bytes.read_array(2, 10)
        screen['new_item_y'] = section_bytes.read_array(2, 10)
      
      if section_version < 19 and self.version.zelda_version > 0x253:
        raise 'TODO'
      
      if section_version >= 20 and self.version.zelda_version > 0x253:
        screen['script'] = section_bytes.read_int()
        screen['screeninitd'] = section_bytes.read_array(4, 8)
      
      if section_version >= 21 and self.version.zelda_version > 0x253:
        screen['preloadscript'] = section_bytes.read_byte()

      if section_version >= 22 and self.version.zelda_version > 0x253:
        screen['hidelayers'] = section_bytes.read_byte()
        screen['hidescriptlayers'] = section_bytes.read_byte()

      return screen

    map_count = section_bytes.read_int()
    maps = []

    for _ in range(map_count):
      map_ = {}
      map_['screens'] = [read_screen() for i in range(136)]
      maps.append(map_)

    self.maps = maps

  def read_guys(self, section_bytes, section_version, section_cversion):
    if section_version <= 3:
      raise 'TODO'
    
    guys = []
    for _ in range(512):
      guy = {}
      guy['name'] = section_bytes.read_str(64)
      guys.append(guy)
    
    for i in range(512):
      guy = guys[i]

      guy['flags'] = section_bytes.read_long()
      guy['flags2'] = section_bytes.read_long()
      if section_version >= 36:
        raise 'TODO' # ?

      guy['tile'] = section_bytes.read_int()
      guy['width'] = section_bytes.read_byte()
      guy['height'] = section_bytes.read_byte()
      guy['s_tile'] = section_bytes.read_int()
      guy['s_width'] = section_bytes.read_byte()
      guy['s_height'] = section_bytes.read_byte()
      guy['e_tile'] = section_bytes.read_int()

      guy['e_width'] = section_bytes.read_byte()
      guy['e_height'] = section_bytes.read_byte()
      guy['hp'] = section_bytes.read_int()
      guy['family'] = section_bytes.read_int()
      guy['cset'] = section_bytes.read_int()
      guy['anim'] = section_bytes.read_int()
      guy['e_anim'] = section_bytes.read_int()
      guy['frate'] = section_bytes.read_int()
      guy['e_frate'] = section_bytes.read_int()

      guy['dp'] = section_bytes.read_int()
      guy['wdp'] = section_bytes.read_int()
      guy['weapon'] = section_bytes.read_int()

      guy['rate'] = section_bytes.read_int()
      guy['hrate'] = section_bytes.read_int()
      guy['step'] = section_bytes.read_int()

      guy['homing'] = section_bytes.read_int()
      guy['grumble'] = section_bytes.read_int()
      guy['item_set'] = section_bytes.read_int()

      if section_version >= 22:
        guy['misc'] = section_bytes.read_array(4, 10)
      else:
        raise 'TODO'
      
      guy['bgsfx'] = section_bytes.read_int()
      guy['bosspal'] = section_bytes.read_int()
      guy['extend'] = section_bytes.read_int()

      if section_version >= 16:
        guy['defense'] = section_bytes.read_array(1, 19)
      
      if section_version >= 18:
        guy['hitsfx'] = section_bytes.read_byte()
        guy['deadsfx'] = section_bytes.read_byte()
      
      if section_version >= 22:
        guy['misc11'] = section_bytes.read_long()
        guy['misc12'] = section_bytes.read_long()
      
      if section_version > 24:
        section_bytes.read_array(1, 41 - 19)
      
      if section_version > 25:
        guy['txsz'] = section_bytes.read_long()
        guy['tysz'] = section_bytes.read_long()
        guy['hxsz'] = section_bytes.read_long()
        guy['hysz'] = section_bytes.read_long()
        guy['hzsz'] = section_bytes.read_long()
      
      if section_version > 26:
        section_bytes.read_long()
        section_bytes.read_long()
        section_bytes.read_long()
        section_bytes.read_long()
        section_bytes.read_long()
      
      if section_version >= 30:
        guy['frozentile'] = section_bytes.read_long()
        guy['frozencset'] = section_bytes.read_long()
        guy['frozenclock'] = section_bytes.read_long()
        guy['frozenmisc'] = section_bytes.read_array(2, 10)

    self.guys = guys

  def read_weapons(self, section_bytes, section_version, section_cversion):
    weapons = []

    if section_version > 2:
      num_weapons = section_bytes.read_int()
      for _ in range(num_weapons):
        weapon = {}
        weapon['name'] = section_bytes.read_str(64)
        weapons.append(weapon)

        if section_version < 5:
          raise 'TODO'

      for i in range(num_weapons):
        weapon = weapons[i]
        weapon['tile'] = section_bytes.read_int()
        weapon['misc'] = section_bytes.read_byte()
        weapon['csets'] = section_bytes.read_byte()
        weapon['frames'] = section_bytes.read_byte()
        weapon['speed'] = section_bytes.read_byte()
        weapon['type'] = section_bytes.read_byte()
        if section_version >= 7:
          weapon['script'] = section_bytes.read_int()
          weapon['newtile'] = section_bytes.read_long()
    else:
      raise 'TODO'

    self.weapons = weapons
  
  def read_link_sprites(self, section_bytes, section_version, section_cversion):
    if section_version >= 6:
      raise 'TODO'

    walk = []
    for _ in range(4):
      walk.append({
        'tile': section_bytes.read_int(),
        'flip': section_bytes.read_byte(),
        'extend': section_bytes.read_byte(),
      })
    
    stab = []
    for _ in range(4):
      stab.append({
        'tile': section_bytes.read_int(),
        'flip': section_bytes.read_byte(),
        'extend': section_bytes.read_byte(),
      })
    
    slash = []
    for _ in range(4):
      slash.append({
        'tile': section_bytes.read_int(),
        'flip': section_bytes.read_byte(),
        'extend': section_bytes.read_byte(),
      })
    
    self.link_sprites = {
      'walk': walk,
      'stab': stab,
      'slash': slash
    }

  def to_json(self):
    data = {
      'combos': self.combos,
      'tiles': self.tiles,
      'csets': self.csets,
      # 'dmaps': self.dmaps,
      'maps': self.maps,
      'guys': self.guys,
      'weapons': self.weapons,
      'link_sprites': self.link_sprites,
    }
    return pretty_json_format(data)
