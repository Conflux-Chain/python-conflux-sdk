from typing import TYPE_CHECKING, Optional, Type, Union, cast
from hexbytes import HexBytes
from web3._utils.method_formatters import (
    to_hexbytes
)
from conflux_web3.types import (
    TxReceipt,
    TxData,
)
from conflux_web3.exceptions import (
    NoWeb3Exception
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

def requires_web3(func):
    def inner(self, *args, **kwargs):
        if self._w3 is None:
            raise NoWeb3Exception("No web3 instance is attached to transaction hash."
                        "Use transactionHash.set_w3() to attach a w3 instance")
        return func(self, *args, **kwargs)
    return inner

class TransactionHash(HexBytes):
    _w3: "Web3" = None # type: ignore
    
    def __new__(cls: Type[bytes], val: Union[bool, bytearray, bytes, int, str]) -> "TransactionHash":
        val = to_hexbytes(32, val)
        return cast(TransactionHash, super().__new__(cls, val)) # type: ignore
    
    def set_w3(self, w3: "Web3"):
        self._w3 = w3
    
    # @property
    # def status(self):
    #     pass
    
    def wait_till(self, target_status: str):
        pass
    
    @requires_web3
    def wait_till_mined(self, timeout: float = 60, poll_latency: float = 0.5) -> TxData:
        return self._w3.cfx.wait_for_transaction_data(self, timeout, poll_latency)
    
    @requires_web3
    def wait_till_executed(self, timeout: float = 300, poll_latency: float = 0.5) -> TxReceipt:
        return self._w3.cfx.wait_for_transaction_receipt(self, timeout, poll_latency) 
    
    @requires_web3
    def wait_till_confirmed(self, timeout: float = 600, poll_latency: float = 0.5) -> TxReceipt:
        return self._w3.cfx.wait_for_transaction_confirmation(self, timeout, poll_latency) 
    
    @requires_web3
    def wait_till_finalized(self) -> TxReceipt: # type: ignore
        # warnings.warn("Several minutes are required to finalize a transaction", UserWarning)
        pass
    
    def __repr__(self) -> str:
        return f"TransactionHash({self.hex()!r})"
    