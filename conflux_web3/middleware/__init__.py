from conflux_web3.middleware.pending import PendingTransactionMiddleware
from conflux_web3.middleware.wallet import WalletMiddlewareFactory

conflux_default_middlewares = [
    (PendingTransactionMiddleware, "PendingTransactionMiddleware")
]

__all__ = [
    "PendingTransactionMiddleware",
    "WalletMiddlewareFactory",
    "conflux_default_middlewares"
]
