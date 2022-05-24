from ..field import F
from ..version import Version


def get_dmap_field(version: Version, sversion: int) -> F:
    if version < Version(zelda_version=0x192, build=41):
        raise Exception('TODO')

    dmap_field = F(type='object', fields={
        'map': 'B',
        'level': 'H' if sversion >= 5 else 'B',
        'xoff': 'b',
        'compass': 'B',
        'color': 'H' if sversion >= 9 else 'B',
        'midi': 'B',
        'cont': 'B',
        'type': 'B',
        'grid': F(arr_len=8, type='B'),
        'name': '21s',
        'title': '21s',
        'intro': '73s',
        'minimap': F(type='object', arr_len=4, fields={
            'tile': 'I' if sversion >= 11 else 'H',
            'cset': 'B',
        }),
        'tmusic': F(arr_len=56, type='B'),
        'tmusictrack': 'B' if sversion >= 2 else None,
        'active_subscreen': 'B' if sversion >= 2 else None,
        'passive_subscreen': 'B' if sversion >= 2 else None,
        'di': F(arr_len=32, type='B') if sversion >= 3 else None,
        'flags': F(type='I' if sversion >= 6 else 'B') if sversion >= 4 else None,
        '_': 'B' if version > Version(zelda_version=0x192, build=41) and version < Version(zelda_version=0x193, build=0) else None,
        'sideview': 'B' if sversion >= 10 else None,
        'script': 'H' if sversion >= 12 else None,
        'init_d': F(arr_len=8, type='I') if sversion >= 12 else None,
        'init_d_label': F(arr_len=8 * 65, type='B') if sversion >= 13 else None,
        'active_subscript': 'H' if sversion >= 14 else None,
        'passive_subscript': 'H' if sversion >= 14 else None,
        'sub_init_d': F(arr_len=8, type='I') if sversion >= 14 else None,
        'sub_init_d_label': F(arr_len=8 * 65, type='B') if sversion >= 14 else None,
    })

    return F(type='array', arr_len='H', field=dmap_field)
