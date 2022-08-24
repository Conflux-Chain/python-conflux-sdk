from typing import (
    TYPE_CHECKING,
    Optional,
)

from web3.contract import (
    BaseContractCaller,
)
from web3.types import (
    ABI,
    CallOverride
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
    ) -> None:
        super().__init__(
            abi=abi,
            w3=w3,
            address=address, # type: ignore
            transaction=transaction, # type: ignore
            block_identifier=block_identifier, # type: ignore
            ccip_read_enabled=ccip_read_enabled,
            contract_function_class=ConfluxContractFunction,
        )

    def __call__(
        self,
        transaction: Optional[TxParam] = None,
        block_identifier: EpochNumberParam = "latest_state",
        state_override: Optional[CallOverride] = None,
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
        )
