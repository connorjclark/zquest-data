from dataclasses import dataclass
from typing import Callable, Dict, Optional, Union


@dataclass
class F:
    type: str
    field: Optional['F'] = None  # only used for array type
    fields: Optional[Dict[str, Union['F', str]]] = None  # only used for object type
    arr_len: Optional[Union[int, str, Callable]] = None
    arr_bitmask: Optional[str] = None
    str_len: Optional[int] = None
