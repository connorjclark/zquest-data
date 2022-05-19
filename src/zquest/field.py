from dataclasses import dataclass
from typing import Any, Dict, Optional


def if_(bool: bool, first: Any, second: Any):
  return first if bool else second


@dataclass
class F:
  type: str
  field: Optional['F'] = None # only used for array type
  fields: Optional[Dict[str, 'F']] = None # only used for object type
  arr_len: Optional[int] = None
  encode_arr_len: Optional[str] = None
  arr_bitmask: Optional[bool] = None
  str_len: Optional[int] = None
