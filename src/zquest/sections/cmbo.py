from zquest.bytes import Bytes
from zquest.field import F, if_
from zquest.version import Version


def get_cmbo_field(bytes: Bytes, version: Version, sversion: int) -> F:
  encode_arr_len = None
  if version.zelda_version < 0x174:
    num_combos = 1024
  elif version.zelda_version < 0x191:
    num_combos = 2048
  else:
    num_combos = bytes.read_int()
    encode_arr_len = 'H'

  combo_field = F(type='object', fields={
    'tile': F(type=if_(sversion >= 11, 'I', 'H')),
    'flip': F(type='B' ),
    'walk': F(type='B' ),
    'type': F(type='B' ),
    'csets': F(type='B' ),
    '_padding1': F(type='2s') if version.zelda_version < 0x193 else None,
    '_padding2': F(type='16s') if version.zelda_version == 0x191 else None,
    'frames': F(type='B' ),
    'speed': F(type='B' ),
    'nextcombo': F(type='H' ),
    'nextcset': F(type='B' ),
    'flag': F(type='B') if sversion >= 3 else None,
    'skipanim': F(type='B') if sversion >= 4 else None,
    'nexttimer': F(type='H') if sversion >= 4 else None,
    'skipanimy': F(type='B') if sversion >= 5 else None,
    'animflags': F(type='B') if sversion >= 6 else None,
    'attributes': F(arr_len= 4, type='I') if sversion >= 8 else None,
    'usrflags': F(type='I') if sversion >= 8 else None,
    'triggerFlags': F(arr_len= 2, type='I') if sversion == 9 else None,
    'triggerLevel': F(type='I') if sversion == 9 else None,
    'triggerFlags': F(arr_len= 3, type='I') if sversion >= 10 else None,
    'triggerLevel': F(type='I') if sversion >= 10 else None,
    'label': F(arr_len= 11, type='B') if sversion >= 12 else None,
    '_padding3': F(type='11s') if version.zelda_version < 0x193 else None,
    'attributes': F(arr_len= 4, type='B') if sversion >= 13 else None,
    'script': F(type='H') if sversion >= 14 else None,
    'initd': F(arr_len= 2, type='I') if sversion >= 14 else None,
  })

  return F(type='array', arr_len=num_combos, encode_arr_len=encode_arr_len, field=combo_field)
