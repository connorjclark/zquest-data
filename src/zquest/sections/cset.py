from ..field import F
from ..version import Version


def get_cset_field(version: Version, sversion: int) -> F:
    MAXLEVELS = 512 if sversion >= 3 else 256
    PALNAMESIZE = 17

    # https://github.com/ArmageddonGames/ZeldaClassic/blob/0fddc19a02ccf62c468d9201dd54dcb834b764ca/src/colors.h#L47
    if sversion >= 4:
        color_data_len = (6701 << 4) * 3
    elif version >= Version(zelda_version=0x192, build=73):
        color_data_len = (3373 << 4) * 3
    else:
        color_data_len = (240 << 4) * 3

    cycle_field = F(type='object', fields={
        'first': F(arr_len=3, type='B'),
        'count': F(arr_len=3, type='B'),
        'speed': F(arr_len=3, type='B'),
    })

    return F(type='object', fields={
        'color_data': F(type='bytes', arr_len=color_data_len),
        'palnames': F(arr_len=MAXLEVELS, type=f'{PALNAMESIZE}s'),
        'cycles': F(type='array', arr_len='H', field=cycle_field),
    })
