from typing import (
    TYPE_CHECKING,
    Optional,
)

from eth_utils.toolz import (
    partial,
)
from eth_typing import (
    ABI,
)

from web3.contract.base_contract import (
    BaseContractCaller,
)


from conflux_web3.types import (
    TxParam,
    AddressParam,
    EpochNumberParam,
)

from .function import (
    ConfluxContractFunctions,
)

if TYPE_CHECKING:
    from conflux_web3 import Web3
    

class ConfluxContractCaller(BaseContractCaller):
    def __init__(
        self,
        abi: ABI,
        w3: "Web3",
        address: AddressParam,
        transaction: Optional[TxParam] = None,
        block_identifier: EpochNumberParam = "latest_state",
        ccip_read_enabled: Optional[bool] = None,
        decode_tuples: Optional[bool] = False,
        contract_functions: Optional[ConfluxContractFunctions] = None,
    ) -> None:
        super().__init__(
            abi,
            w3,
            address, # type: ignore
            decode_tuples=decode_tuples
        )


        if self.abi:
            if transaction is None:
                transaction = {}

            if contract_functions is None:
                contract_functions = ConfluxContractFunctions(
                    abi, w3, address=address, decode_tuples=decode_tuples
                )

            self._functions = contract_functions._functions
            for fn in contract_functions.__iter__():
                caller_method = partial(
                    self.call_function,
                    fn,
                    transaction=transaction,
                    block_identifier=block_identifier,
                    ccip_read_enabled=ccip_read_enabled,
                )
                setattr(self, str(fn.abi_element_identifier), caller_method)
        

    def __call__(
        self,
        transaction: Optional[TxParam] = None,
        block_identifier: EpochNumberParam = "latest_state",
        ccip_read_enabled: Optional[bool] = None,
    ) -> "ConfluxContractCaller":
        if transaction is None:
            transaction = {}
        return type(self)(
            self.abi,
            self.w3, # type: ignore
            self.address,
            transaction=transaction,
            block_identifier=block_identifier,
            ccip_read_enabled=ccip_read_enabled,
            decode_tuples=self.decode_tuples,
        )
