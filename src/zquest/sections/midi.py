from ..field import F
from ..version import Version


# "readtunes" in qst.cpp
def get_midi_field(version: Version, sversion: int) -> F:
    tune_field = F(type='object', fields={
        'title': '36s' if sversion >= 4 else '20s',
        'start': 'I',
        'loop_start': 'I',
        'loop_end': 'I',
        'loop': 'H',
        'volume': 'H',
        '_padding': 'I' if version.zelda_version < 0x193 else None,
        'flags': 'B' if sversion >= 3 else None,
        'format': 'B' if sversion >= 2 else None,
        'divisions': '>h',
        'tracks': F(arr_len=32, type='array', field=F(arr_len='>I', type='bytes')),
    })

    return F(type='array', arr_len=252, arr_bitmask=32, field=tune_field)
