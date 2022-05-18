import json
import numpy

INDENT = 2
SPACE = " "
NEWLINE = "\n"

# Changed basestring to str, and dict uses items() instead of iteritems().
def pretty_json_format(o, level=2):
  # import json
  # return json.dumps(o, indent=2)
  
  ret = ""
  if isinstance(o, dict):
    ret += "{" + NEWLINE
    comma = ""
    for k, v in o.items():
      ret += comma
      comma = ",\n"
      ret += SPACE * INDENT * (level + 1)
      ret += '"' + str(k) + '":' + SPACE
      ret += pretty_json_format(v, level + 1)

    ret += NEWLINE + SPACE * INDENT * level + "}"
  elif isinstance(o, str):
    ret += json.dumps(o)
  elif isinstance(o, list):
    ret += "[" + ",".join([pretty_json_format(e, level + 1) for e in o]) + "]"
  # Tuples are interpreted as lists
  elif isinstance(o, tuple):
    ret += "[" + ",".join(pretty_json_format(e, level + 1) for e in o) + "]"
  elif isinstance(o, bool):
    ret += "true" if o else "false"
  elif isinstance(o, int):
    ret += str(o)
  elif isinstance(o, float):
    ret += '%.7g' % o
  elif isinstance(o, numpy.ndarray) and numpy.issubdtype(o.dtype, numpy.integer):
    ret += "[" + ','.join(map(str, o.flatten().tolist())) + "]"
  elif isinstance(o, numpy.ndarray) and numpy.issubdtype(o.dtype, numpy.inexact):
    ret += "[" + ','.join(map(lambda x: '%.7g' % x, o.flatten().tolist())) + "]"
  elif o is None:
    ret += 'null'
  else:
    raise TypeError("Unknown type '%s' for json serialization" % str(type(o)))
  return ret