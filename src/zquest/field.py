from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class F:
    type: str
    field: Optional['F'] = None  # only used for array type
    fields: Optional[Dict[str, 'F']] = None  # only used for object type
    arr_len: Optional[int] = None
    encode_arr_len: Optional[str] = None
    arr_bitmask: Optional[bool] = None
    str_len: Optional[int] = None