from ..field import F
from ..version import Version


def get_init_field(version: Version, sversion: int) -> F:
    if version <= Version(zelda_version=0x192, build=26):
        raise Exception('TODO')
    if sversion < 15:
        raise Exception('TODO')

    extended_arrays = sversion > 12 or version == Version(zelda_version=0x211, build=18)
    return F(type='object', fields={
        'items': F(arr_len=256, type='B') if sversion >= 10 else None,
        '_padding1': F(arr_len=6, type='B') if sversion < 10 else None,
        '_padding2': F(arr_len=7, type='B') if sversion < 10 else None,
        '_padding3': F(arr_len=5, type='B') if sversion < 10 else None,
        'bombs': 'B' if sversion < 29 else None,
        'super_bombs': 'B' if sversion < 29 else None,
        '_padding4': F(arr_len=10, type='B') if sversion < 10 and version > Version(zelda_version=0x192, build=173) else None,
        '_padding5': F(arr_len=10, type='B') if sversion < 10 and version.zelda_version == 0x192 and version.build > 173 else None,
        'hc': 'B',
        'start_heart': 'H' if sversion >= 14 else 'B',
        'continue_heart': 'H' if sversion >= 14 else 'B',
        'hcp': 'B',
        'hcp_per_hc': 'B' if sversion >= 14 else None,
        'max_bombs': 'B' if sversion < 29 else None,
        'keys': 'B',
        'rupees': 'H',
        'triforce': 'B',
        'map': F(arr_len=64 if extended_arrays else 32, type='B'),
        'compass': F(arr_len=64 if extended_arrays else 32, type='B'),
        'boss_keys': F(arr_len=64 if extended_arrays else 32, type='B') if version > Version(zelda_version=0x192, build=173) else None,
        'misc': F(arr_len=16, type='B'),
        'sword_hearts': F(arr_len=4, type='B') if sversion < 15 else None,
        'last_map': 'B',
        'last_screen': 'B',
        'max_magic': 'H' if sversion >= 14 else 'B',
        'magic': 'H' if sversion >= 14 else 'B',
        'beam_hearts': F(arr_len=4, type='B') if sversion < 15 else None,
        'beam_percent': 'B' if sversion < 15 else None,
        'bomb_ratio': 'B' if sversion >= 15 else None,
        'bomb_power': F(arr_len=4, type='H' if sversion >= 14 else 'B') if sversion < 15 else None,
        'hookshot_links': 'B' if sversion < 15 else None,
        'hookshot_length': 'B' if sversion < 15 and sversion > 6 else None,
        'longshot_links': 'B' if sversion < 15 and sversion > 6 else None,
        'longshot_length': 'B' if sversion < 15 and sversion > 6 else None,
        'msg_more_x': 'B',
        'msg_more_y': 'B',
        'subscreen': 'B',
        'start_dmap': F(type='H' if sversion > 10 else 'B') if version > Version(zelda_version=0x192, build=173) else None,
        'link_animation_style': 'B' if version > Version(zelda_version=0x192, build=173) else None,
        'arrows': 'B' if sversion > 1 and sversion < 29 else None,
        'max_arrows': 'B' if sversion > 1 and sversion < 29 else None,
        'level_keys': F(arr_len=512 if sversion > 10 else 256, type='B') if sversion > 2 and sversion < 29 else None,

        **({
            'ss_grid_x': 'H',
            'ss_grid_y': 'H',
            'ss_grid_xofs': 'H',
            'ss_grid_yofs': 'H',
            'ss_grid_color': 'H',
            'ss_bbox_1_color': 'H',
            'ss_bbox_2_color': 'H',
            'ss_flags': 'H',
        } if sversion > 3 else {}),

        'subscreen_style': 'B' if sversion > 6 else None,
        'use_custom_sfx': 'B' if sversion > 7 else None,
        'max_rupees': 'H' if sversion > 8 else None,
        'max_keys': 'H' if sversion > 8 else None,

        **({
            'gravity': 'B',
            'terminalv': 'H',
            'msg_speed': 'B',
            'transition_type': 'B',
            'jump_hero_layer_threshold': 'B',
        } if sversion > 16 else {}),

        'msg_more_is_offset': 'B' if sversion > 17 else None,

        **({
            'bombs': 'H',
            'super_bombs': 'H',
            'max_bombs': 'H',
            'max_sbombs': 'H',
            'arrows': 'H',
            'max_arrows': 'H',
        } if sversion >= 19 else {}),

        'hero_step': 'H' if sversion >= 20 else None,
        'subscr_speed': 'H' if sversion >= 21 else None,

        **({
            'hp_per_heart': 'B',
            'magic_per_block': 'B',
            'hero_damage_multiplier': 'B',
            'ene_damage_multiplier': 'B',
        } if sversion > 21 else {}),

        **({
            'scr_cnt': F(arr_len=25, type='H'),
            'scr_max_cnt': F(arr_len=25, type='H'),
        } if sversion > 22 else {}),

        **({
            'dither_type': 'B',
            'dither_arg': 'B',
            'dither_percent': 'B',
            'def_lightrad': 'B',
            'transdark_percent': 'B',
        } if sversion > 23 else {}),

        'dark_color': 'B' if sversion > 24 else None,
        'gravity_2': 'I' if sversion > 25 else None,
        'swim_gravity': 'I' if sversion > 25 else None,

        **({
            'hero_sideswim_up_step': 'H',
            'hero_sideswim_side_step': 'H',
            'hero_sideswim_down_step': 'H',
        } if sversion > 26 else {}),

        'exit_water_jump': 'I' if sversion > 27 else None,
        'bunny_ltm': 'I' if sversion > 29 else None,
        'switch_hook_style': 'B' if sversion > 30 else None,
        'magic_drain_rate': 'B' if sversion > 31 else None,
    })
