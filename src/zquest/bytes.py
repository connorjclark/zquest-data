from io import IOBase
import os
from struct import *
from typing import Any


class Bytes:
    def __init__(self, f: IOBase):
        self.f = f

        f.seek(0, os.SEEK_END)
        self.length = f.tell()
        f.seek(0)

    def bytes_read(self):
        return self.f.tell()

    def advance(self, n: int):
        self.f.seek(n, 1)

    def rewind(self):
        self.f.seek(0)

    def has_bytes(self) -> bool:
        more_bytes = self.f.read(1) != b''
        if more_bytes:
            self.f.seek(-1, 1)
        return more_bytes

    def peek(self, n: int):
        bytes = self.f.read(n)
        self.f.seek(-len(bytes), 1)
        return bytes

    def read(self, n: int) -> bytes:
        return self.f.read(n)

    def write(self, n: int):
        self.f.write(n)

    def read_packed(self, format: str) -> Any:
        return unpack(format, self.read(calcsize(format)))[0]

    def write_packed(self, format: str, val: Any):
        self.f.write(pack(format, val))

    def read_byte(self) -> int:
        return unpack('B', self.read(1))[0]

    def write_byte(self, val):
        self.f.write(pack('B', val))

    def read_int(self) -> int:
        return unpack('<H', self.read(2))[0]

    def write_int(self, val):
        self.f.write(pack('<H', val))

    def read_long(self) -> int:
        return unpack('<I', self.read(4))[0]

    def write_long(self, val):
        self.f.write(pack('<I', val))
