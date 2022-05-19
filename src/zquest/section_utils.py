from __future__ import annotations
import io
from typing import TYPE_CHECKING, Any, Tuple
import types

from zquest.bytes import Bytes
from zquest.field import F
from zquest.sections.cmbo import get_cmbo_field
from zquest.sections.map import get_map_field
from zquest.version import Version

if TYPE_CHECKING:
  from zquest.extract import ZeldaClassicReader

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


def read_field_value(bytes: Bytes, field: F):
  match field.type:
    case 'object':
      result = {}
      for f in field.fields:
        if f:
          result[f.name] = read_field(bytes, f)

      # hack to avoid lack of a good object structure in the field structure...
      # TODO: make this better
      if len(field.fields) == 1 and field.fields[0].name == '':
        return result['']

      return result
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

    if field.arr_bitmask:
      # TODO: do not hardcode type
      mask = bytes.read_long()
      for i in range(field.arr_len):
        result.append(read_field_value(bytes, field) if (mask >> i) & 1 else None)
    else:
      for _ in range(field.arr_len):
        result.append(read_field_value(bytes, field))
    return result
  else:
    return read_field_value(bytes, field)


def serialize(reader: ZeldaClassicReader) -> bytearray:
  reader.b.rewind()
  raw_byte_array = bytearray(reader.b.read(reader.b.length))

  # TODO: Currently doesn't support every section.
  ids = [
    SECTION_IDS.COMBOS,
    # SECTION_IDS.MAPS,
  ]
  for id in ids:
    combos_raw_bytes = serialize_section(reader, id)
    combos_start = reader.section_offsets[id]
    combos_end = combos_start + reader.section_lengths[id] + 12
    raw_byte_array[combos_start:combos_end] = combos_raw_bytes

  return raw_byte_array


def serialize_section(reader: ZeldaClassicReader, id: bytes) -> bytes:
  bytes = Bytes(io.BytesIO())

  assert len(id) == 4
  bytes.write(id)
  bytes.write_int(reader.section_versions[id])
  bytes.write_int(reader.section_cversions[id])
  bytes.write_long(0)
  assert len(bytes.f.getvalue()) == 12

  match id:
    case SECTION_IDS.COMBOS:
      write_field(bytes, reader.combos, reader.section_fields[id])
    case SECTION_IDS.MAPS:
      write_field(bytes, reader.maps, reader.section_fields[id])
    case _:
      raise Exception(f'unexpected id {id}')

  bytes.f.seek(8)
  bytes.write_long(len(bytes.f.getvalue()) - 12)

  return bytes.f.getvalue()


def write_field(bytes: Bytes, data: Any, field: F):
  if field.arr_len != None:
    data_array = data[field.name] if field.name else data
    if field.encode_arr_len != None:
      bytes.write_int(len(data_array))
    for i in range(len(data_array)):
      write_field_value(bytes, data_array[i], field)
  else:
    write_field_value(bytes, data, field)


def write_field_value(bytes: Bytes, data: Any, field: F):
  match field.type:
    case 'object':
      for f in field.fields:
        if f:
          write_field(bytes, data[f.name], f)
    case 'I':
      bytes.write_long(data)
    case 'H':
      bytes.write_int(data)
    case 'B':
      bytes.write_byte(data)
    case 'str':
      # TODO
      raise Exception(f'TODO implement write_str')
    case _:
      raise Exception(f'unexpected type {field.type}')


def read_section(bytes: Bytes, id: bytes, version: Version, sversion: int) -> Tuple[Any, F]:
  field = get_section_field(bytes, id, version, sversion)
  return read_field(bytes, field), field


# TODO: move all section reading to this new function
def get_section_field(bytes: Bytes, id: bytes, version: Version, sversion: int) -> F:
  match id:
    case SECTION_IDS.COMBOS:
      return get_cmbo_field(bytes, version, sversion)
    case SECTION_IDS.MAPS:
      return get_map_field(bytes, version, sversion)
    case _:
      raise Exception(f'unexpected id {id}')
