from typing import (
    TYPE_CHECKING, Any, Union
)
from web3._utils.ens import (
    is_ens_name
)
from web3._utils.empty import (
    empty
)
from web3.exceptions import (
    NameNotFound
)
from cfx_address.utils import (
    is_valid_base32
)
from cfx_address import (
    Base32Address
)
from conflux_web3.exceptions import (
    NameServiceNotSet
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

def is_cns_name(value: Any) -> bool:
    if is_valid_base32(value):
        return False
    else:
        return is_ens_name(value)
    
def validate_cns_existence(w3: "Web3"):
    if w3.cns is empty:
        raise NameServiceNotSet("Web3's name service is not set")

def resolve_if_cns_name(w3: "Web3", cns_name: str) -> Union[str, Base32Address]:
    if is_cns_name(cns_name):
        validate_cns_existence(w3)
        if addr := w3.cns.address(cns_name):
            return addr
        raise NameNotFound(f"{cns_name} resolve failed")
    return cns_name
