from dataclasses import dataclass
from typing import Any, List, Optional
import types
from bytes import Bytes

# https://github.com/ArmageddonGames/ZeldaClassic/blob/30c9e17409304390527fcf84f75226826b46b819/src/zdefs.h#L155

SECTION_IDS = types.SimpleNamespace()
SECTION_IDS.HEADER = b'HDR '
SECTION_IDS.RULES = b'RULE'
SECTION_IDS.STRINGS = b'STR '
SECTION_IDS.MISC = b'MISC'
SECTION_IDS.TILES = b'TILE'
SECTION_IDS.COMBOS = b'CMBO'
SECTION_IDS.CSETS = b'CSET'
SECTION_IDS.MAPS = b'MAP '
SECTION_IDS.DMAPS = b'DMAP'
SECTION_IDS.DOORS = b'DOOR'
SECTION_IDS.ITEMS = b'ITEM'
SECTION_IDS.WEAPONS = b'WPN '
SECTION_IDS.COLORS = b'MCLR'
SECTION_IDS.ICONS = b'ICON'
SECTION_IDS.GRAPHICSPACK = b'GPAK'
SECTION_IDS.INITDATA = b'INIT'
SECTION_IDS.GUYS = b'GUY '
SECTION_IDS.MIDIS = b'MIDI'
SECTION_IDS.CHEATS = b'CHT '
SECTION_IDS.SAVEGAME = b'SVGM'
SECTION_IDS.COMBOALIASES = b'CMBA'
SECTION_IDS.LINKSPRITES = b'LINK'
SECTION_IDS.SUBSCREEN = b'SUBS'
SECTION_IDS.ITEMDROPSETS = b'DROP'
SECTION_IDS.FAVORITES = b'FAVS'
SECTION_IDS.FFSCRIPT = b'FFSC'
SECTION_IDS.SFX = b'SFX '

@dataclass
class F:
  name: str
  type: str
  fields: Optional[List[Any]] = None # List[F]
  arr_len: Optional[int] = None
  str_len: Optional[int] = None


def read_field_value(bytes: Bytes, field: F):
  if field.type == 'object':
    result = {}
    for f in field.fields:
      result[f.name] = read_field(bytes, f)
    return result
  
  match field.type:
    case 'I':
      return bytes.read_long()
    case 'H':
      return bytes.read_int()
    case 'B':
      return bytes.read_byte()
    case 'str':
      if field.str_len == None:
        raise 'must have str_len'
      return bytes.read_str(field.str_len)
    case _:
      raise Exception(f'unexpected type {field.type}')


def read_field(bytes: Bytes, field: F):
  if field.arr_len != None:
    result = []
    for _ in range(field.arr_len):
      result.append(read_field_value(bytes, field))
    return result
  
  return read_field_value(bytes, field)


def if_(bool: bool, first: Any, second: Any):
  return first if bool else second


def read_section(bytes, id, zelda_version, sversion):
  fields = get_fields(bytes, id, zelda_version, sversion)
  # print(fields)
  return read_field(bytes, fields)


def get_fields(bytes, id, zelda_version, sversion):
  match id:
    case SECTION_IDS.COMBOS:
      return combo_fields(bytes, zelda_version, sversion)
    case _:
      raise Exception(f'unexpected id {id}')


def combo_fields(bytes, zelda_version, sversion):
  if zelda_version < 0x174:
    num_combos = 1024
  elif zelda_version < 0x191:
    num_combos = 2048
  else:
    num_combos = bytes.read_int()

  fields = [
    F(name='tile', type=if_(sversion >= 11, 'I', 'H')),
    F(name='flip', type='B' ),
    F(name='walk', type='B' ),
    F(name='type', type='B' ),
    F(name='csets', type='B' ),
    F(name='_padding', type='2s') if zelda_version < 0x193 else None,
    F(name='_padding', type='16s') if zelda_version == 0x191 else None,
    F(name='frames', type='B' ),
    F(name='speed', type='B' ),
    F(name='nextcombo', type='H' ),
    F(name='nextcset', type='B' ),
    F(name='flag', type='B') if sversion >= 3 else None,
    F(name='skipanim', type='B') if sversion >= 4 else None,
    F(name='nexttimer', type='H') if sversion >= 4 else None,
    F(name='skipanimy', type='B') if sversion >= 5 else None,
    F(name='animflags', type='B') if sversion >= 6 else None,
    F(name='attributes', arr_len= 4, type='I') if sversion >= 8 else None,
    F(name='usrflags', type='I') if sversion >= 8 else None,

    F(name='triggerFlags', arr_len= 2, type='I') if sversion == 9 else None,
    F(name='triggerLevel', type='I') if sversion == 9 else None,
    F(name='triggerFlags', arr_len= 3, type='I') if sversion >= 10 else None,
    F(name='triggerLevel', type='I') if sversion >= 10 else None,

    F(name='label', arr_len= 11, type='B') if sversion >= 12 else None,
    F(name='_padding', type='11s') if zelda_version < 0x193 else None,
    F(name='attribytes', arr_len= 4, type='B') if sversion >= 13 else None,
    F(name='script', type='H') if sversion >= 14 else None,
    F(name='initd', arr_len= 2, type='I') if sversion >= 14 else None,
  ]
  fields = [f for f in fields if f]

  return F(name='', type='object', arr_len=num_combos, fields=fields)
