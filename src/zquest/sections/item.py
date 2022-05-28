from ..field import F
from ..version import Version


def get_item_field(version: Version, sversion: int) -> F:
    if version.zelda_version > 0x192:
        num_items = 'H'
    elif version.zelda_version < 0x186:
        num_items = 64
    else:
        num_items = 256

    item_field = F(type='object', fields={
        'tile': F(type='I' if sversion > 35 else 'H'),
        'misc': 'B',
        'csets': 'B',  # ffffcccc (f:flash cset, c:cset)
        'frames': 'B',
        'speed': 'B',
        'delay': 'B',
        'padding_1': 'B' if version.zelda_version < 0x193 else None,
        'ltm': 'I',
        'padding_2': F(type='12s') if version.zelda_version < 0x193 else None,

        **({
            'family': F(type='I' if sversion >= 31 else 'B'),
            'family_type': 'B',
            'power': F(type='I' if sversion >= 31 else 'B') if sversion > 5 else None,
            'flags': F(type='I' if sversion >= 41 else 'H') if sversion > 5 else None,
            'flags_item_gamedata': 'B' if sversion <= 5 else None,
            'script': 'H',
            'count': 'B',
            'amount': 'H',
            'collect_script': 'H',
            'set_max': 'H',
            'max': 'H',
            'play_sound': 'B',
            'initial_d': F(arr_len=8, type='I'),
            'initial_a': F(arr_len=2, type='B'),
        } if sversion > 1 else {}),

        **({
            'flags_item_edible': 'B' if sversion <= 5 else None,

            'wpn': F(arr_len=10 if sversion >= 15 else 4, type='B') if sversion > 5 else None,
            'pickup_hearts': 'B' if sversion > 5 else None,
            'misc_1': F(type='I' if sversion >= 15 else 'H') if sversion > 5 else None,
            'misc_2': F(type='I' if sversion >= 15 else 'H') if sversion > 5 else None,
            'magic': 'B' if sversion > 5 else None,
        } if sversion > 4 else {}),

        **({
            'misc_3': 'H' if sversion < 15 else None,
            'misc_4': 'H' if sversion < 15 else None,

            'misc_3': 'I' if sversion >= 15 else None,
            'misc_4': 'I' if sversion >= 15 else None,
            'misc_5': 'I' if sversion >= 15 else None,
            'misc_6': 'I' if sversion >= 15 else None,
            'misc_7': 'I' if sversion >= 15 else None,
            'misc_8': 'I' if sversion >= 15 else None,
            'misc_9': 'I' if sversion >= 15 else None,
            'misc_10': 'I' if sversion >= 15 else None,

            'use_sound': 'B',
        } if sversion >= 12 else {}),

        **({
            'use_weapon': 'B',
            'use_defense': 'B',
            'weapon_range': 'I',
            'weapon_duration': 'I',
            'weapon_pattern': F(arr_len=10, type='I'),
        } if sversion >= 26 else {}),

        **({
            'duplicates': 'I',
            'weapon_initial_d': F(arr_len=8, type='I'),
            'weapon_initial_a': F(arr_len=2, type='B'),
            'draw_layer': 'B',
            'hxofs': 'I',
            'hyofs': 'I',
            # TODO
            'skip_1': F(arr_len=16, type='I'),
            'skip_2': F(arr_len=1, type='H'),
        } if sversion >= 27 else {}),

        **({
            'override_flags': 'I',
            'tile_w': 'I',
            'tile_h': 'I',
        } if sversion >= 28 else {}),

        **({
            'weapon_override_flags': 'I',
            'weapon_tile_w': 'I',
            'weapon_tile_h': 'I',
        } if sversion >= 29 else {}),

        'pickup': 'I' if sversion >= 30 else None,
        'p_string': 'H' if sversion >= 32 else None,
        'pickup_string_flags': 'H' if sversion >= 33 else None,
        'cost_counter': F(arr_len=2 if sversion >= 53 else 1, type='B') if sversion >= 34 else None,

        **({
            # TODO
            'skip_3': F(arr_len=8 * (65 * 3 + 4), type='B'),
            'sprite_initial_a': F(arr_len=2, type='B'),
            'sprite_script': 'H',
        } if sversion >= 44 else {}),

        'pickup_flag': 'B' if sversion >= 48 else None,
    })

    if sversion > 1:
        names_len = num_items
        def items_len(data): return len(data['names'])
    else:
        items_len = num_items

    return F(type='object', fields={
        'names': F(arr_len=names_len, type='64s') if sversion > 1 else None,
        'items': F(type='array', arr_len=items_len, field=item_field),
    })
