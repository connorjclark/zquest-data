cdef extern from "decode.c":
  int decode(const char *data, char *output, long size, int method)


def py_decode(const char *data, char *output, long size, int method) -> int:
  return decode(data, output, size, method)
