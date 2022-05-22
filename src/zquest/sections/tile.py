from ..bytes import Bytes
from ..field import F
from ..version import Version


def tilesize(format: int) -> int:
    """
    https://github.com/ArmageddonGames/ZeldaClassic/blob/b56ba20bc6be4a8e4bf01c7c681238d545069baf/src/tiles.cpp#L2579
    """
    if format == 5:
        return 1024
    if format == 4:
        return 768
    if format >= 1 and format <= 3:
        return 64 << format

    return 256


def get_tile_field(bytes: Bytes, version: Version, sversion: int) -> F:
    def format_to_data_len(data):
        format = data['format'] if 'format' in data else 1
        return tilesize(format)

    tile_field = F(type='object', fields={
        'format': 'B' if version > Version(zelda_version=0x211, build=4) else None,
        'compressed_pixels': F(arr_len=format_to_data_len, type='B'),
    })

    if version >= Version(zelda_version=0x254, build=41):
        tile_count = bytes.read_long()
    else:
        tile_count = bytes.read_int()
    return F(type='array', arr_len=tile_count, encode_arr_len='H', field=tile_field)
