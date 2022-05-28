from ..field import F
from ..version import Version


def get_wpn_field(version: Version, sversion: int) -> F:
    if version.zelda_version < 0x186:
        num_weapons = 64
    if version.zelda_version < 0x185:
        num_weapons = 32
    if version.zelda_version > 0x192:
        num_weapons = 'H'

    weapon_field = F(type='object', fields={
        'tile': 'H',
        'misc': 'B',
        'csets': 'B',
        'frames': 'B',
        'speed': 'B',
        'type': 'B',
        'script': 'H' if sversion >= 7 else None,
        'new_tile': 'I' if sversion >= 7 else None,
    })

    if sversion > 2:
        names_len = num_weapons
        def weapons_len(data): return len(data['names'])
    else:
        weapons_len = num_weapons

    return F(type='object', fields={
        'names': F(arr_len=names_len, type='64s') if sversion > 2 else None,
        'weapons': F(type='array', arr_len=weapons_len, field=weapon_field),
    })
