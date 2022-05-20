from ..bytes import Bytes
from ..field import F
from ..version import Version


def get_dmap_field(bytes: Bytes, version: Version, sversion: int) -> F:
    if version < Version(zelda_version=0x192, build=41):
        raise Exception('TODO')

    dmap_field = F(type='object', fields={
        'map': F(type='B'),
        'level': F(type='H' if sversion >= 5 else 'B'),
        'xoff': F(type='b'),
        'compass': F(type='B'),
        'color': F(type='H' if sversion >= 9 else 'B'),
        'midi': F(type='B'),
        'cont': F(type='B'),
        'type': F(type='B'),
        'grid': F(arr_len=8, type='B'),
        'name': F(type='21s'),
        'title': F(type='21s'),
        'intro': F(type='73s'),
        'minimap': F(type='object', arr_len=4, fields={
            'tile': F(type='I' if sversion >= 11 else 'H'),
            'cset': F(type='B'),
        }),
        'tmusic': F(arr_len=56, type='B'),
        'tmusictrack': F(type='B') if sversion >= 2 else None,
        'active_subscreen': F(type='B') if sversion >= 2 else None,
        'passive_subscreen': F(type='B') if sversion >= 2 else None,
        'di': F(arr_len=32, type='B') if sversion >= 3 else None,
        'flags': F(type='I' if sversion >= 6 else 'B') if sversion >= 4 else None,
        '_': F(type='B') if version > Version(zelda_version=0x192, build=41) and version < Version(zelda_version=0x193, build=0) else None,
        'sideview': F(type='B') if sversion >= 10 else None,
        'script': F(type='H') if sversion >= 12 else None,
        'initD': F(arr_len=8, type='I') if sversion >= 12 else None,
        'initDLabel': F(arr_len=8 * 65, type='B') if sversion >= 13 else None,
        'activeSubscript': F(type='H') if sversion >= 14 else None,
        'passiveSubscript': F(type='H') if sversion >= 14 else None,
        'subInitD': F(arr_len=8, type='I') if sversion >= 14 else None,
        'subInitDLabel': F(arr_len=8 * 65, type='B') if sversion >= 14 else None,
    })

    num_dmaps = bytes.read_int()
    return F(type='array', arr_len=num_dmaps, encode_arr_len='H', field=dmap_field)
