from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    cast
)
from eth_typing.evm import ChecksumAddress
from web3.contract import (
    BaseContractFunctions,
    ContractFunction,
    Contract,
    ContractCaller,
    ContractEvents
    
)
from web3.types import (
    ABI,
    # ABIEvent,
    ABIFunction,
    # BlockIdentifier,
    # CallOverrideParams,
    # EventData,
    FunctionIdentifier,
    # LogReceipt,
    TxParams,
    # TxReceipt,
)

from cfx_address import Address as CfxAddress

from conflux_web3.types import Base32Address
from conflux_web3._utils.validation import validate_base32_address
from conflux_web3._utils.contracts import prepare_transaction


if TYPE_CHECKING:
    from conflux_web3 import Web3


class ConfluxContractFunction(ContractFunction):
    w3: "Web3"
    
    def build_transaction(self, transaction: Optional[TxParams] = None) -> TxParams:
        built_transaction = self._build_transaction(transaction)
        return build_transaction_for_function(
            self.address,
            self.w3,
            self.function_identifier,
            built_transaction,
            self.contract_abi,
            self.abi,
            *self.args,
            **self.kwargs,
        )


class ConfluxContractFunctions(BaseContractFunctions):
    def __init__(
        self,
        abi: ABI,
        w3: "Web3",
        address: Optional[Base32Address] = None,
    ) -> None:
        super().__init__(abi, w3, ConfluxContractFunction, address)  # type: ignore
     
def build_transaction_for_function(
        address: ChecksumAddress,
        web3: 'Web3',
        function_name: Optional[FunctionIdentifier] = None,
        transaction: Optional[TxParams] = None,
        contract_abi: Optional[ABI] = None,
        fn_abi: Optional[ABIFunction] = None,
        *args: Any,
        **kwargs: Any) -> TxParams:
    """Builds a dictionary with the fields required to make the given transaction

    Don't call this directly, instead use :meth:`Contract.build_transaction`
    on your contract instance.
    """
    prepared_transaction = prepare_transaction(
        address,
        web3,
        fn_identifier=function_name, # type: ignore
        contract_abi=contract_abi,
        fn_abi=fn_abi,
        transaction=transaction,
        fn_args=args,
        fn_kwargs=kwargs,
    ) 

    # TODO
    # prepared_transaction = fill_transaction_defaults(web3, prepared_transaction)

    return prepared_transaction


class ConfluxContract(Contract):
    address: Base32Address
    w3: 'Web3'
    _hex_address: ChecksumAddress
    functions: ConfluxContractFunctions
    
    def __init__(self, address: Base32Address) -> None:
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
            self._hex_address = cast(ChecksumAddress, CfxAddress(address).eth_checksum_address)

        if not self.address:
            raise TypeError("The address argument is required to instantiate a contract.")

        self.functions = ConfluxContractFunctions(self.abi, self.w3, self.address)
        self.caller = ContractCaller(self.abi, self.w3, self.address) # type: ignore
        self.events = ContractEvents(self.abi, self.w3, self.address) # type: ignore
        self.fallback = Contract.get_fallback_function(self.abi, self.w3, self.address) # type: ignore
        self.receive = Contract.get_receive_function(self.abi, self.w3, self.address) # type: ignore
