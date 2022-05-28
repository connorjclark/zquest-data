from ..field import F
from ..version import Version


def get_cmbo_field(version: Version, sversion: int) -> F:
    if version.zelda_version < 0x174:
        num_combos = 1024
    elif version.zelda_version < 0x191:
        num_combos = 2048
    else:
        num_combos = 'H'

    combo_field = F(type='object', fields={
        'tile': 'I' if sversion >= 11 else 'H',
        'flip': 'B',
        'walk': 'B',
        'type': 'B',
        'csets': 'B',
        '_padding1': '2s' if version.zelda_version < 0x193 else None,
        '_padding2': '16s' if version.zelda_version == 0x191 else None,
        'frames': 'B',
        'speed': 'B',
        'nextcombo': 'H',
        'nextcset': 'B',
        'flag': 'B' if sversion >= 3 else None,
        'skipanim': 'B' if sversion >= 4 else None,
        'nexttimer': 'H' if sversion >= 4 else None,
        'skipanimy': 'B' if sversion >= 5 else None,
        'animflags': 'B' if sversion >= 6 else None,
        'attributes': F(arr_len=4, type='I') if sversion >= 8 else None,
        'usr_flags': 'I' if sversion >= 8 else None,
        'gen_flags': 'H' if sversion >= 20 else None,
        'trigger_flags': F(arr_len=3 if sversion >= 10 else 2, type='I') if sversion >= 9 else None,
        'trigger_level': 'I' if sversion >= 9 else None,
        'trigger_btn': 'B' if sversion >= 22 else None,
        'label': F(arr_len=11, type='B') if sversion >= 12 else None,
        '_padding3': '11s' if version.zelda_version < 0x193 else None,
        'attribytes': F(arr_len=4, type='B') if sversion >= 13 else None,
        'script': 'H' if sversion >= 14 else None,
        'initd': F(arr_len=2, type='I') if sversion >= 14 else None,
        'o_tile': 'I' if sversion >= 15 else None,
        'cur_frame': 'B' if sversion >= 15 else None,
        'aclk': 'B' if sversion >= 15 else None,
        'more_attribytes': F(arr_len=4, type='B') if sversion >= 17 else None,
        'more_attrishorts': F(arr_len=8, type='H') if sversion >= 17 else None,
    })

    return F(type='array', arr_len=num_combos, field=combo_field)
