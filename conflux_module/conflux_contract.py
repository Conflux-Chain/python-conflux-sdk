from typing import (
    Optional,
    cast
)
from eth_typing.evm import ChecksumAddress

from web3.contract import (
    Contract,
    ContractFunctions,
    ContractCaller,
    ContractEvents    
)

from cfx_address import Address as CfxAddress

from conflux_module.types import Base32Address
# from conflux_web3 import Web3
from conflux_module._utils.validation import validate_base32_address


class ConfluxContract(Contract):
    address: Base32Address = None  # type: ignore
    # base32_address: Base32Address = None # type: ignore
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

        self.functions = ContractFunctions(self.abi, self.web3, self.address)
        self.caller = ContractCaller(self.abi, self.web3, self.address)
        self.events = ContractEvents(self.abi, self.web3, self.address)
        self.fallback = Contract.get_fallback_function(self.abi, self.web3, self.address)
        self.receive = Contract.get_receive_function(self.abi, self.web3, self.address)