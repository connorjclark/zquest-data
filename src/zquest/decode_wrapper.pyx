import cython

cdef extern from "decode.h":
  int decode(const char* qstpath, const char* outpath)


def py_decode(qstpath, outpath):
  qstpath = qstpath.encode('utf-8')
  outpath = outpath.encode('utf-8')
  return decode(qstpath, outpath)
