from typing import List


def to_index(x: int, y: int, w: int) -> int:
    return x + y * w


def bit(flags: bytes, index: int) -> bool:
    byte_index = int(index // 8)
    bit_index = index % 8
    return (flags[byte_index] & (1 << bit_index)) != 0


class BitField:
    def __init__(self, values: List[str], bits: bytearray):
        self.values = values
        self.bits = bits

    def value_from_index(self, index: int):
        return self.values[index]
    
    def index_from_value(self, value: str):
        return self.values.index(value)

    def get_indices(self):
        indices = []
        for i in range(len(self.bits) * 8):
            if bit(self.bits, i):
                indices.append(i)
        return indices

    def get_values(self):
        return [self.values[x] for x in self.get_indices()]
