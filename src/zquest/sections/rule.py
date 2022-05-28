from ..field import F
from ..version import Version


def get_rule_field(version: Version, sversion: int) -> F:
    return F(arr_len=100 if sversion >= 15 else 20, type='bytes')
