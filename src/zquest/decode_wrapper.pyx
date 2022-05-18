import cython

cdef extern from "decode.h":
  int decode(const char* qstpath, const char* outpath)
  int encode(const char* inputpath, const char* outpath)


def py_decode(qstpath, outpath):
  qstpath = qstpath.encode('utf-8')
  outpath = outpath.encode('utf-8')
  return decode(qstpath, outpath)


def py_encode(inputpath, outpath):
  inputpath = inputpath.encode('utf-8')
  outpath = outpath.encode('utf-8')
  return encode(inputpath, outpath)
