from ..field import F
from ..version import Version


def get_tile_field(version: Version, sversion: int) -> F:
    def format_to_data_len(data):
        """
        https://github.com/ArmageddonGames/ZeldaClassic/blob/b56ba20bc6be4a8e4bf01c7c681238d545069baf/src/tiles.cpp#L2579
        """
        format = data['format'] if 'format' in data else 1
        if format == 5:
            return 1024
        if format == 4:
            return 768
        if format >= 1 and format <= 3:
            return 64 << format

        return 256

    tile_field = F(type='object', fields={
        'format': 'B' if version > Version(zelda_version=0x211, build=4) else None,
        'compressed_pixels': F(arr_len=format_to_data_len, type='B'),
    })

    if version >= Version(zelda_version=0x254, build=41):
        tiles_arr_len = 'I'
    else:
        tiles_arr_len = 'H'
    return F(type='array', arr_len=tiles_arr_len, field=tile_field)
