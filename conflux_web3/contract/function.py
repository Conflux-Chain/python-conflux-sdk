from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
)

from eth_typing.evm import (
    ChecksumAddress
)
from web3.contract import (
    BaseContractFunctions,
    ContractFunction,
    call_contract_function
)
from web3.types import (
    ABI,
    ABIFunction,
    FunctionIdentifier,
    CallOverride
)

from conflux_web3.types import (
    TxParam,
    AddressParam,
    EpochNumberParam,
)
from conflux_web3._utils.contracts import (
    prepare_transaction,
)
from conflux_web3._utils.transactions import (
    fill_formal_transaction_defaults,
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

def build_transaction_for_function(
        address: ChecksumAddress,
        web3: 'Web3',
        function_name: Optional[FunctionIdentifier] = None,
        transaction: Optional[TxParam] = None,
        contract_abi: Optional[ABI] = None,
        fn_abi: Optional[ABIFunction] = None,
        *args: Any,
        **kwargs: Any) -> TxParam:
    """Builds a dictionary with the fields required to make the given transaction

    Don't call this directly, instead use :meth:`Contract.build_transaction`
    on your contract instance.
    """
    prepared_transaction:TxParam = prepare_transaction(
        address,
        web3,
        fn_identifier=function_name, # type: ignore
        contract_abi=contract_abi,
        fn_abi=fn_abi,
        transaction=transaction,  # type: ignore
        fn_args=args,
        fn_kwargs=kwargs,
    ) 

    prepared_transaction = fill_formal_transaction_defaults(web3, prepared_transaction)

    return prepared_transaction  # type: ignore

class ConfluxContractFunction(ContractFunction):
    w3: "Web3"
    
    def __call__(self, *args: Any, **kwargs: Any) -> "ConfluxContractFunction":
        return super().__call__(*args, **kwargs) # type: ignore
    
    def build_transaction(self, transaction: Optional[TxParam] = None) -> TxParam:
        built_transaction = self._build_transaction(transaction)  # type: ignore
        return build_transaction_for_function(
            self.address,
            self.w3,
            self.function_identifier,
            built_transaction,  # type: ignore
            self.contract_abi,
            self.abi,
            *self.args,
            **self.kwargs,
        )
    
    def call(self,
            transaction: Optional[TxParam] = None,
            block_identifier: Optional[EpochNumberParam] = "latest_state",
            state_override: Optional[CallOverride] = None,
            ccip_read_enabled: Optional[bool] = None) -> Any:
        call_transaction = self._get_call_txparams(transaction) # type: ignore

        # block_id = parse_block_identifier(self.w3, block_identifier)

        return call_contract_function(
            self.w3,
            self.address,
            self._return_data_normalizers, # type: ignore
            self.function_identifier,
            call_transaction,
            block_identifier, # type: ignore
            self.contract_abi,
            self.abi,
            state_override,
            ccip_read_enabled,
            *self.args,
            **self.kwargs,
        )


class ConfluxContractFunctions(BaseContractFunctions):
    def __init__(
        self,
        abi: ABI,
        w3: "Web3",
        address: Optional[AddressParam] = None,
    ) -> None:
        super().__init__(abi, w3, ConfluxContractFunction, address)  # type: ignore
    
    def __getattr__(self, function_name: str) -> "ConfluxContractFunction":
        return super().__getattr__(function_name) # type: ignore
