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
        self.assertEqual(self.get_hash('vertical'), '5c4927c2a06f5a93366ab5c8f3f62d1d')
        self.assertEqual(self.get_hash('horizontal'), 'a9c330f4cdeb4ac04b3ef42cd3f33005')
        self.assertEqual(self.get_hash('both'), '138cb1413e60c45a875cb202a78197d1')


if __name__ == '__main__':
    unittest.main()
