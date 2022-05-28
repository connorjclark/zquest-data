from ..field import F
from ..version import Version


def get_link_field(version: Version, sversion: int) -> F:
    if sversion >= 6 or sversion == 0:
        raise Exception('TODO')

    sprites_field = F(type='object', fields={
        'tile': 'H',
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
    })
