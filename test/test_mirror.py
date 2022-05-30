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
        self.assertEqual(self.get_hash('vertical'), 'aad7f82d1d4da46802c7bf2ddb20c20b')
        self.assertEqual(self.get_hash('horizontal'), 'c99c396de1b0cfc5c117aa6a12b4877f')
        self.assertEqual(self.get_hash('both'), '86eede412196d04147fe3ec49f652328')


if __name__ == '__main__':
    unittest.main()
