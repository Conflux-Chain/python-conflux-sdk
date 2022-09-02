from conflux_web3.middleware.pending import PendingTransactionMiddleware
from conflux_web3.middleware.wallet import (
    Wallet,
    construct_sign_and_send_raw_middleware
)

conflux_default_middlewares = [
    (PendingTransactionMiddleware, "PendingTransactionMiddleware"),
    (Wallet(), "wallet")
]


__all__ = [
    "PendingTransactionMiddleware",
    "Wallet",
    "construct_sign_and_send_raw_middleware",
    "conflux_default_middlewares"
]
