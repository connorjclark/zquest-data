cdef extern from "decode.c":
  int decode_file_007(const char *data, char *output, long size, int method)


def py_decode_file_007(const char *data, char *output, long size, int method) -> int:
  return decode_file_007(data, output, size, method)
