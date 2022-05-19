from zquest.bytes import Bytes
from zquest.field import F
from zquest.version import Version


def get_map_field(bytes: Bytes, version: Version, sversion: int) -> F:
  extended_arrays = version > Version(zelda_version=0x211, build=7)
  common_arr_len = 4 if extended_arrays else 1

  if version < Version( zelda_version=0x192, build=137):
    num_secret_combos = 20
  elif version.zelda_version == 0x192 and version.build < 154:
    num_secret_combos = 256
  else:
    num_secret_combos = 128

  if version < Version(zelda_version=0x192, build=137):
    num_screens = 132
  else:
    num_screens = 136

  screen_field = F(name='', type='object', fields=[
    F(name='valid', type='B'),
    F(name='guy', type='B'),
    F(name='str', type='H' if version > Version(zelda_version=0x192, build=146) else 'B'),
    F(name='room', type='B'),
    F(name='item', type='B'),
    F(name='hasItem', type='B') if version >= Version(zelda_version=0x211, build=14) else None,
    F(name='_padding', type='B') if version < Version(zelda_version=0x192, build=154) else None,
    F(name='tileWarpType', arr_len=common_arr_len, type='B'),
    F(name='doorComboSet', type='H') if version > Version(zelda_version=0x192, build=153) else None,
    F(name='warpReturnX', arr_len=common_arr_len, type='B'),
    F(name='warpReturnY', arr_len=common_arr_len, type='B'),
    F(name='warpReturnC', type='H' if sversion >= 18 else 'B') if version > Version(zelda_version=0x211, build=7) else None,
    F(name='stairX', type='B'),
    F(name='stairY', type='B'),
    F(name='itemX', type='B'),
    F(name='itemY', type='B'),
    F(name='color', type='H' if sversion > 15 else 'B'),
    F(name='enemyFlags', type='B'),
    F(name='doors', arr_len=4, type='B'),
    F(name='tileWarpDmap', arr_len=common_arr_len, type='H' if sversion > 11 else 'B'),
    F(name='tileWarpScreen', arr_len=common_arr_len, type='B'),
    F(name='tileWarpOverlayFlags', type='B') if sversion >= 15 else None,
    F(name='exitDir', type='B'),
    F(name='_padding', type='B') if version.zelda_version < 0x193 else None,
    F(name='_padding', type='B') if version > Version(zelda_version=0x192, build=145) and version < Version(zelda_version=0x192, build=154) else None,
    F(name='enemies', arr_len=10, type= 'H' if version >= Version(zelda_version=0x192, build=10) else 'B'),
    F(name='pattern', type='B'),
    F(name='sideWarpType', arr_len=common_arr_len, type='B'),
    F(name='sideWarpOverlayFlags', type='B') if sversion >= 15 else None,
    F(name='warpArrivalX', type='B'),
    F(name='warpArrivalY', type='B'),
    F(name='path', arr_len=4, type='B'),
    F(name='sideWarpScreen', arr_len=common_arr_len, type='B'),
    F(name='sideWarpDmap', arr_len=common_arr_len, type='H' if sversion > 11 else 'B'),
    F(name='sideWarpIndex', type='B') if version > Version(zelda_version=0x211, build=7) else None,
    F(name='underCombo', type='H'),
    F(name='old_cpage', type='B') if version.zelda_version < 0x193 else None,
    F(name='underCset', type='B'),
    F(name='catchAll', type='H'),
    F(name='flags', type='B'),
    F(name='flags2', type='B'),
    F(name='flags3', type='B'),
    F(name='flags4', type='B') if version > Version(zelda_version=0x211, build=1) else None,
    F(name='flags5', type='B') if version > Version(zelda_version=0x211, build=7) else None,
    F(name='noreset', type='H') if version > Version(zelda_version=0x211, build=7) else None,
    F(name='nocarry', type='H') if version > Version(zelda_version=0x211, build=7) else None,
    F(name='flags6', type='B') if version > Version(zelda_version=0x211, build=9) else None,
    F(name='flags7', type='B') if sversion > 5 else None,
    F(name='flags8', type='B') if sversion > 5 else None,
    F(name='flags9', type='B') if sversion > 5 else None,
    F(name='flags10', type='B') if sversion > 5 else None,
    F(name='csensitive', type='B') if sversion > 5 else None,
    F(name='oceanSfx', type='B') if sversion >= 14 else None,
    F(name='bossSfx', type='B') if sversion >= 14 else None,
    F(name='secretSfx', type='B') if sversion >= 14 else None,
    F(name='holdUpSfx', type='B') if sversion >= 15 else None,

    # this is a weird one for older versions
    F(name='layerMap', arr_len=6, type='B') if version > Version(zelda_version=0x192, build=97) else None,
    F(name='layerScreen', arr_len=6, type='B') if version > Version(zelda_version=0x192, build=97) else None,
    F(name='_skip', arr_len=4, type='B') if version > Version(zelda_version=0x192, build=23) and version < Version(zelda_version=0x192, build=98) else None,

    F(name='layerOpacity', arr_len=6, type='B') if version > Version(zelda_version=0x192, build=149) else None,
    F(name='_padding', type='B') if version == Version(zelda_version=0x192, build=153) else None,
    F(name='timedWarpTics', type='H') if version > Version(zelda_version=0x192, build=153) else None,
    F(name='nextMap', type='B') if version > Version(zelda_version=0x211, build=2) else None,
    F(name='nextScreen', type='B') if version > Version(zelda_version=0x211, build=2) else None,
    F(name='secretCombos', arr_len=num_secret_combos, type='B' if version < Version(zelda_version=0x192, build=154) else 'H'),
    F(name='secretCsets', arr_len=128, type='B') if version > Version(zelda_version=0x192, build=153) else None,
    F(name='secretFlags', arr_len=128, type='B') if version > Version(zelda_version=0x192, build=153) else None,
    F(name='_padding', type='B') if version > Version(zelda_version=0x192, build=97) and version < Version(zelda_version=0x192, build=154) else None,
    F(name='data', arr_len=16 * 11, type='H'),
    F(name='sflag', arr_len=16 * 11, type='B') if version > Version(zelda_version=0x192, build=20) else None,
    F(name='cset', arr_len=16 * 11, type='B') if version > Version(zelda_version=0x192, build=97) else None,
    F(name='screenMidi', type='H') if sversion > 4 else None,
    F(name='lensLayer', type='B') if sversion >= 17 else None,

    *([
      F(name='ff', type='object', arr_len=32, arr_bitmask=True, fields=[
        F(name='data', type='H'),
        F(name='cset', type='B'),
        F(name='delay', type='H'),
        F(name='x', type='I') if sversion >= 9 else None,
        F(name='y', type='I') if sversion >= 9 else None,
        F(name='xDelta', type='I') if sversion >= 9 else None,
        F(name='yDelta', type='I') if sversion >= 9 else None,
        F(name='xDelta2', type='I') if sversion >= 9 else None,
        F(name='yDelta2', type='I') if sversion >= 9 else None,
        F(name='link', type='B'),
        F(name='width', type='B') if sversion > 7 else None,
        F(name='height', type='B') if sversion > 7 else None,
        F(name='flags', type='I') if sversion > 7 else None,
        F(name='script', type='H') if sversion > 9 else None,
        F(name='initd', arr_len=8, type='I') if sversion > 10 else None,
        F(name='inita', arr_len=2, type='B') if sversion > 10 else None,
      ]),
    ] if sversion > 6 else []),

    F(name='npcStrings', arr_len=10, type='I') if sversion >= 19 and version.zelda_version > 0x253 else None,
    F(name='newItems', arr_len=10, type='H') if sversion >= 19 and version.zelda_version > 0x253 else None,
    F(name='newItemX', arr_len=10, type='H') if sversion >= 19 and version.zelda_version > 0x253 else None,
    F(name='newItemY', arr_len=10, type='H') if sversion >= 19 and version.zelda_version > 0x253 else None,
    F(name='script', type='H') if sversion >= 20 and version.zelda_version > 0x253 else None,
    F(name='screenInitd', arr_len=8, type='I') if sversion >= 20 and version.zelda_version > 0x253 else None,
    F(name='preloadScript', type='B') if sversion >= 21 and version.zelda_version > 0x253 else None,
    F(name='hideLayers', type='B') if sversion >= 22 and version.zelda_version > 0x253 else None,
    F(name='hideScriptLayers', type='B') if sversion >= 22 and version.zelda_version > 0x253 else None,
  ])

  map_field = F(name='', type='object', fields=[
    F(name='screens', type='object', arr_len=num_screens, fields=[screen_field]),
  ])

  map_count = bytes.read_int()
  return F(name='', type='object', arr_len=map_count, encode_arr_len='H', fields=[map_field])
