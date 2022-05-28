from ..field import F
from ..version import Version


def get_link_field(version: Version, sversion: int) -> F:
    if sversion == 0:
        raise Exception('TODO')

    sprites_field = F(type='object', fields={
        'tile': 'I' if sversion >= 6 else 'H',
        'flip': 'B',
        'extend': 'B',
    })

    return F(type='object', fields={
        'walk': F(type='array', arr_len=4, field=sprites_field),
        'stab': F(type='array', arr_len=4, field=sprites_field),
        'slash': F(type='array', arr_len=4, field=sprites_field),
        'float': F(type='array', arr_len=4, field=sprites_field),
        'swim': F(type='array', arr_len=4, field=sprites_field),
        'dive': F(type='array', arr_len=4, field=sprites_field),
        'pound': F(type='array', arr_len=4, field=sprites_field),
        'casting': sprites_field,
        'hold': F(type='array', arr_len=2, field=F(type='array', arr_len=3 if sversion > 6 else 2, field=sprites_field)),
        'jump': F(type='array', arr_len=4, field=sprites_field) if sversion > 2 else None,
        'charge': F(type='array', arr_len=4, field=sprites_field) if sversion > 3 else None,
        'link_swim_speed': 'B' if sversion > 4 else None,

        **({
            'frozen': F(type='array', arr_len=4, field=sprites_field),
            'frozen_water': F(type='array', arr_len=4, field=sprites_field),
            'on_fire': F(type='array', arr_len=4, field=sprites_field),
            'on_fire_water': F(type='array', arr_len=4, field=sprites_field),
            'digging': F(type='array', arr_len=4, field=sprites_field),
            'using_rod': F(type='array', arr_len=4, field=sprites_field),
            'using_cane': F(type='array', arr_len=4, field=sprites_field),
            'pushing': F(type='array', arr_len=4, field=sprites_field),
            'lifting': F(type='array', arr_len=4, field=sprites_field),
            'lifting_heavy': F(type='array', arr_len=4, field=sprites_field),
            'stunned': F(type='array', arr_len=4, field=sprites_field),
            'stunned_water': F(type='array', arr_len=4, field=sprites_field),
            'drowning': F(type='array', arr_len=4, field=sprites_field),
            'drowning_lava': F(type='array', arr_len=4, field=sprites_field),
            'falling': F(type='array', arr_len=4, field=sprites_field),
            'shocked': F(type='array', arr_len=4, field=sprites_field),
            'shocked_water': F(type='array', arr_len=4, field=sprites_field),
            'pull_sword': F(type='array', arr_len=4, field=sprites_field),
            'reading': F(type='array', arr_len=4, field=sprites_field),
            'slash_180': F(type='array', arr_len=4, field=sprites_field),
            'slash_z4': F(type='array', arr_len=4, field=sprites_field),
            'dash': F(type='array', arr_len=4, field=sprites_field),
            'bonk': F(type='array', arr_len=4, field=sprites_field),
            'medallions': F(type='array', arr_len=3, field=sprites_field),
        } if sversion > 6 else {}),

        'sideswim': F(type='array', arr_len=4, field=sprites_field) if sversion >= 8 else None,

        **({
            'sideswimslash': F(type='array', arr_len=4, field=sprites_field),
            'sideswimstab': F(type='array', arr_len=4, field=sprites_field),
            'sideswimpound': F(type='array', arr_len=4, field=sprites_field),
            'sideswimcharge': F(type='array', arr_len=4, field=sprites_field),
        } if sversion > 9 else {}),

        'hammer_offsets': F(arr_len=4, type='I') if sversion > 10 else None,
        'sideswimhold': F(type='array', arr_len=3, field=sprites_field) if sversion > 11 else None,
        'sideswimcasting': sprites_field if sversion > 12 else None,
        'sidedrowning': F(type='array', arr_len=4, field=sprites_field) if sversion > 13 else None,
        'revslash': F(type='array', arr_len=4, field=sprites_field) if sversion > 14 else None,
        'defence': F(arr_len=146, type='B') if sversion > 7 else None,
    })
