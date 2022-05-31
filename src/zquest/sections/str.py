from ..field import F
from ..version import Version


def get_str_field(version: Version, sversion: int) -> F:
    if version.zelda_version < 0x193:
        raise Exception('TODO')

    string_field = F(type='object', fields={
        'str': F(type='varstr', str_len='I') if sversion > 8 else F(type=f'{73 if sversion < 2 else 145}s'),
        'next_string': 'H',

        **({
            'tile': 'I' if sversion >= 6 else 'H',
            'cset': 'B',
            'trans': 'B',
            'font': 'B',
        } if sversion >= 2 else {}),

        **({
            'x': 'H',
            'y': 'H',
            'w': 'H',
            'h': 'H',
            'h_space': 'B',
            'v_space': 'B',
            'flags': 'B',
        } if sversion >= 5 else {
            'y': 'B',
        }),

        **({
            'margins': F(arr_len=4, type='B'),
            'portrait_tile': 'I',
            'portrait_cset': 'B',
            'portrait_x': 'B',
            'portrait_y': 'B',
            'portrait_tw': 'B',
            'portrait_th': 'B',
        } if sversion >= 7 else {}),

        'shadow_type': 'B' if sversion >= 8 else None,
        'shadow_color': 'B' if sversion >= 8 else None,
        'sfx': 'B' if sversion >= 2 else None,
        'list_pos': 'H' if sversion > 3 else None,
    })

    return F(arr_len='H', type='array', field=string_field)
