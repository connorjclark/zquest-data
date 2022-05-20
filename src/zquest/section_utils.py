from __future__ import annotations
import io
from typing import TYPE_CHECKING, Any, Tuple
import types

from .bytes import Bytes
from .field import F
from .sections.cmbo import get_cmbo_field
from .sections.map import get_map_field
from .version import Version

if TYPE_CHECKING:
    from .extract import ZeldaClassicReader

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


def expand_field_shorthand(field: F) -> F:
    """
    Allows for shorthand fields.

    Expands:
      F(arr_len=3, type='I')
    To:
      F(type='array', arr_len=3, field=F(type='I'))
    """
    if field.arr_len != None and field.type != 'array':
        return F(type='array', arr_len=field.arr_len, field=F(type=field.type))
    else:
        return field


def read_field(bytes: Bytes, field: F):
    field = expand_field_shorthand(field)
    match field.type:
        case 'array':
            result = []
            if field.arr_bitmask:
                # TODO: do not hardcode type
                mask = bytes.read_long()
                for i in range(field.arr_len):
                    result.append(read_field(bytes, field.field)
                                  if (mask >> i) & 1 else None)
            else:
                for _ in range(field.arr_len):
                    result.append(read_field(bytes, field.field))
            return result
        case 'object':
            result = {}
            for key, f in field.fields.items():
                if f:
                    result[key] = read_field(bytes, f)
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
    field = expand_field_shorthand(field)
    match field.type:
        case 'array':
            assert type(data) == type([])
            if field.encode_arr_len != None:
                bytes.write_int(len(data))

            if field.arr_bitmask:
                mask = 0
                for i in range(len(data)):
                    if data[i]:
                        mask |= 1 << i
                bytes.write_long(mask)
                for i in range(len(data)):
                    if data[i] != None:
                        write_field(bytes, data[i], field.field)
            else:
                for i in range(len(data)):
                    write_field(bytes, data[i], field.field)
        case 'object':
            for key, f in field.fields.items():
                if f:
                    write_field(bytes, data[key], f)
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