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
        self.assertEqual(self.get_hash('vertical'), '842385b707c279b4b92be82adfbf7b4d')
        self.assertEqual(self.get_hash('horizontal'), 'd74c1c210cc8bf67d4c1004d81d513d8')
        self.assertEqual(self.get_hash('both'), '978ac1faf09845480856636d6d59467d')


if __name__ == '__main__':
    unittest.main()
