from io import IOBase
import os
from struct import *
from typing import List

class Bytes:
  def __init__(self, f: IOBase):
    self.f = f
    self.bytes_read = 0

    f.seek(0, os.SEEK_END)
    self.length = f.tell()
    f.seek(0)
  
  def has_bytes(self) -> bool:
    more_bytes = self.f.read(1) != b''
    if more_bytes:
      self.f.seek(-1,1)
    return more_bytes

  def peek(self):
    byte = self.f.read(1)
    if byte != b'':
      self.f.seek(-1,1)
    return byte
  
  def read(self, n: int) -> List[int]:
    if n == 0:
      return b''

    data = self.f.read(n)
    self.bytes_read += n
    return data
  
  def read_byte(self) -> int:
    return unpack('B', self.read(1))[0]

  def read_int(self) -> int:
    return unpack('<H', self.read(2))[0]
  
  def read_signed_int_big_endian(self) -> int:
    return unpack('>h', self.read(2))[0]

  def read_long(self) -> int:
    return unpack('<I', self.read(4))[0]
  
  def read_long_big_endian(self) -> int:
    return unpack('>I', self.read(4))[0]
  
  def read_array(self, word_size, length) -> List[int]:
    if (word_size == 1):
      read = self.read_byte
    elif (word_size == 2):
      read = self.read_int
    elif (word_size == 4):
      read = self.read_long
    return [read() for _ in range(length)]
  
  def read_str(self, n: int) -> str:
    raw = self.read(n)
    if raw.find(b'\x00') != -1:
      return raw[0:raw.index(b'\x00')].decode('utf-8', errors='ignore')
    else:
      return raw.decode('utf-8', errors='ignore')

  def debug(self, n):
    b = self.read(n)
    print('DEBUG')
    print(b)
    print(b.hex())
    for byte in b:
      print(byte)
    self.f.seek(-n, 1)
