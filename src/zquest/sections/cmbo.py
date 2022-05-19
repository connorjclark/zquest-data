from zquest.field import F, if_


def get_cmbo_field(bytes, zelda_version, sversion) -> F:
  encode_arr_len = None
  if zelda_version < 0x174:
    num_combos = 1024
  elif zelda_version < 0x191:
    num_combos = 2048
  else:
    num_combos = bytes.read_int()
    encode_arr_len = 'H'

  return F(name='', type='object', arr_len=num_combos, encode_arr_len=encode_arr_len, fields=[
    F(name='tile', type=if_(sversion >= 11, 'I', 'H')),
    F(name='flip', type='B' ),
    F(name='walk', type='B' ),
    F(name='type', type='B' ),
    F(name='csets', type='B' ),
    F(name='_padding', type='2s') if zelda_version < 0x193 else None,
    F(name='_padding', type='16s') if zelda_version == 0x191 else None,
    F(name='frames', type='B' ),
    F(name='speed', type='B' ),
    F(name='nextcombo', type='H' ),
    F(name='nextcset', type='B' ),
    F(name='flag', type='B') if sversion >= 3 else None,
    F(name='skipanim', type='B') if sversion >= 4 else None,
    F(name='nexttimer', type='H') if sversion >= 4 else None,
    F(name='skipanimy', type='B') if sversion >= 5 else None,
    F(name='animflags', type='B') if sversion >= 6 else None,
    F(name='attributes', arr_len= 4, type='I') if sversion >= 8 else None,
    F(name='usrflags', type='I') if sversion >= 8 else None,
    F(name='triggerFlags', arr_len= 2, type='I') if sversion == 9 else None,
    F(name='triggerLevel', type='I') if sversion == 9 else None,
    F(name='triggerFlags', arr_len= 3, type='I') if sversion >= 10 else None,
    F(name='triggerLevel', type='I') if sversion >= 10 else None,
    F(name='label', arr_len= 11, type='B') if sversion >= 12 else None,
    F(name='_padding', type='11s') if zelda_version < 0x193 else None,
    F(name='attributes', arr_len= 4, type='B') if sversion >= 13 else None,
    F(name='script', type='H') if sversion >= 14 else None,
    F(name='initd', arr_len= 2, type='I') if sversion >= 14 else None,
  ])
