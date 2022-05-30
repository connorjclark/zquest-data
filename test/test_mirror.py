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
        self.assertEqual(self.get_hash('vertical'), 'f0cf3e91ec01f0379502180a18632557')
        self.assertEqual(self.get_hash('horizontal'), 'd07a2dfe3fd1fc31ce133e1eea521e21')
        self.assertEqual(self.get_hash('both'), '8b3f356753f31d38fa320e477f60ffbb')


if __name__ == '__main__':
    unittest.main()
