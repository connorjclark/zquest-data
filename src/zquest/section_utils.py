from __future__ import annotations
import io
import re
from typing import TYPE_CHECKING, Any, Tuple
import types
from struct import *

from .bytes import Bytes
from .field import F
from .sections.cmbo import get_cmbo_field
from .sections.map import get_map_field
from .sections.dmap import get_dmap_field
from .sections.tile import get_tile_field
from .sections.door import get_door_field
from .sections.hdr import get_hdr_field
from .sections.item import get_item_field
from .sections.midi import get_midi_field
from .sections.guy import get_guy_field
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


def access_bit(data: bytearray, index: int) -> int:
    base = int(index // 8)
    shift = int(index % 8)
    return (data[base] & (1 << shift)) >> shift


def set_bit(data: bytearray, index: int, on: bool):
    base = int(index // 8)
    shift = int(index % 8)
    if on:
        mask = 1 << shift
        data[base] |= mask
    else:
        mask = ~(1 << shift)
        data[base] &= mask


def expand_field_shorthand(field: F) -> F:
    """
    Allows for shorthand fields.

    Expands:
      'B'
    To:
      F(type='B')

    Expands:
      F(arr_len=3, type='I')
    To:
      F(type='array', arr_len=3, field=F(type='I'))
    """

    if type(field) == str:
        return F(type=field)
    if field.arr_len != None and field.type != 'array' and field.type != 'bytes':
        return F(type='array', arr_len=field.arr_len, field=F(type=field.type, fields=field.fields))
    else:
        return field


def normalize_field(field: F):
    field = expand_field_shorthand(field)

    match field.type:
        case 'array':
            field.field = normalize_field(field.field)
        case 'object':
            fields = {}
            for key, f in field.fields.items():
                if f:
                    fields[key] = normalize_field(f)
            field.fields = fields

    return field


def eval_arr_len(field: F, bytes: Bytes, data: Any):
    arr_len = field.arr_len

    if type(arr_len) == int:
        return arr_len
    elif type(arr_len) == str:
        return bytes.read_packed(arr_len)
    elif callable(arr_len):
        return arr_len(data)
    else:
        raise Exception(f'unhandled type {type(arr_len)}: can\'t handle {arr_len}')


def read_field(bytes: Bytes, field: F, root_data: Any = None):
    match field.type:
        case 'array':
            result = []
            if field.arr_bitmask:
                mask = bytearray(bytes.read(field.arr_bitmask))
                for i in range(field.arr_len):
                    result.append(read_field(bytes, field.field)
                                  if access_bit(mask, i) else None)
            else:
                arr_len = eval_arr_len(field, bytes, root_data)
                for _ in range(arr_len):
                    result.append(read_field(bytes, field.field))
            return result
        case 'object':
            result = {}
            for key, f in field.fields.items():
                result[key] = read_field(bytes, f, root_data if root_data else result)
            return types.SimpleNamespace(**result)
        case 'bytes':
            arr_len = eval_arr_len(field, bytes, root_data)
            return bytes.read(arr_len)
        case _:
            val = bytes.read_packed(field.type)
            if re.match(r'\d+s', field.type):
                val = val.rstrip(b'\x00').decode('utf-8', errors='ignore')
            return val


def serialize(reader: ZeldaClassicReader) -> bytearray:
    reader.b.rewind()
    raw_byte_array = bytearray(reader.b.read(reader.b.length))

    # TODO: Currently doesn't support every section.
    ids = [
        SECTION_IDS.HEADER,
        SECTION_IDS.COMBOS,
        SECTION_IDS.MAPS,
        SECTION_IDS.DMAPS,
        SECTION_IDS.TILES,
        SECTION_IDS.DOORS,
        SECTION_IDS.ITEMS,
        SECTION_IDS.MIDIS,
        SECTION_IDS.GUYS,
    ]
    # Modify in the same order sections were found in the original file,
    # to avoid messing up the offsets of unprocessed sections.
    ids.sort(key=lambda id: -reader.section_offsets[id])

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
        case SECTION_IDS.HEADER:
            write_field(bytes, reader.header, reader.section_fields[id])
        case SECTION_IDS.COMBOS:
            write_field(bytes, reader.combos, reader.section_fields[id])
        case SECTION_IDS.MAPS:
            write_field(bytes, reader.maps, reader.section_fields[id])
        case SECTION_IDS.DMAPS:
            write_field(bytes, reader.dmaps, reader.section_fields[id])
        case SECTION_IDS.TILES:
            write_field(bytes, reader.tiles, reader.section_fields[id])
        case SECTION_IDS.DOORS:
            write_field(bytes, reader.doors, reader.section_fields[id])
        case SECTION_IDS.ITEMS:
            write_field(bytes, reader.items, reader.section_fields[id])
        case SECTION_IDS.MIDIS:
            write_field(bytes, reader.midis, reader.section_fields[id])
        case SECTION_IDS.GUYS:
            write_field(bytes, reader.guys, reader.section_fields[id])
        case _:
            raise Exception(f'unexpected id {id}')

    bytes.f.seek(8)
    bytes.write_long(len(bytes.f.getvalue()) - 12)

    return bytes.f.getvalue()


def write_field(bytes: Bytes, data: Any, field: F):
    match field.type:
        case 'array':
            assert type(data) == type([])
            if type(field.arr_len) == str:
                bytes.write_packed(field.arr_len, len(data))

            if field.arr_bitmask:
                mask = bytearray(field.arr_bitmask)
                for i in range(len(data)):
                    if data[i]:
                        set_bit(mask, i, True)
                bytes.write(mask)
                for i in range(len(data)):
                    if data[i] != None:
                        write_field(bytes, data[i], field.field)
            else:
                for i in range(len(data)):
                    write_field(bytes, data[i], field.field)
        case 'object':
            for key, f in field.fields.items():
                write_field(bytes, getattr(data, key), f)
        case 'bytes':
            if type(field.arr_len) == str:
                bytes.write_packed(field.arr_len, len(data))
            bytes.write(data)
        case _:
            if type(data) == str:
                data = data.encode()
            bytes.write_packed(field.type, data)


def read_section(bytes: Bytes, id: bytes, version: Version, sversion: int) -> Tuple[Any, F]:
    field = get_section_field(id, version, sversion)
    return read_field(bytes, field), field


def validate_field(field: F):
    match field.type:
        case 'array':
            validate_field(field.field)
        case 'object':
            for f in field.fields.values():
                if f:
                    validate_field(f)
        case 'bytes':
            if field.arr_len == None:
                raise Exception('bytes field type must have an arr_len')
        case _:
            # Only explicit byte order notation allowed is '>' and '!' (big-endian).
            # '<' (little-endian) is assumed by default, and not allowed explicitly.
            if field.type[0] == '@' or field.type[0] == '=':
                raise Exception(f'bad field: {field.type}. Don\'t use native byte order')
            if field.type[0] == '<':
                raise Exception(f'bad field: {field.type}. Drop <, little-endian is assumed')
            if not re.match(r'\d+s', field.type) and field.type[0] != '>' and field.type[0] != '!':
                field.type = f'<{field.type}'
            try:
                calcsize(field.type)
            except:
                raise Exception(f'invalid field type: {field.type}')


# TODO: move all section reading to this new function
def get_section_field(id: bytes, version: Version, sversion: int) -> F:
    match id:
        case SECTION_IDS.HEADER:
            field = get_hdr_field(version, sversion)
        case SECTION_IDS.COMBOS:
            field = get_cmbo_field(version, sversion)
        case SECTION_IDS.MAPS:
            field = get_map_field(version, sversion)
        case SECTION_IDS.DMAPS:
            field = get_dmap_field(version, sversion)
        case SECTION_IDS.TILES:
            field = get_tile_field(version, sversion)
        case SECTION_IDS.DOORS:
            field = get_door_field(version, sversion)
        case SECTION_IDS.ITEMS:
            field = get_item_field(version, sversion)
        case SECTION_IDS.MIDIS:
            field = get_midi_field(version, sversion)
        case SECTION_IDS.GUYS:
            field = get_guy_field(version, sversion)
        case _:
            raise Exception(f'unexpected id {id}')

    field = normalize_field(field)
    validate_field(field)
    return field
