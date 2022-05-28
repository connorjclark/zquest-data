from ..field import F
from ..version import Version


def get_guy_field(version: Version, sversion: int) -> F:
    if sversion <= 2:
        raise Exception('TODO')

    guy_field = F(type='object', fields={
        'flags': 'I',
        'flags2': 'I',
        'tile': 'I' if sversion >= 36 else 'H',
        'width': 'B',
        'height': 'B',
        's_tile': 'I' if sversion >= 36 else 'H',
        's_width': 'B',
        's_height': 'B',
        'e_tile': 'I' if sversion >= 36 else 'H',
        'e_width': 'B',
        'e_height': 'B',
        'hp': 'H',
        'family': 'H',
        'cset': 'H',
        'anim': 'H',
        'e_anim': 'H',
        'frate': 'H',
        'e_frate': 'H',
        'dp': 'H',
        'wdp': 'H',
        'weapon': 'H',
        'rate': 'H',
        'hrate': 'H',
        'step': 'H',
        'homing': 'H',
        'grumble': 'H',
        'item_set': 'H',
        'misc': F(arr_len=10, type='I' if sversion >= 22 else 'H'),
        'bgsfx': 'H',
        'bosspal': 'H',
        'extend': 'H',
        'defense': F(arr_len=19, type='B') if sversion >= 16 else None,
        'hitsfx': 'B' if sversion >= 18 else None,
        'deadsfx': 'B' if sversion >= 18 else None,

        **({
            'misc11': 'I',
            'misc12': 'I',
        } if sversion >= 22 else {
            'misc11': 'H' if sversion >= 19 else None,
            'misc12': 'H' if sversion >= 19 else None,
        }),

        '_padding1': F(arr_len=41 - 19, type='B') if sversion > 24 else None,
        'txsz': 'I' if sversion > 25 else None,
        'tysz': 'I' if sversion > 25 else None,
        'hxsz': 'I' if sversion > 25 else None,
        'hysz': 'I' if sversion > 25 else None,
        'hzsz': 'I' if sversion > 25 else None,
        '_padding2': F(arr_len=5, type='I') if sversion >= 26 else None,
        'frozen_tile': 'I' if sversion >= 30 else None,
        'frozen_cset': 'I' if sversion >= 30 else None,
        'frozen_clock': 'I' if sversion >= 30 else None,
        'frozen_misc': F(arr_len=10, type='H') if sversion >= 30 else None,

        **({
            'fire_sfx': 'H',
            'misc16': F(arr_len=17, type='I'),
            'movement': F(arr_len=32, type='I'),
            'new_weapon': F(arr_len=32, type='I'),
            'script': 'H',
            'initD': F(arr_len=8, type='I'),
            'initA': F(arr_len=2, type='I'),
        } if sversion >= 34 else {}),

        'editor_flags': 'I' if sversion >= 37 else None,

        **({
            'misc13': 'I',
            'misc14': 'I',
            'misc15': 'I',
        } if sversion >= 38 else {}),

        '_skip': F(arr_len=8 * 65 * 2, type='B') if sversion >= 39 else None,
        'weapon_script': 'H' if sversion >= 40 else None,
        'weapon_initial_d': F(arr_len=8, type='I') if sversion >= 41 else None,
    })

    return F(type='object', fields={
        'names': F(arr_len=512, type='64s') if sversion > 3 else None,
        'guys': F(arr_len=512, type='array', field=guy_field),
    })
