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
        (name_to_address_middleware(w3), "name_to_address"),
        (PendingTransactionMiddleware, "PendingTransactionMiddleware"),
        (Wallet(), "wallet"),
    ]


__all__ = [
    "PendingTransactionMiddleware",
    "Wallet",
    "conflux_default_middlewares"
]
