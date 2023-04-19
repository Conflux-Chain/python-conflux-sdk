from typing import (
    TYPE_CHECKING,
    cast,
    Any,
    Optional,
)

from web3._utils.datatypes import (
    PropertyCheckingFactory,
)

from web3.contract.contract import (
    BaseContractFunctions,
    ContractFunction,
)

from web3.contract.contract import (
    call_contract_function
)

from web3.types import (
    ABI,
    ABIFunction,
    FunctionIdentifier,
    CallOverride
)

from cfx_utils.token_unit import (
    to_int_if_drip_units
)
from cfx_address import (
    Base32Address
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
    fill_transaction_defaults,
)
from conflux_web3._utils.normalizers import (
    addresses_to_verbose_base32
)

if TYPE_CHECKING:
    from conflux_web3 import Web3
    from conflux_web3.types.transaction_hash import TransactionHash

def build_transaction_for_function(
        address: Base32Address,
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
        address, # type: ignore
        web3,
        fn_identifier=function_name, # type: ignore
        contract_abi=contract_abi,
        fn_abi=fn_abi,
        transaction=transaction,  # type: ignore
        fn_args=args,
        fn_kwargs=kwargs,
    ) 

    prepared_transaction = fill_transaction_defaults(web3, prepared_transaction)

    return prepared_transaction  # type: ignore

class ConfluxContractFunction(ContractFunction):
    w3: "Web3"
    address: Base32Address
    
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
            self.address, # type: ignore
            # self._return_data_normalizers,
            [
                addresses_to_verbose_base32(self.w3.cfx.chain_id), # type: ignore
            ],
            self.function_identifier,
            call_transaction,
            block_identifier, # type: ignore
            self.contract_abi,
            self.abi,
            state_override,
            ccip_read_enabled,
            self.decode_tuples,
            *self.args,
            **self.kwargs,
        )

    def transact(self, transaction: Optional[TxParam] = None) -> "TransactionHash":
        if transaction and "value" in transaction:
            transaction["value"] = to_int_if_drip_units(transaction["value"])
        return super().transact(transaction) # type: ignore

    @classmethod
    def factory(cls, class_name: str, **kwargs: Any) -> "ConfluxContractFunction":
        return cast(ConfluxContractFunction, PropertyCheckingFactory(class_name, (cls,), kwargs)(kwargs.get("abi")))


class ConfluxContractFunctions(BaseContractFunctions):
    def __init__(
        self,
        abi: ABI,
        w3: "Web3",
        address: Optional[AddressParam] = None,
        decode_tuples: Optional[bool] = False,
    ) -> None:
        super().__init__(
            abi,
            w3,
            ConfluxContractFunction,
            address, # type: ignore
            decode_tuples
        )
    
    def __getattr__(self, function_name: str) -> "ConfluxContractFunction":
        return super().__getattr__(function_name) # type: ignore
