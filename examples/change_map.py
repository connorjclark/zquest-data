import context
import os

from zquest.extract import ZeldaClassicReader


def print_map(map):
    map_str = ''
    for screen in map['screens']:
        map_str += chr(0x30 + screen['color'])
    print('\n'.join(map_str[i:i+16] for i in range(0, len(map_str), 16)))
    print('------')


dir = os.path.dirname(__file__)
qst_path = os.path.join(dir, '../test_data/1st.qst')
reader = ZeldaClassicReader(qst_path)
reader.read_qst()

assert len(reader.maps) == 3
assert reader.maps[2]['screens'][0]['color'] == 7
for i, map in enumerate(reader.maps):
    print(f'map #{i}')
    print_map(map)

reader.maps[2]['screens'][0]['color'] = 9
reader.save_qst(os.path.join(dir, '../output/1st-modified.qst'))

reader = ZeldaClassicReader(os.path.join(dir, '../output/1st-modified.qst'))
reader.read_qst()

assert len(reader.maps) == 3
# TODO: does not persist yet
assert reader.maps[2]['screens'][0]['color'] == 9
for i, map in enumerate(reader.maps):
    print(f'map #{i}')
    print_map(map)
