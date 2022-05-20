import os
import unittest
import hashlib
from pathlib import Path

from src.zquest.extract import ZeldaClassicReader


class TestReader(unittest.TestCase):

    def test_read_and_write_qst(self):
        reader = ZeldaClassicReader('test_data/1st.qst')
        reader.read_qst()
        self.assertEqual(len(reader.combos), 160)
        self.assertEqual(reader.combos[0]['tile'], 316)

        os.makedirs('.tmp', exist_ok=True)
        reader.save_qst('.tmp/1st-test.qst')
        self.assertEqual(len(reader.combos), 160)
        self.assertEqual(reader.combos[0]['tile'], 316)

        original_hash = hashlib.md5(
            Path('test_data/1st.qst').read_bytes()).hexdigest()
        copy_hash = hashlib.md5(
            Path('.tmp/1st-test.qst').read_bytes()).hexdigest()
        self.assertEqual(original_hash, copy_hash)


if __name__ == '__main__':
    unittest.main()
