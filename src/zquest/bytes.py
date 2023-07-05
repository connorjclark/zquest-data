from functools import cache
from struct import *
from typing import Any

# TODO: break up into reading / writing classes.


@cache
def cached_calcsize(format: str) -> int:
    return calcsize(format)


class Bytes:
    def __init__(self, data: bytearray):
        # offset is_only used for reading. bytes written are always
        # appended to the end of the bytearray.
        self.offset = 0
        self.data = data

    @property
    def length(self):
        return len(self.data)

    def bytes_read(self):
        return self.offset

    def bytes_remaining(self):
        return self.length - self.offset

    def advance(self, n: int):
        self.offset += n

    def rewind(self):
        self.offset = 0

    def has_bytes(self) -> bool:
        return self.length > self.offset

    def peek(self, n: int):
        bytes = self.read(n)
        self.advance(-len(bytes))
        return bytes

    def read(self, n: int) -> bytearray:
        result = self.data[self.offset:self.offset+n]
        self.offset += n
        # TODO: 1st-may-2022.qst rule section should be 100 bytes, but is only 26?
        # old file-based (self.f.read) code made this no problem, but new code
        # needs to bound the offset to self.length to prevent noisy errors
        # should fix this.
        if n == 100:
            self.offset = min(self.offset, self.length)
        return result

    def write(self, n: Any):
        if type(n) == bytearray or type(n) == bytes or type(n) == list:
            self.data.extend(n)
        else:
            self.data.append(n)

    def read_packed(self, format: str) -> Any:
        result = unpack_from(format, self.data, self.offset)[0]
        self.offset += cached_calcsize(format)
        return result

    def write_packed(self, format: str, val: Any):
        result = pack(format, val)
        self.data += result

    def read_byte(self) -> int:
        return self.read_packed('B')

    def write_byte(self, val):
        self.write_packed('B', val)

    def read_int(self) -> int:
        return self.read_packed('<H')

    def write_int(self, val):
        self.write_packed('<H', val)

    def read_long(self) -> int:
        return self.read_packed('<I')

    def write_long(self, val):
        self.write_packed('<I', val)
