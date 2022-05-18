import context
import os

from zquest.extract import ZeldaClassicReader

dir = os.path.dirname(__file__)
qst = os.path.join(dir, '../test_data/1st.qst')
reader = ZeldaClassicReader('test_data/1st.qst')
reader.read_qst()

for i, combo in enumerate(reader.combos):
  print(f'combo #{i}: tile={combo["tile"]}')

# TODO: change combo data and write back to qst file
