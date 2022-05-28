from ..field import F
from ..version import Version


def get_map_field(version: Version, sversion: int) -> F:
    extended_arrays = version > Version(zelda_version=0x211, build=7)
    common_arr_len = 4 if extended_arrays else 1

    if version < Version(zelda_version=0x192, build=137):
        num_secret_combos = 20
    elif version.zelda_version == 0x192 and version.build < 154:
        num_secret_combos = 256
    else:
        num_secret_combos = 128

    if version < Version(zelda_version=0x192, build=137):
        num_screens = 132
    else:
        num_screens = 136

    screen_field = F(type='object', fields={
        'valid': 'B',
        'guy': 'B',
        'str': 'H' if version > Version(zelda_version=0x192, build=146) else 'B',
        'room': 'B',
        'item': 'B',
        'has_item': 'B' if version >= Version(zelda_version=0x211, build=14) else None,
        '_padding0': 'B' if version < Version(zelda_version=0x192, build=154) else None,
        'tile_warp_type': F(arr_len=common_arr_len, type='B'),
        'door_combo_set': 'H' if version > Version(zelda_version=0x192, build=153) else None,
        'warp_return_x': F(arr_len=common_arr_len, type='B'),
        'warp_return_y': F(arr_len=common_arr_len, type='B'),
        'warp_return_c': F(type='H' if sversion >= 18 else 'B') if version > Version(zelda_version=0x211, build=7) else None,
        'stair_x': 'B',
        'stair_y': 'B',
        'item_x': 'B',
        'item_y': 'B',
        'color': 'H' if sversion > 15 else 'B',
        'enemy_flags': 'B',
        'doors': F(arr_len=4, type='B'),
        'tile_warp_dmap': F(arr_len=common_arr_len, type='H' if sversion > 11 else 'B'),
        'tile_warp_screen': F(arr_len=common_arr_len, type='B'),
        'tile_warp_overlay_flags': 'B' if sversion >= 15 else None,
        'exit_dir': 'B',
        '_padding1': 'B' if version.zelda_version < 0x193 else None,
        '_padding2': 'B' if version > Version(zelda_version=0x192, build=145) and version < Version(zelda_version=0x192, build=154) else None,
        'enemies': F(arr_len=10, type='H' if version >= Version(zelda_version=0x192, build=10) else 'B'),
        'pattern': 'B',
        'side_warp_type': F(arr_len=common_arr_len, type='B'),
        'side_warp_overlay_flags': 'B' if sversion >= 15 else None,
        'warp_arrival_x': 'B',
        'warp_arrival_y': 'B',
        'path': F(arr_len=4, type='B'),
        'side_warp_screen': F(arr_len=common_arr_len, type='B'),
        'side_warp_dmap': F(arr_len=common_arr_len, type='H' if sversion > 11 else 'B'),
        'side_warp_index': 'B' if version > Version(zelda_version=0x211, build=7) else None,
        'under_combo': 'H',
        'old_cpage': 'B' if version.zelda_version < 0x193 else None,
        'under_cset': 'B',
        'catch_all': 'H',
        'flags': 'B',
        'flags2': 'B',
        'flags3': 'B',
        'flags4': 'B' if version > Version(zelda_version=0x211, build=1) else None,
        'flags5': 'B' if version > Version(zelda_version=0x211, build=7) else None,
        'noreset': 'H' if version > Version(zelda_version=0x211, build=7) else None,
        'nocarry': 'H' if version > Version(zelda_version=0x211, build=7) else None,
        'flags6': 'B' if version > Version(zelda_version=0x211, build=9) else None,
        'flags7': 'B' if sversion > 5 else None,
        'flags8': 'B' if sversion > 5 else None,
        'flags9': 'B' if sversion > 5 else None,
        'flags10': 'B' if sversion > 5 else None,
        'csensitive': 'B' if sversion > 5 else None,
        'ocean_sfx': 'B' if sversion >= 14 else None,
        'boss_sfx': 'B' if sversion >= 14 else None,
        'secret_sfx': 'B' if sversion >= 14 else None,
        'hold_up_sfx': 'B' if sversion >= 15 else None,

        # this is a weird one for older versions
        'layer_map': F(arr_len=6, type='B') if version > Version(zelda_version=0x192, build=97) else None,
        'layer_screen': F(arr_len=6, type='B') if version > Version(zelda_version=0x192, build=97) else None,
        '_skip': F(arr_len=4, type='B') if version > Version(zelda_version=0x192, build=23) and version < Version(zelda_version=0x192, build=98) else None,

        'layer_opacity': F(arr_len=6, type='B') if version > Version(zelda_version=0x192, build=149) else None,
        '_padding3': 'B' if version == Version(zelda_version=0x192, build=153) else None,
        'timed_warp_tics': 'H' if version > Version(zelda_version=0x192, build=153) else None,
        'next_map': 'B' if version > Version(zelda_version=0x211, build=2) else None,
        'next_screen': 'B' if version > Version(zelda_version=0x211, build=2) else None,
        'secret_combos': F(arr_len=num_secret_combos, type='B' if version < Version(zelda_version=0x192, build=154) else 'H'),
        'secret_csets': F(arr_len=128, type='B') if version > Version(zelda_version=0x192, build=153) else None,
        'secret_flags': F(arr_len=128, type='B') if version > Version(zelda_version=0x192, build=153) else None,
        '_padding4': 'B' if version > Version(zelda_version=0x192, build=97) and version < Version(zelda_version=0x192, build=154) else None,
        'data': F(arr_len=16 * 11, type='H'),
        'sflag': F(arr_len=16 * 11, type='B') if version > Version(zelda_version=0x192, build=20) else None,
        'cset': F(arr_len=16 * 11, type='B') if version > Version(zelda_version=0x192, build=97) else None,
        'screen_midi': 'H' if sversion > 4 else None,
        'lens_layer': 'B' if sversion >= 17 else None,

        **({
            'ff': F(type='array', arr_len=32, arr_bitmask=4, field=F(type='object', fields={
                'data': 'H',
                'cset': 'B',
                'delay': 'H',
                'x': 'I' if sversion >= 9 else None,
                'y': 'I' if sversion >= 9 else None,
                'x_delta': 'I' if sversion >= 9 else None,
                'y_delta': 'I' if sversion >= 9 else None,
                'x_delta_2': 'I' if sversion >= 9 else None,
                'y_delta_2': 'I' if sversion >= 9 else None,
                'link': 'B',
                'width': 'B' if sversion > 7 else None,
                'height': 'B' if sversion > 7 else None,
                'flags': 'I' if sversion > 7 else None,
                'script': 'H' if sversion > 9 else None,
                'initd': F(arr_len=8, type='I') if sversion > 10 else None,
                'inita': F(arr_len=2, type='B') if sversion > 10 else None,
            })),
        } if sversion > 6 else {}),

        'npc_strings': F(arr_len=10, type='I') if sversion >= 19 and version.zelda_version > 0x253 else None,
        'new_items': F(arr_len=10, type='H') if sversion >= 19 and version.zelda_version > 0x253 else None,
        'newitem_x': F(arr_len=10, type='H') if sversion >= 19 and version.zelda_version > 0x253 else None,
        'newitem_y': F(arr_len=10, type='H') if sversion >= 19 and version.zelda_version > 0x253 else None,
        'script': 'H' if sversion >= 20 and version.zelda_version > 0x253 else None,
        'screen_initd': F(arr_len=8, type='I') if sversion >= 20 and version.zelda_version > 0x253 else None,
        'preload_script': 'B' if sversion >= 21 and version.zelda_version > 0x253 else None,
        'hide_layers': 'B' if sversion >= 22 and version.zelda_version > 0x253 else None,
        'hide_script_layers': 'B' if sversion >= 22 and version.zelda_version > 0x253 else None,
    })

    map_field = F(type='object', fields={
        'screens': F(type='array', arr_len=num_screens, field=screen_field),
    })

    return F(type='array', arr_len='H', field=map_field)
