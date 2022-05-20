import os
import unittest
import hashlib
from pathlib import Path

from src.zquest.extract import ZeldaClassicReader

os.makedirs('.tmp', exist_ok=True)


class TestReader(unittest.TestCase):

    def test_read_and_write_qst(self):
        reader = ZeldaClassicReader('test_data/1st.qst')
        reader.read_qst()
        self.assertEqual(len(reader.combos), 160)
        self.assertEqual(reader.combos[0]['tile'], 316)
        self.assertEqual(len(reader.maps), 3)
        self.assertEqual(reader.maps[2]['screens'][0]['color'], 7)
        reader.save_qst('.tmp/1st-test.qst')

        reader = ZeldaClassicReader('.tmp/1st-test.qst')
        reader.read_qst()
        self.assertEqual(len(reader.combos), 160)
        self.assertEqual(len(reader.maps), 3)
        self.assertEqual(reader.combos[0]['tile'], 316)

        original_hash = hashlib.md5(
            Path('test_data/1st.qst').read_bytes()).hexdigest()
        copy_hash = hashlib.md5(
            Path('.tmp/1st-test.qst').read_bytes()).hexdigest()
        self.assertEqual(original_hash, copy_hash)

    def test_modify_qst(self):
        reader = ZeldaClassicReader('test_data/1st.qst')
        reader.read_qst()
        reader.combos[0]['tile'] = 1234
        reader.maps[2]['screens'][0]['color'] = 9
        reader.save_qst('.tmp/1st-test.qst')

        reader = ZeldaClassicReader('.tmp/1st-test.qst')
        reader.read_qst()
        self.assertEqual(len(reader.combos), 160)
        self.assertEqual(reader.combos[0]['tile'], 1234)
        self.assertEqual(reader.maps[2]['screens'][0]['color'], 9)

    def test_modify_qst_add_combo(self):
        reader = ZeldaClassicReader('test_data/1st.qst')
        reader.read_qst()
        reader.combos.append(reader.combos[0].copy())
        reader.save_qst('.tmp/1st-test.qst')

        reader = ZeldaClassicReader('.tmp/1st-test.qst')
        reader.read_qst()
        self.assertEqual(len(reader.combos), 161)
        self.assertEqual(reader.combos[0]['tile'], 316)
        self.assertEqual(reader.maps[2]['screens'][0]['color'], 7)


if __name__ == '__main__':
    unittest.main()
