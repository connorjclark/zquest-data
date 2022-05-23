from ..field import F
from ..version import Version


def get_door_field(version: Version, sversion: int) -> F:
    def make_door_field(arr_len: int) -> F:
        return F(type='object', fields={
            'combos': F(arr_len=arr_len, type='H'),
            'csets': F(arr_len=arr_len, type='B'),
        })

    door_set_field = F(type='object', fields={
        'name': '21s',
        '_padding1': 'B' if version.zelda_version < 0x193 else None,
        'up': make_door_field(9 * 4),
        'down': make_door_field(9 * 4),
        'left': make_door_field(9 * 6),
        'right': make_door_field(9 * 6),
        'up_bomb_rubble': make_door_field(2),
        'down_bomb_rubble': make_door_field(2),
        'left_bomb_rubble': make_door_field(3),
        'right_bomb_rubble': make_door_field(3),
        '_padding2': 'B' if version.zelda_version < 0x193 else None,
        'walkthrough': make_door_field(4),
        'flags': F(arr_len=2, type='B'),
        'expansion': F(arr_len=30, type='B') if version.zelda_version < 0x193 else None,
    })

    return F(type='array', arr_len='H', field=door_set_field)
