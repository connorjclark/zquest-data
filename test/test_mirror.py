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
        self.assertEqual(self.get_hash('vertical'), '8118e3663d823d1503ee21853c08dab4')
        self.assertEqual(self.get_hash('horizontal'), '18b515fd2b734dac7ad235552f70647c')
        self.assertEqual(self.get_hash('both'), '8169fa3658515e064f7417e40e43875f')


if __name__ == '__main__':
    unittest.main()
