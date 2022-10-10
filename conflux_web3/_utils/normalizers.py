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
)

if TYPE_CHECKING:
    from conflux_web3 import Web3  # noqa: F401


@curry
def abi_cns_resolver(w3: "Web3", type_str: TypeStr, val: Any) -> Tuple[TypeStr, Any]:
    if type_str == "address" and is_cns_name(val):
        if w3 is None:
            raise InvalidAddress(
                f"Could not look up name {val!r} because no web3"
                " connection available"
            )

        _ens = cast(ENS, w3.ens)
        if _ens is empty:
            raise InvalidAddress(
                f"Could not look up name {val!r} because ENS is" " set to None"
            )
        # elif int(w3.net.version) != 1 and not isinstance(_ens, StaticENS):
        #     raise InvalidAddress(
        #         f"Could not look up name {val!r} because web3 is"
        #         " not connected to mainnet"
        #     )
        else:
            return type_str, validate_name_has_address(_ens, val)
    else:
        return type_str, val
