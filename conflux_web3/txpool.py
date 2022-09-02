from web3.module import Module
from conflux_web3.method import ConfluxMethod
from conflux_web3.types import AddressParam
from conflux_web3._utils.rpc_abi import RPC

class Txpool(Module):
    _next_nonce = ConfluxMethod(
        RPC.txpool_nextNonce
    )
    
    def next_nonce(self, address: AddressParam):
        return self._next_nonce(address)
