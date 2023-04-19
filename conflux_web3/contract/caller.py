from typing import (
    TYPE_CHECKING,
    Optional,
)

from eth_utils.toolz import (
    partial,
)

from web3._utils.contracts import (
    parse_block_identifier,
)

from web3.contract.base_contract import (
    BaseContractCaller,
)
from web3.types import (
    ABI,
)

from web3._utils.abi import (
    filter_by_type,
)

from conflux_web3.types import (
    TxParam,
    AddressParam,
    EpochNumberParam,
)

from .function import (
    ConfluxContractFunction
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

            self._functions = filter_by_type("function", self.abi)
            for func in self._functions:
                fn: ConfluxContractFunction = ConfluxContractFunction.factory(
                    func["name"],
                    w3=self.w3,
                    contract_abi=self.abi,
                    address=self.address,
                    function_identifier=func["name"],
                    decode_tuples=decode_tuples,
                )

                block_id = parse_block_identifier(self.w3, block_identifier)
                caller_method = partial(
                    self.call_function,
                    fn,
                    transaction=transaction,
                    block_identifier=block_id,
                    ccip_read_enabled=ccip_read_enabled,
                    # decode_tuples=decode_tuples,
                )

                setattr(self, func["name"], caller_method)
        

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
