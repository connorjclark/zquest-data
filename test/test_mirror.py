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
        self.assertEqual(self.get_hash('vertical'), '09ea4fba4124d2be16e6c4e564fc80ff')
        self.assertEqual(self.get_hash('horizontal'), 'd5eed71a394dcf4f468ab2085e161b51')
        self.assertEqual(self.get_hash('both'), 'a44ec690978f2032a3427e79b02b8c83')


if __name__ == '__main__':
    unittest.main()
