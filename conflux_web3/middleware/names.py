# a fork from web3.middleware.names
from typing import (
    TYPE_CHECKING,
)

from web3._utils.rpc_abi import (
    abi_request_formatters,
)
from web3.middleware.formatting import (
    construct_formatting_middleware,
)

from conflux_web3.types import (
    Middleware,
)
from conflux_web3._utils.normalizers import (
    abi_cns_resolver,
)
from conflux_web3._utils.rpc_abi import (
    RPC_ABIS,
)

if TYPE_CHECKING:
    from conflux_web3 import Web3  # noqa: F401


def name_to_address_middleware(w3: "Web3") -> Middleware:
    normalizers = [
        abi_cns_resolver(w3), # type: ignore
    ]
    return construct_formatting_middleware(
        request_formatters=abi_request_formatters(normalizers, RPC_ABIS)  # type: ignore
    )
