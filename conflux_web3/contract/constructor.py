from typing import (
    TYPE_CHECKING,
    Optional
)
from web3.contract import (
    ContractConstructor
)

from cfx_utils.decorators import (
    combomethod
)
from conflux_web3.types.transaction_hash import (
    TransactionHash
)
from conflux_web3.types import (
    TxParam,
    EpochNumberParam,
    EstimateResult
)
from conflux_web3._utils.transactions import (
    fill_transaction_defaults
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

class ConfluxContractConstructor(ContractConstructor):
    w3: "Web3"
    
    @combomethod
    def transact(self, transaction: Optional[TxParam] = None) -> TransactionHash:
        return super().transact(transaction)
    
    @combomethod
    def build_transaction(self, transaction: Optional[TxParam] = None) -> TxParam:
        built_transaction = self._build_transaction(transaction)
        return fill_transaction_defaults(self.w3, built_transaction)
    
    @combomethod
    def estimate_gas(
        self,
        transaction: Optional[TxParam] = None,
        block_identifier: Optional[EpochNumberParam] = None,
    ) -> EstimateResult:
        return self.estimate_gas_and_collateral(transaction, block_identifier)
    
    @combomethod
    def estimate_gas_and_collateral(
        self,
        transaction: Optional[TxParam] = None,
        block_identifier: Optional[EpochNumberParam] = None,
    ) -> EstimateResult:
        return super().estimate_gas(transaction, block_identifier)
