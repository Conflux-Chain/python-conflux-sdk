from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    cast
)

from web3.contract import (
    Contract,
)

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

from cfx_address import (
    Base32Address,
)
from cfx_address.utils import (
    validate_address_agaist_network_id,
)

from cfx_utils.exceptions import (
    InvalidEpochNumebrParam,
    Base32AddressNotMatch,
)
from conflux_web3.types import (
    Base32Address,
    AddressParam,
    EpochNumberParam,
    EpochLiteral,
)
from conflux_web3.contract.function import (
    ConfluxContractFunction,
    ConfluxContractFunctions,
)
from conflux_web3.contract.caller import (
    ConfluxContractCaller
)
from conflux_web3.contract.event import (
    ConfluxContractEvents
)
from conflux_web3.contract.constructor import (
    ConfluxContractConstructor
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

# used to hook web3.contract.parse_block_identifier
# hook is activated in conflux_web3._hook
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


class ConfluxContract(Contract):
    address: AddressParam
    w3: 'Web3'
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

        # address should match chainId
        if address:             
            validate_address_agaist_network_id(address, self.w3.cfx.chain_id, True)
            address = Base32Address(address, self.w3.cfx.chain_id)
            if address.address_type != "contract" and address.address_type != "builtin":
                raise Base32AddressNotMatch(f"expected an address of contract type or builtin type"
                                            f"receives {address} of {address.address_type}")
            self.address = Base32Address(address, self.w3.cfx.chain_id)

        if not self.address:
            raise TypeError("The address argument is required to instantiate a contract.")

        self.functions = ConfluxContractFunctions(self.abi, self.w3, self.address)
        self.caller = ConfluxContractCaller(self.abi, self.w3, self.address) 
        self.events = ConfluxContractEvents(self.abi, self.w3, self.address)
        self.fallback = Contract.get_fallback_function(self.abi, self.w3, ConfluxContractFunction, self.address) # type: ignore
        self.receive = Contract.get_receive_function(self.abi, self.w3, ConfluxContractFunction, self.address) # type: ignore

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

    @classmethod
    def constructor(cls, *args: Any, **kwargs: Any) -> "ConfluxContractConstructor":
        """
        :param args: The contract constructor arguments as positional arguments
        :param kwargs: The contract constructor arguments as keyword arguments
        :return: a contract constructor object
        """
        if cls.bytecode is None:
            raise ValueError(
                "Cannot call constructor on a contract that does not have "
                "'bytecode' associated with it"
            )

        return ConfluxContractConstructor(cls.w3, cls.abi, cls.bytecode, *args, **kwargs)
