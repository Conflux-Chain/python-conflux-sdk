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
    Tuple,
    Union,
    Dict
)
import functools
# from eth_typing import Address
from hexbytes import HexBytes

from web3.eth import BaseEth, Eth
from web3.method import (
    # DeprecatedMethod,
    Method,
    default_root_munger,
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

from conflux_module._utils.rpc_abi import RPC
from conflux_module._utils.method_formatters import cfx_request_formatters
from conflux_module.types import (
    Drip,
    BlockIdentifier,
    AddressParam
)
from conflux_module.contract import ConfluxContract
from conflux_module._utils.validation import validate_base32_address

class BaseCfx(BaseEth):
    _default_block: BlockIdentifier = "latest_state"
    
    def send_transaction_munger(self, transaction: TxParams) -> Tuple[TxParams]:
        if self.default_account:
            validate_base32_address(self.default_account)
        
        if 'from' not in transaction:
            transaction = assoc(transaction, 'from', self.default_account)

        return (transaction,)
    
    _get_status: Method[Callable[[], Any]] = Method(
        RPC.cfx_getStatus,
        mungers=None,
    )
    
    _get_balance: Method[Callable[..., HexStr]] = Method(
        RPC.cfx_getBalance,
        mungers=[BaseEth.block_id_munger],
    )
    
    _get_next_nonce: Method[Callable[..., HexStr]] = Method(
        RPC.cfx_getNextNonce,
        mungers=[BaseEth.block_id_munger],
    )
    
    _send_raw_transaction: Method[Callable[[Union[HexStr, bytes]], HexBytes]] = Method(
        RPC.cfx_sendRawTransaction,
        mungers=[default_root_munger],
        request_formatters=cfx_request_formatters
    )
    
    _send_transaction: Method[Callable[[TxParams], HexBytes]] = Method(
        RPC.cfx_sendTransaction,
        mungers=[send_transaction_munger],
        request_formatters=cfx_request_formatters
    )
    

class ConfluxClient(BaseCfx, Eth):
    account = CfxAccount
    address = CfxAddress
    defaultContractFactory = ConfluxContract
    
    @property
    def get_status(self) -> Dict[str, str]:
        """
            Returns the node status.
        Returns:
            Dict[str, str]: node status
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
    
    @functools.cached_property
    def chain_id(self) -> int:
        return int(self._get_status()["chainId"], 16)
    
    def get_balance(self, address: Union[str, AddressParam], block_identifier: BlockIdentifier = BaseCfx._default_block) -> Drip:
        return Drip(int(self._get_balance(address, block_identifier), 16))
    
    def get_next_nonce(self, address: Union[str, AddressParam], block_identifier: BlockIdentifier = BaseCfx._default_block) -> Drip:
        return Drip(int(self._get_next_nonce(address, block_identifier), 16))

    def send_raw_transaction(self, transaction: Union[HexStr, bytes]) -> HexBytes:
        return self._send_raw_transaction(transaction)
    
    def send_transaction(self, transaction: TxParams) -> HexBytes:
        return self._send_transaction(transaction)
    