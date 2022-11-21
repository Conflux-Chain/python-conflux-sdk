from typing import (
    Callable,
    Union
)

from web3.module import Module
from cfx_address import Base32Address

from conflux_web3.method import ConfluxMethod
from conflux_web3._utils.rpc_abi import RPC

class Txpool(Module):
    _next_nonce: ConfluxMethod[Callable[[Union[Base32Address, str]], int]] = ConfluxMethod(
        RPC.txpool_nextNonce
    )
    
    def next_nonce(self, address: Union[Base32Address, str]) -> int:
        return self._next_nonce(address)
