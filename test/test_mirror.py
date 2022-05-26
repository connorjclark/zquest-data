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
        self.assertEqual(self.get_hash('vertical'), '64aa751c28b1d38b59edf4ee5fbe952b')
        self.assertEqual(self.get_hash('horizontal'), '635ce9259347e284622ff91e9f458677')
        self.assertEqual(self.get_hash('both'), '404e4866ea352e9bb01945f2565290d3')


if __name__ == '__main__':
    unittest.main()
