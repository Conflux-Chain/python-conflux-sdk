from typing import (
    TYPE_CHECKING,
    Dict,
    Optional,
    Sequence,
    Union,
)

from eth_typing import (
    HexStr
)

from eth_keys.datatypes import (
    PrivateKey,
)
from cfx_account import Account
from cfx_account.account import (
    LocalAccount
)
from cfx_address import Base32Address
from cfx_address.utils import validate_network_id as validate_chain_id
from cfx_address.utils import normalize_to
from conflux_web3._utils.rpc_abi import (
    RPC
)
import warnings


if TYPE_CHECKING:
    from conflux_web3 import Web3

_PrivateKey = Union[LocalAccount, PrivateKey, HexStr, bytes]
    

class WalletMiddleware:
    def __init__(self, 
                account_or_accounts: Union[Sequence[_PrivateKey], _PrivateKey]=[],
                forced_chain_id: Optional[int]=None,
                ):
        """
        generate a wallet middleware object 
        with specific chain_id and accounts to use

        :param Union[Sequence[_PrivateKey], _PrivateKey] account_or_accounts: Any param could be private key source. 
            Both [account] and account can be served as "accounts" param.
            For LocalAccount type param, ensure chain_id and LocalAccount is consistent. 
            Defaults to []
        :param int forced_chain_id: the network id of the wallet, all account will be set at the specified network, 
            and network checking will be applied to every added account. 
            If is None, then no default network id is set, and
        """
        if forced_chain_id is not None:
            validate_chain_id(forced_chain_id)

        self._chain_id = forced_chain_id
        self._accounts_map: Dict[str, LocalAccount] = {}
        
        if isinstance(account_or_accounts, Sequence):
            for account in account_or_accounts:
                self.add_account(account)
        else:
            self.add_account(account_or_accounts)
    
    @property
    def chain_id(self):
        return self._chain_id
    
    def normalize_private_key_to_account(self, private_key: _PrivateKey) -> LocalAccount:
        if isinstance(private_key, LocalAccount):
            local_account = private_key
            # if self._chain_id is set, check if local_account.network_id is same as self._network_id
            if self._chain_id:
                if local_account.network_id and local_account.network_id != self._chain_id:
                    raise ValueError("wallet's chain_id and local_account's chain_id is supposed to be consistent")
            private_key = local_account._private_key
            
        return Account.from_key(private_key, self._chain_id)
    
    def __call__(self, make_request, w3: "Web3"):
        def inner(method, params):
            if method != RPC.cfx_sendTransaction:
                return make_request(method, params)
            
            transaction = params[0]
            if "from" not in transaction:
                return make_request(method, params)
            # TODO: change to """transaction.get("from") not in self"""
            elif normalize_to(transaction.get("from"), self._chain_id) not in self._accounts_map:
                return make_request(method, params)
            
            account = self[transaction["from"]]
            raw_tx = account.sign_transaction(transaction).rawTransaction
            # because param formatting has been done before middleware process
            # we do the param formatting manually
            response = make_request(RPC.cfx_sendRawTransaction, [raw_tx.hex()])
            return response
        return inner
    
    def add_account(self, account):
        local_account = self.normalize_private_key_to_account(account)
        # assert Address.has_network_prefix
        if local_account.address in self._accounts_map:
            warnings.warn(f"Duplicate account: {local_account.address} is already in the wallet, this operation overwrites the existed old account")
        self._accounts_map[local_account.address] = local_account

    def add_accounts(self, accounts):
        for account in accounts:
            self.add_account(account)
    
    def __getitem__(self, address: str) -> LocalAccount:
        if self._chain_id is None:
            return self._accounts_map[normalize_to(address, None)]
        else:
            return self._accounts_map[address]


def construct_sign_and_send_raw_middleware(
    account_or_accounts: Union[Sequence[_PrivateKey], _PrivateKey], 
    forced_chain_id: Optional[int]=None
) -> WalletMiddleware:
    return WalletMiddleware(account_or_accounts, forced_chain_id)
