from ..field import F
from ..version import Version


def get_item_field(version: Version, sversion: int) -> F:
    if sversion <= 1:
        raise Exception(f'item section is too old')

    if version.zelda_version > 0x192:
        num_items = 'H'
    elif version.zelda_version < 0x186:
        num_items = 64
    else:
        num_items = 256

    item_field = F(type='object', fields={
        'tile': F(type='I' if sversion > 35 else 'H'),
        'misc': F(type='B'),
        'csets': F(type='B'),  # ffffcccc (f:flash cset, c:cset)
        'frames': F(type='B'),
        'speed': F(type='B'),
        'delay': F(type='B'),
        'padding_1': F(type='B') if version.zelda_version < 0x193 else None,
        'ltm': F(type='I'),
        'padding_2': F(type='12s') if version.zelda_version < 0x193 else None,

        **({
            'family': F(type='I' if sversion >= 31 else 'B'),
            'family_type': F(type='B'),
            'power': F(type='I' if sversion >= 31 else 'B') if sversion > 5 else None,
            'flags': F(type='I' if sversion >= 41 else 'H') if sversion > 5 else None,
            'flags_item_gamedata': F(type='B') if sversion <= 5 else None,
            'script': F(type='H'),
            'count': F(type='B'),
            'amount': F(type='H'),
            'collect_script': F(type='H'),
            'set_max': F(type='H'),
            'max': F(type='H'),
            'play_sound': F(type='B'),
            'initial_d': F(arr_len=8, type='I'),
            'initial_a': F(arr_len=2, type='B'),
        } if sversion > 1 else {}),

        **({
            'flags_item_edible': F(type='B') if sversion <= 5 else None,

            'wpn': F(arr_len=10 if sversion >= 15 else 4, type='B') if sversion > 5 else None,
            'pickup_hearts': F(type='B') if sversion > 5 else None,
            'misc_1': F(type='I' if sversion >= 15 else 'H') if sversion > 5 else None,
            'misc_2': F(type='I' if sversion >= 15 else 'H') if sversion > 5 else None,
            'magic': F(type='B') if sversion > 5 else None,
        } if sversion > 4 else {}),

        **({
            'misc_3': F(type='H') if sversion < 15 else None,
            'misc_4': F(type='H') if sversion < 15 else None,

            'misc_3': F(type='I') if sversion >= 15 else None,
            'misc_4': F(type='I') if sversion >= 15 else None,
            'misc_5': F(type='I') if sversion >= 15 else None,
            'misc_6': F(type='I') if sversion >= 15 else None,
            'misc_7': F(type='I') if sversion >= 15 else None,
            'misc_8': F(type='I') if sversion >= 15 else None,
            'misc_9': F(type='I') if sversion >= 15 else None,
            'misc_10': F(type='I') if sversion >= 15 else None,

            'use_sound': F(type='B'),
        } if sversion >= 12 else {}),

        **({
            'use_weapon': F(type='B'),
            'use_defense': F(type='B'),
            'weapon_range': F(type='I'),
            'weapon_duration': F(type='I'),
            'weapon_pattern': F(arr_len=10, type='I'),
        } if sversion >= 26 else {}),

        **({
            'duplicates': F(type='I'),
            'weapon_initial_d': F(arr_len=8, type='I'),
            'weapon_initial_a': F(arr_len=2, type='B'),
            'draw_layer': F(type='B'),
            'hxofs': F(type='I'),
            'hyofs': F(type='I'),
            # TODO
            'skip_1': F(arr_len=16, type='I'),
            'skip_2': F(arr_len=1, type='H'),
        } if sversion >= 27 else {}),

        **({
            'override_flags': F(type='I'),
            'tile_w': F(type='I'),
            'tile_h': F(type='I'),
        } if sversion >= 28 else {}),

        **({
            'weapon_override_flags': F(type='I'),
            'weapon_tile_w': F(type='I'),
            'weapon_tile_h': F(type='I'),
        } if sversion >= 29 else {}),

        'pickup': F(type='I') if sversion >= 30 else None,
        'p_string': F(type='H') if sversion >= 32 else None,
        'pickup_string_flags': F(type='H') if sversion >= 33 else None,
        'cost_counter': F(type='B') if sversion >= 34 else None,

        **({
            # TODO
            'skip_3': F(arr_len=8 * (65 * 3 + 4), type='B'),
            'sprite_initial_a': F(arr_len=2, type='B'),
            'sprite_script': F(type='H'),
        } if sversion >= 44 else {}),
    })

    return F(type='object', fields={
        'names': F(arr_len=num_items, type='64s') if sversion > 1 else None,
        'items': F(type='array', arr_len=lambda data: len(data['names']), field=item_field),
    })
