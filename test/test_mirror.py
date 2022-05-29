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
        self.assertEqual(self.get_hash('vertical'), 'afddec3bfcebaf296e13b8a628b6eece')
        self.assertEqual(self.get_hash('horizontal'), '3a3c90d307d2f7a6d1f3879570800678')
        self.assertEqual(self.get_hash('both'), 'd938701a9bb6716d6357fc676c670b15')


if __name__ == '__main__':
    unittest.main()
