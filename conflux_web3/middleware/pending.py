from typing import Any
from web3.types import RPCEndpoint
from conflux_web3._utils.rpc_abi import (
    RPC
)
from conflux_web3.types.transaction_hash import (
    TransactionHash
)

from conflux_web3.middleware.base import ConfluxWeb3Middleware
    
class PendingTransactionMiddleware(ConfluxWeb3Middleware):
    def response_processor(self, method: RPCEndpoint, response: Any):
        if method == RPC.cfx_sendTransaction or method == RPC.cfx_sendRawTransaction:
            if "result" in response:
                transaction_hash = TransactionHash(response["result"])
                transaction_hash.set_w3(self._w3)
                
                response["result"] = transaction_hash
        return response

