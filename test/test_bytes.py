import unittest
import io
from src.zquest.bytes import Bytes


class TestBytes(unittest.TestCase):

    def test_read_str(self):
        with open(__file__, 'rb') as f:
            b = Bytes(f)
            self.assertEqual(b.read_str(15), 'import unittest')

    def test_write_byte(self):
        b = Bytes(io.BytesIO())
        b.write_byte(0)
        b.write_byte(1)
        b.write_byte(2)
        b.rewind()
        self.assertEqual(b.read_byte(), 0)
        self.assertEqual(b.read_byte(), 1)
        self.assertEqual(b.read_byte(), 2)


if __name__ == '__main__':
    unittest.main()
