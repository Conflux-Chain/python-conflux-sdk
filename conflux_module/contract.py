
from typing import (
    Any,
    Optional,
    cast
)
from eth_typing.evm import ChecksumAddress
from web3 import contract
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

from conflux_module.types import Base32Address
from conflux_module._utils.validation import validate_base32_address
from conflux_module._utils.contracts import prepare_transaction
from conflux_module._utils.decorators import (
    temp_alter_module_variable,
    cfx_web3_condition,
    conditional_func
)
        
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
        fn_identifier=function_name,
        contract_abi=contract_abi,
        fn_abi=fn_abi,
        transaction=transaction,
        fn_args=args,
        fn_kwargs=kwargs,
    )

    # TODO
    # prepared_transaction = fill_transaction_defaults(web3, prepared_transaction)

    return prepared_transaction

contract.build_transaction_for_function = conditional_func(
    build_transaction_for_function, 
    cfx_web3_condition
)(contract.build_transaction_for_function)


class ConfluxContract(contract.Contract):
    address: Base32Address = None  # type: ignore
    web3: 'Web3' = None # type: ignore
    _hex_address: ChecksumAddress = None # type: ignore
    
    def __init__(self, address: Base32Address) -> None:
        """Create a new smart contract proxy object.

        :param address: Base32 Contract address 
        """
        if self.web3 is None:
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

        self.functions = contract.ContractFunctions(self.abi, self.web3, self.address)
        self.caller = contract.ContractCaller(self.abi, self.web3, self.address)
        self.events = contract.ContractEvents(self.abi, self.web3, self.address)
        self.fallback = contract.Contract.get_fallback_function(self.abi, self.web3, self.address)
        self.receive = contract.Contract.get_receive_function(self.abi, self.web3, self.address)
