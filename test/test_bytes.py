import unittest
from zquest.bytes import Bytes


class TestBytes(unittest.TestCase):
    def test_write_byte(self):
        b = Bytes(bytearray())
        b.write_byte(0)
        b.write_byte(1)
        b.write_byte(2)
        b.rewind()
        self.assertEqual(b.read_byte(), 0)
        self.assertEqual(b.read_byte(), 1)
        self.assertEqual(b.read_byte(), 2)


if __name__ == '__main__':
    unittest.main()
