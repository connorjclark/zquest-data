from dataclasses import dataclass
from typing import Callable, Dict, Optional, Union
import pprint
import inspect


def convert_dict_for_repr(dict: Dict) -> Dict:
    """
    Removes None values, and prints functions as string.
    """
    return {k: inspect.getsource(v) if callable(v) else v for k, v in dict.items() if v is not None}


@dataclass
class F:
    type: str
    field: Optional['F'] = None  # only used for array type
    fields: Optional[Dict[str, Union['F', str]]] = None  # only used for object type
    arr_len: Optional[Union[int, str, Callable]] = None
    arr_bitmask: Optional[str] = None
    str_len: Optional[str] = None  # only used for varstr type

    def __repr__(self):
        without_nones = convert_dict_for_repr(self.__dict__)
        if 'fields' in without_nones:
            without_nones['fields'] = convert_dict_for_repr(without_nones['fields'])
        return pprint.pformat(without_nones, sort_dicts=False, indent=4)
