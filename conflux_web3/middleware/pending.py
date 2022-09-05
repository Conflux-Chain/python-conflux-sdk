from typing import TYPE_CHECKING
from conflux_web3._utils.rpc_abi import (
    RPC
)
from conflux_web3.types.transaction_hash import (
    TransactionHash
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

    
class PendingTransactionMiddleware:
    def __init__(self, make_request, w3: "Web3"):
        self._make_request = make_request
        self._w3 = w3
        
    def __call__(self, method, params):
        response = self._make_request(method, params)
        if method == RPC.cfx_sendTransaction or method == RPC.cfx_sendRawTransaction:
            if "result" in response:
                transaction_hash = TransactionHash(response["result"])
                transaction_hash.set_w3(self._w3)
                
                response["result"] = transaction_hash
        return response

