from dataclasses import dataclass
from typing import Any, List, Optional


def if_(bool: bool, first: Any, second: Any):
  return first if bool else second


@dataclass
class F:
  name: str
  type: str
  fields: Optional[List[Any]] = None # List[F]
  arr_len: Optional[int] = None
  encode_arr_len: Optional[str] = None
  str_len: Optional[int] = None
