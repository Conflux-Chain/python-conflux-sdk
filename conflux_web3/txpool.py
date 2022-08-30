from web3.module import Module
from conflux_web3.method import ConfluxMethod
from conflux_web3.types import AddressParam
from conflux_web3._utils.rpc_abi import RPC

class Txpool(Module):
    _nextNonce = ConfluxMethod(
        RPC.txpool_nextNonce
    )
    
    def nextNonce(self, address: AddressParam):
        return self._nextNonce(address)
