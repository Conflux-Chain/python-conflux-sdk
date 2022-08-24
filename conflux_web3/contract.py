import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Optional,
    cast
)

from eth_typing.evm import (
    ChecksumAddress
)
from eth_utils.functional import (
    to_tuple
)
from web3.contract import (
    BaseContractFunctions,
    BaseContractCaller,
    BaseContractEvent,
    ContractFunction,
    Contract,
    BaseContractEvents,
    call_contract_function
)
from web3.types import (
    ABI,
    # ABIEvent,
    ABIFunction,
    # CallOverrideParams,
    # EventData,
    FunctionIdentifier,
    # LogReceipt,
    # TxParams,
    # TxReceipt,
    CallOverride
)
from web3.logs import (
    DISCARD,
    IGNORE,
    STRICT,
    WARN,
)
from web3._utils.events import (
    EventLogErrorFlags,
)

from web3 import contract
from web3._utils.blocks import (
    is_hex_encoded_block_hash,
)
from web3._utils.normalizers import (
    normalize_abi,
    normalize_bytecode,
)
from web3._utils.datatypes import (
    PropertyCheckingFactory,
)
from web3.exceptions import (
    InvalidEventABI,
    LogTopicError,
    MismatchedABI,
)

from cfx_address import (
    Base32Address,
)
from cfx_utils.exceptions import (
    InvalidEpochNumebrParam
)
from conflux_web3.types import (
    Base32Address,
    TxParam,
    AddressParam,
    EpochNumberParam,
    EpochLiteral,
    TxReceipt,
    EventData,
)
from conflux_web3._utils.validation import (
    validate_base32_address,
)
from conflux_web3._utils.contracts import (
    prepare_transaction,
)
from conflux_web3._utils.transactions import (
    fill_formal_transaction_defaults,
)
from conflux_web3._utils.decorators import (
    conditional_func,
    cfx_web3_condition,
)
from conflux_web3._utils.events import (
    cfx_get_event_data
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

# begin hacking 
def cfx_parse_block_identifier(
    w3: "Web3", block_identifier: EpochNumberParam
) -> EpochNumberParam:
    if isinstance(block_identifier, int):
        return block_identifier
    elif block_identifier in EpochLiteral.__args__: # type: ignore
        return block_identifier
    elif isinstance(block_identifier, bytes) or is_hex_encoded_block_hash(
        block_identifier
    ):
        # r = 
        # assert r is not None
        return w3.cfx.get_block_by_hash(block_identifier)["epochNumber"] # type: ignore
    else:
        raise InvalidEpochNumebrParam

contract.parse_block_identifier = conditional_func(
    cfx_parse_block_identifier,
    cfx_web3_condition
)(contract.parse_block_identifier)

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

class ConfluxContractEvent(BaseContractEvent):
    
    w3: "Web3"
    
    @to_tuple
    def _parse_logs(
        self, txn_receipt: TxReceipt, errors: EventLogErrorFlags
    ) -> Iterable[EventData]:
        try:
            errors.name
        except AttributeError:
            raise AttributeError(
                f"Error flag must be one of: {EventLogErrorFlags.flag_options()}"
            )

        for log in txn_receipt["logs"]:
            try:
                rich_log = cfx_get_event_data(self.w3.codec, self.abi, log, self.w3.cfx.chain_id)
            except (MismatchedABI, LogTopicError, InvalidEventABI, TypeError) as e:
                if errors == DISCARD:
                    continue
                elif errors == IGNORE:
                    # type ignores b/c rich_log set on 1092 conflicts with mutated types
                    new_log = MutableAttributeDict(log)  # type: ignore
                    new_log["errors"] = e
                    rich_log = AttributeDict(new_log)  # type: ignore
                elif errors == STRICT:
                    raise e
                else:
                    warnings.warn(
                        f"The log with transaction hash: {log['transactionHash']!r} "
                        f"and logIndex: {log['logIndex']} encountered the following "
                        f"error during processing: {type(e).__name__}({e}). It has "
                        "been discarded."
                    )
                    continue
            yield rich_log
    

# hacking web3._utils.events.get_event_data in conflux_web3._utils.events
class ConfluxContractEvents(BaseContractEvents):
    def __init__(
        self, abi: ABI, w3: "Web3", address: Optional[AddressParam] = None
    ) -> None:
        super().__init__(abi, w3, ConfluxContractEvent, address) # type: ignore


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


class ConfluxContract(Contract):
    address: AddressParam
    w3: 'Web3'
    _hex_address: ChecksumAddress
    functions: ConfluxContractFunctions
    caller: "ConfluxContractCaller"
    events: "ConfluxContractEvents"
    
    def __init__(self, address: AddressParam) -> None:
        """Create a new smart contract proxy object.

        :param address: Base32 Contract address 
        """
        if self.w3 is None:
            raise AttributeError(
                'The `Contract` class has not been initialized.  Please use the '
                '`web3.contract` interface to create your contract class.'
            )

        if address:
            # TODO: validate is a contract address
            # TODO: validate chainid matches
            validate_base32_address(address)
            self.address = address
            self._hex_address = cast(ChecksumAddress, Base32Address(address).eth_checksum_address)

        if not self.address:
            raise TypeError("The address argument is required to instantiate a contract.")

        self.functions = ConfluxContractFunctions(self.abi, self.w3, self.address)
        self.caller = ConfluxContractCaller(self.abi, self.w3, self.address) 
        self.events = ConfluxContractEvents(self.abi, self.w3, self.address)
        self.fallback = Contract.get_fallback_function(self.abi, self.w3, self.address) # type: ignore
        self.receive = Contract.get_receive_function(self.abi, self.w3, self.address) # type: ignore

    @classmethod
    def factory(cls, w3: "Web3", class_name: Optional[str] = None, **kwargs: Any) -> "Contract":
        kwargs["w3"] = w3

        normalizers = {
            "abi": normalize_abi,
            # "address": partial(normalize_address, kwargs["w3"].ens),
            "bytecode": normalize_bytecode,
            "bytecode_runtime": normalize_bytecode,
        }

        contract = cast(
            ConfluxContract,
            PropertyCheckingFactory(
                class_name or cls.__name__,
                (cls,),
                kwargs,
                normalizers=normalizers,
            ),
        )
        contract.functions = ConfluxContractFunctions(contract.abi, contract.w3)
        contract.caller = ConfluxContractCaller(contract.abi, contract.w3, contract.address)
        contract.events = ConfluxContractEvents(contract.abi, contract.w3)
        contract.fallback = Contract.get_fallback_function(
            contract.abi,
            contract.w3,
            ConfluxContractFunction,
        )
        contract.receive = Contract.get_receive_function(
            contract.abi,
            contract.w3,
            ConfluxContractFunction,
        )

        return contract
