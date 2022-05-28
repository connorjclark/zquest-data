import cython

cdef extern from "decode.h":
  int decode(const char* qstpath, const char* outpath)
  int get_decoded_method()
  int get_decoded_key()
  int encode(const char* inputpath, const char* outpath, int method, int key)


def py_decode(qstpath, outpath):
  qstpath = qstpath.encode('utf-8')
  outpath = outpath.encode('utf-8')
  err = decode(qstpath, outpath)
  method = get_decoded_method() if err == 0 else None
  key = get_decoded_key() if err == 0 else None
  return (err, method, key)


def py_encode(inputpath, outpath, method=0, key=0):
  inputpath = inputpath.encode('utf-8')
  outpath = outpath.encode('utf-8')
  return encode(inputpath, outpath, method, key)
