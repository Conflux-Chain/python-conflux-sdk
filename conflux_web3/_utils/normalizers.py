from typing import (
    TYPE_CHECKING,
    Any,
    Tuple,
)

from eth_typing import (
    TypeStr,
)

from eth_utils.toolz import (
    curry, # type: ignore
)

from cfx_address import (
    Base32Address
)
from conflux_web3._utils.cns import (
    is_cns_name,
    resolve_if_cns_name,
)
from conflux_web3.exceptions import (
    NoWeb3Exception
)

if TYPE_CHECKING:
    from conflux_web3 import Web3  # noqa: F401

def rpc_snake_to_camel(snake_str: str) -> str:
    components = snake_str.split('_')
    rtn = ""
    for i, word in enumerate(components):
        rtn += word if i == 0 else word.title()
    return rtn

@curry
def abi_cns_resolver(w3: "Web3", type_str: TypeStr, val: Any) -> Tuple[TypeStr, Any]:
    if type_str == "address" and is_cns_name(val):
        if w3 is None:
            raise NoWeb3Exception(
                f"Could not look up name {val!r} because no web3"
                " connection available"
            )
        return type_str, resolve_if_cns_name(w3, val)
    else:
        return type_str, val

@curry
def addresses_to_verbose_base32(
    network_id: int, type_str: TypeStr, data: Any
) -> Tuple[TypeStr, Base32Address]:
    if type_str == "address":
        return type_str, Base32Address(data, network_id, verbose=True, _ignore_invalid_type=True)
    return type_str, data
