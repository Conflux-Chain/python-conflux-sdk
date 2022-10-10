from typing import Any
from web3._utils.ens import (
    is_ens_name
)
from cfx_address.utils import (
    is_valid_base32
)

def is_cns_name(value: Any) -> bool:
    if is_valid_base32(value):
        return False
    else:
        return is_ens_name(value)
