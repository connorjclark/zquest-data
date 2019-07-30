import cython

cdef extern from "decode.c":
  int decode(const char *data, char *output, long size, int method)


def py_decode(const char *data, long size, int method):
  # minus 8 bytes for seed and checksum
  cdef char [::1] output = cython.view.array(shape=(size-8,), itemsize=1, format="B")
  err = decode(data, &output[0], size, method)
  return (err, bytes(output))
