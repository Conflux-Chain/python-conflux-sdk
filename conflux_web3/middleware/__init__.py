from typing import (
    TYPE_CHECKING, 
    Sequence, 
    Tuple,
)
from conflux_web3.middleware.pending import (
    PendingTransactionMiddleware
)
from conflux_web3.middleware.wallet import (
    Wallet,
    construct_sign_and_send_raw_middleware
)
from conflux_web3.middleware.cache import (
    simple_cache_middleware
)
from conflux_web3.middleware.names import (
    name_to_address_middleware
)
from conflux_web3.types import (
    Middleware
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

def conflux_default_middlewares(w3: "Web3") -> Sequence[Tuple[Middleware, str]]:
    return [
        (PendingTransactionMiddleware, "PendingTransactionMiddleware"),
        (Wallet(), "wallet"),
        (simple_cache_middleware, "CacheMiddleware"),
        (name_to_address_middleware(w3), "name_to_address"),
    ]


__all__ = [
    "PendingTransactionMiddleware",
    "Wallet",
    "construct_sign_and_send_raw_middleware",
    "conflux_default_middlewares"
]
