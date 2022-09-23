from typing import (
    Any,
    Dict,
    Set,
    Type,
    cast,
)
import functools
import lru

from web3.middleware.cache import (
    construct_simple_cache_middleware
)
from conflux_web3.types import RPCEndpoint

CONFLUX_SIMPLE_CACHE_RPC_WHITELIST = cast(
    Set[RPCEndpoint],
    {
        "cfx_chainId",
    },
)

simple_cache_middleware = construct_simple_cache_middleware(
    cache_class=cast(Type[Dict[Any, Any]], functools.partial(lru.LRU, 256)),
    rpc_whitelist=CONFLUX_SIMPLE_CACHE_RPC_WHITELIST,
)
