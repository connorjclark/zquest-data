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
        self.assertEqual(self.get_hash('horizontal'), 'f038a4ecccd871e6e5a20e842f24d1e0')
        self.assertEqual(self.get_hash('both'), 'b68e61e5aa130349468ff29b6c486021')


if __name__ == '__main__':
    unittest.main()
