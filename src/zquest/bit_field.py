from typing import List


def get_indices(index: int):
    byte_index = int(index // 8)
    bit_index = index % 8
    return byte_index, bit_index


class BitField:
    def __init__(self, values: List[str], bits: bytearray):
        self.values = values
        self.bits = bits

    def value_from_index(self, index: int):
        return self.values[index]
    
    def index_from_value(self, value: str):
        return self.values.index(value)

    def get(self, index: int) -> bool:
        if index > len(self.bits) * 8:
            raise Exception('index out of bounds')

        byte_index, bit_index = get_indices(index)
        return (self.bits[byte_index] & (1 << bit_index)) != 0

    def set(self, index: int, enable: bool):
        if index > len(self.bits) * 8:
            raise Exception('index out of bounds')

        byte_index, bit_index = get_indices(index)
        if enable:
            self.bits[byte_index] = self.bits[byte_index] | (1 << bit_index)
        else:
            self.bits[byte_index] = self.bits[byte_index] & ~(1 << bit_index)

    def get_indices(self):
        indices = []
        for i in range(len(self.bits) * 8):
            if self.get(i):
                indices.append(i)
        return indices

    def get_values(self):
        return [self.values[x] for x in self.get_indices()]
