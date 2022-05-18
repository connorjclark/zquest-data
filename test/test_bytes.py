import unittest
from src.zquest.bytes import Bytes

class TestStringMethods(unittest.TestCase):

    def test_read_str(self):
        with open(__file__, 'rb') as f:
            b = Bytes(f)
            self.assertEqual(b.read_str(15), 'import unittest')

if __name__ == '__main__':
    unittest.main()
