"""
The MIT License (MIT)

Copyright (c) 2016 Piper Merriam

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from typing import (
    Any,
    Callable,
    Optional,
    Sequence,
    Tuple,
    Union,
    Dict,
    cast
)
import functools
# from eth_typing import Address
from hexbytes import HexBytes

from web3.eth import (
    BaseEth, 
    Eth
)
from web3._utils.empty import (
    Empty,
    empty,
)
from web3.method import (
    # DeprecatedMethod,
    default_root_munger,
)
from web3.datastructures import (
    AttributeDict,
)
from web3.types import (
    # ENS,
    # BlockData,
    # CallOverrideParams,
    # FeeHistory,
    # FilterParams,
    # GasPriceStrategy,
    # LogReceipt,
    # MerkleProof,
    # Nonce,
    # SignedTx,
    # SyncStatus,
    # TxData,
    TxParams,
    # TxReceipt,
    # Uncle,
    # Wei,
    # _Hash32,
)

from eth_typing.encoding import HexStr
from eth_utils.toolz import assoc  # type: ignore

from cfx_address import Address as CfxAddress
from cfx_account import Account as CfxAccount
from cfx_account.account import LocalAccount


from conflux_web3._utils.rpc_abi import RPC
from conflux_web3._utils.method_formatters import cfx_request_formatters
from conflux_web3.types import (
    Drip,
    BlockIdentifier,
    AddressParam,
    EstimateResult,
    Base32Address
)
from conflux_web3.contract import ConfluxContract
from conflux_web3._utils.validation import validate_base32_address
from conflux_web3.method import (
    ConfluxMethod
)

class BaseCfx(BaseEth):
    _default_block: BlockIdentifier = "latest_state"
    _default_account: Union[Base32Address, str, Empty] = empty

    
    @property
    def default_account(self) -> Union[Base32Address, str, Empty]:
        """default account address rather than a local account with private key
        """
        return self._default_account

    @default_account.setter
    def default_account(self, account: Union[Base32Address, str, LocalAccount, Empty]) -> None:
        """set default account address
        Args:
            account: an address or a local account (but only address field works)
        """
        if getattr(account, "address", None):
            validate_base32_address(account.address) # type: ignore
            self._default_account = account.address # type: ignore
        else:
            validate_base32_address(account)
            self._default_account = account # type: ignore
    
    
    def send_transaction_munger(self, transaction: TxParams) -> Tuple[TxParams]:
        if self.default_account:
            validate_base32_address(self.default_account)
        
        if 'from' not in transaction:
            transaction = assoc(transaction, 'from', self.default_account)

        return (transaction,)
    
    _get_status: ConfluxMethod[Callable[[], Dict]] = ConfluxMethod(
        RPC.cfx_getStatus,
    )
    
    _gas_price: ConfluxMethod[Callable[[], int]] = ConfluxMethod(
        RPC.cfx_gasPrice,
    )
    
    _estimate_gas: None
    
    def estimate_gas_and_collateral_munger(
        self, transaction: Union[TxParams, dict[str, Any]], block_identifier: Optional[BlockIdentifier]=None
    ) -> Sequence[Union[TxParams, dict[str, Any], BlockIdentifier]]:
        if "from" not in transaction and self.default_account:
            transaction = assoc(transaction, "from", self.default_account)

        if block_identifier is None:
            params = [transaction]
        else:
            params = [transaction, block_identifier]

        return params
    
    _estimate_gas_and_collateral: ConfluxMethod[Callable[..., EstimateResult]] = ConfluxMethod(
        RPC.cfx_estimateGasAndCollateral, mungers=[estimate_gas_and_collateral_munger]
    )
    
    _get_balance: ConfluxMethod[Callable[..., int]] = ConfluxMethod(
        RPC.cfx_getBalance,
    )
    
    _epoch_number: ConfluxMethod[Callable[..., int]] = ConfluxMethod(
        RPC.cfx_epochNumber,
    )
    
    _get_next_nonce: ConfluxMethod[Callable[..., int]] = ConfluxMethod(
        RPC.cfx_getNextNonce,
    )
    
    _send_raw_transaction: ConfluxMethod[Callable[[Union[HexStr, bytes]], HexBytes]] = ConfluxMethod(
        RPC.cfx_sendRawTransaction,
        mungers=[default_root_munger],
    )
    
    _send_transaction: ConfluxMethod[Callable[[TxParams], HexBytes]] = ConfluxMethod(
        RPC.cfx_sendTransaction,
        mungers=[send_transaction_munger],
    )
    

class ConfluxClient(BaseCfx, Eth):
    account = CfxAccount
    address = CfxAddress
    defaultContractFactory = ConfluxContract
    
    def get_status(self) -> AttributeDict:
        """
            Returns the node status.
        Returns:
            AttributeDict: node status
            e.g.
            {
                "bestHash": "0xe4bf02ad95ad5452c7676d3dfc2e57fde2a70806c2e68231c58c77cdda5b7c6c",
                "chainId": "0x1",
                "networkId": "0x1",
                "blockNumber": "0x1a80325",
                "epochNumber": "0xaf28ab",
                "latestCheckpoint": "0xada520",
                "latestConfirmed": "0xaf2885",
                "latestState": "0xaf28a7",
                "latestFinalized": "0x2a420c",
                "ethereumSpaceChainId": "0x22b9",
                "pendingTxNumber": "0x0"
            },
        """
        return self._get_status()
    
    @property
    def gas_price(self) -> Drip:
        return self._gas_price()
    
    @property
    def epoch_number(self) -> int:
        return self._epoch_number()
    
    @property
    def chain_id(self) -> int:
        return self._get_status()["chainId"]
    
    def get_balance(self, address: Union[str, AddressParam], block_identifier: BlockIdentifier = None) -> Drip:
        return Drip(self._get_balance(address, block_identifier))
    
    def get_next_nonce(self, address: Union[str, AddressParam], block_identifier: BlockIdentifier = None) -> Drip:
        return self._get_next_nonce(address, block_identifier)

    def estimate_gas_and_collateral(self, transaction: Union[TxParams, dict], block_identifier: Optional[BlockIdentifier]=None):
        return self._estimate_gas_and_collateral(transaction, block_identifier)

    def send_raw_transaction(self, transaction: Union[HexStr, bytes]) -> HexBytes:
        return self._send_raw_transaction(transaction)
    
    def send_transaction(self, transaction: TxParams) -> HexBytes:
        return self._send_transaction(transaction)
    