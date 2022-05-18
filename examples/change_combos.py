import context
import os

from zquest.extract import ZeldaClassicReader

dir = os.path.dirname(__file__)
qst_path = os.path.join(dir, '../test_data/1st.qst')
reader = ZeldaClassicReader(qst_path)
reader.read_qst()

for i, combo in enumerate(reader.combos):
  print(f'combo #{i}: tile={combo["tile"]}')

reader.combos[0]['tile'] = 1234
reader.save_qst(os.path.join(dir, '../output/1st-modified.qst'))

reader = ZeldaClassicReader(os.path.join(dir, '../output/1st-modified.qst'))
reader.read_qst()
# TODO: doesn't actually persist yet
print(reader.combos[0]['tile'], reader.combos[0]['tile'] == 1234)
print(reader.combos[1]['tile'], reader.combos[1]['tile'] == 317)
