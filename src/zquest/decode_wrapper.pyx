import cython

cdef extern from "decode.h":
  int decode(const char* qstpath, const char* outpath)
  int get_decoded_key()
  int encode(const char* inputpath, const char* outpath, int key)


def py_decode(qstpath, outpath):
  qstpath = qstpath.encode('utf-8')
  outpath = outpath.encode('utf-8')
  err = decode(qstpath, outpath)
  key = get_decoded_key() if err == 0 else None
  return (err, key)


def py_encode(inputpath, outpath, key=0):
  inputpath = inputpath.encode('utf-8')
  outpath = outpath.encode('utf-8')
  return encode(inputpath, outpath, key)
