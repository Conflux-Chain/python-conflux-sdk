import imp
from typing import (
    TYPE_CHECKING,
    Any,
    Tuple,
    cast,
)

from eth_typing import (
    TypeStr,
)

from eth_utils.toolz import (
    curry, # type: ignore
)

from ens import ENS

from web3._utils.ens import (
    StaticENS,
    validate_name_has_address,
)
from web3._utils.empty import (
    empty
)
from web3.exceptions import (
    InvalidAddress,
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
