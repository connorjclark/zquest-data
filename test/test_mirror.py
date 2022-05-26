import os
import unittest
import hashlib
from pathlib import Path

from examples.mirror import mirror_qst

os.makedirs('.tmp', exist_ok=True)


class TestMirror(unittest.TestCase):
    def get_hash(self, dir):
        mirror_qst(dir, 'test_data/1st.qst', '.tmp/1st-mirror-test.qst')
        return hashlib.md5(Path('.tmp/1st-mirror-test.qst').read_bytes()).hexdigest()

    def test_mirror_qst(self):
        self.assertEqual(self.get_hash('vertical'), 'f411965668efd8ae157e2255ac225069')
        self.assertEqual(self.get_hash('horizontal'), 'ba328da2706c5c399f66fe8e63f5c494')
        self.assertEqual(self.get_hash('both'), '5f74def0303ddcb093595906efefd252')


if __name__ == '__main__':
    unittest.main()
