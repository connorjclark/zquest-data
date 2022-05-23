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
        'hasItem': 'B' if version >= Version(zelda_version=0x211, build=14) else None,
        '_padding0': 'B' if version < Version(zelda_version=0x192, build=154) else None,
        'tileWarpType': F(arr_len=common_arr_len, type='B'),
        'doorComboSet': 'H' if version > Version(zelda_version=0x192, build=153) else None,
        'warpReturnX': F(arr_len=common_arr_len, type='B'),
        'warpReturnY': F(arr_len=common_arr_len, type='B'),
        'warpReturnC': F(type='H' if sversion >= 18 else 'B') if version > Version(zelda_version=0x211, build=7) else None,
        'stairX': 'B',
        'stairY': 'B',
        'itemX': 'B',
        'itemY': 'B',
        'color': 'H' if sversion > 15 else 'B',
        'enemyFlags': 'B',
        'doors': F(arr_len=4, type='B'),
        'tileWarpDmap': F(arr_len=common_arr_len, type='H' if sversion > 11 else 'B'),
        'tileWarpScreen': F(arr_len=common_arr_len, type='B'),
        'tileWarpOverlayFlags': 'B' if sversion >= 15 else None,
        'exitDir': 'B',
        '_padding1': 'B' if version.zelda_version < 0x193 else None,
        '_padding2': 'B' if version > Version(zelda_version=0x192, build=145) and version < Version(zelda_version=0x192, build=154) else None,
        'enemies': F(arr_len=10, type='H' if version >= Version(zelda_version=0x192, build=10) else 'B'),
        'pattern': 'B',
        'sideWarpType': F(arr_len=common_arr_len, type='B'),
        'sideWarpOverlayFlags': 'B' if sversion >= 15 else None,
        'warpArrivalX': 'B',
        'warpArrivalY': 'B',
        'path': F(arr_len=4, type='B'),
        'sideWarpScreen': F(arr_len=common_arr_len, type='B'),
        'sideWarpDmap': F(arr_len=common_arr_len, type='H' if sversion > 11 else 'B'),
        'sideWarpIndex': 'B' if version > Version(zelda_version=0x211, build=7) else None,
        'underCombo': 'H',
        'old_cpage': 'B' if version.zelda_version < 0x193 else None,
        'underCset': 'B',
        'catchAll': 'H',
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
        'oceanSfx': 'B' if sversion >= 14 else None,
        'bossSfx': 'B' if sversion >= 14 else None,
        'secretSfx': 'B' if sversion >= 14 else None,
        'holdUpSfx': 'B' if sversion >= 15 else None,

        # this is a weird one for older versions
        'layerMap': F(arr_len=6, type='B') if version > Version(zelda_version=0x192, build=97) else None,
        'layerScreen': F(arr_len=6, type='B') if version > Version(zelda_version=0x192, build=97) else None,
        '_skip': F(arr_len=4, type='B') if version > Version(zelda_version=0x192, build=23) and version < Version(zelda_version=0x192, build=98) else None,

        'layerOpacity': F(arr_len=6, type='B') if version > Version(zelda_version=0x192, build=149) else None,
        '_padding3': 'B' if version == Version(zelda_version=0x192, build=153) else None,
        'timedWarpTics': 'H' if version > Version(zelda_version=0x192, build=153) else None,
        'nextMap': 'B' if version > Version(zelda_version=0x211, build=2) else None,
        'nextScreen': 'B' if version > Version(zelda_version=0x211, build=2) else None,
        'secretCombos': F(arr_len=num_secret_combos, type='B' if version < Version(zelda_version=0x192, build=154) else 'H'),
        'secretCsets': F(arr_len=128, type='B') if version > Version(zelda_version=0x192, build=153) else None,
        'secretFlags': F(arr_len=128, type='B') if version > Version(zelda_version=0x192, build=153) else None,
        '_padding4': 'B' if version > Version(zelda_version=0x192, build=97) and version < Version(zelda_version=0x192, build=154) else None,
        'data': F(arr_len=16 * 11, type='H'),
        'sflag': F(arr_len=16 * 11, type='B') if version > Version(zelda_version=0x192, build=20) else None,
        'cset': F(arr_len=16 * 11, type='B') if version > Version(zelda_version=0x192, build=97) else None,
        'screenMidi': 'H' if sversion > 4 else None,
        'lensLayer': 'B' if sversion >= 17 else None,

        **({
            'ff': F(type='array', arr_len=32, arr_bitmask=True, field=F(type='object', fields={
                'data': 'H',
                'cset': 'B',
                'delay': 'H',
                'x': 'I' if sversion >= 9 else None,
                'y': 'I' if sversion >= 9 else None,
                'xDelta': 'I' if sversion >= 9 else None,
                'yDelta': 'I' if sversion >= 9 else None,
                'xDelta2': 'I' if sversion >= 9 else None,
                'yDelta2': 'I' if sversion >= 9 else None,
                'link': 'B',
                'width': 'B' if sversion > 7 else None,
                'height': 'B' if sversion > 7 else None,
                'flags': 'I' if sversion > 7 else None,
                'script': 'H' if sversion > 9 else None,
                'initd': F(arr_len=8, type='I') if sversion > 10 else None,
                'inita': F(arr_len=2, type='B') if sversion > 10 else None,
            })),
        } if sversion > 6 else {}),

        'npcStrings': F(arr_len=10, type='I') if sversion >= 19 and version.zelda_version > 0x253 else None,
        'newItems': F(arr_len=10, type='H') if sversion >= 19 and version.zelda_version > 0x253 else None,
        'newItemX': F(arr_len=10, type='H') if sversion >= 19 and version.zelda_version > 0x253 else None,
        'newItemY': F(arr_len=10, type='H') if sversion >= 19 and version.zelda_version > 0x253 else None,
        'script': 'H' if sversion >= 20 and version.zelda_version > 0x253 else None,
        'screenInitd': F(arr_len=8, type='I') if sversion >= 20 and version.zelda_version > 0x253 else None,
        'preloadScript': 'B' if sversion >= 21 and version.zelda_version > 0x253 else None,
        'hideLayers': 'B' if sversion >= 22 and version.zelda_version > 0x253 else None,
        'hideScriptLayers': 'B' if sversion >= 22 and version.zelda_version > 0x253 else None,
    })

    map_field = F(type='object', fields={
        'screens': F(type='array', arr_len=num_screens, field=screen_field),
    })

    return F(type='array', arr_len='H', field=map_field)
