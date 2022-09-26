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

conflux_default_middlewares = [
    (PendingTransactionMiddleware, "PendingTransactionMiddleware"),
    (Wallet(), "wallet"),
    (simple_cache_middleware, "CacheMiddleware")
]


__all__ = [
    "PendingTransactionMiddleware",
    "Wallet",
    "construct_sign_and_send_raw_middleware",
    "conflux_default_middlewares"
]
