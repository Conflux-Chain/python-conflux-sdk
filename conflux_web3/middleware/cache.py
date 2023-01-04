from typing import (
    Set,
    cast,
)

from web3.middleware.cache import (
    construct_simple_cache_middleware
)
from conflux_web3.types import RPCEndpoint

CONFLUX_SIMPLE_CACHE_RPC_WHITELIST = cast(
    Set[RPCEndpoint],
    {
        # "cfx_chainId", this is not a supported api
        "cfx_gasPrice"
    },
)

simple_cache_middleware = construct_simple_cache_middleware(
    rpc_whitelist=CONFLUX_SIMPLE_CACHE_RPC_WHITELIST,
)
