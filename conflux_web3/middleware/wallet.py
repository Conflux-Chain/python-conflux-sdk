from typing import (
    TYPE_CHECKING,
    Collection,
    Dict,
    Iterable,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    Any
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
from cfx_account._utils.validation import (
    validate_chain_id
)
from conflux_web3._utils.rpc_abi import (
    RPC
)
import warnings


if TYPE_CHECKING:
    from conflux_web3 import Web3

_PrivateKey = Union[LocalAccount, PrivateKey, HexStr, bytes]

def normalize_private_key_to_account(private_key: _PrivateKey, chain_id: int) -> LocalAccount:
    if isinstance(private_key, LocalAccount):
        if private_key.chain_id is None:
            private_key.chain_id = chain_id
        elif private_key.chain_id != chain_id:
            raise ValueError("chain_id and localAccount's chain_id is supposed to be consistent")
        return private_key
    return Account.from_key(private_key, chain_id)

class WalletMiddlewareFactory:
    def __init__(self, 
                chain_id: int,
                account_or_accounts: Union[Sequence[_PrivateKey], _PrivateKey]=[]
                ):
        """generate a wallet middleware object 
        with specific chain_id and accounts to use

        Args:
            chain_id (int, required): the network wallet to be used
            account_or_accounts (Union[Sequence[_PrivateKey], _PrivateKey], optional): 
                Any param could be private key source. 
                Both [account] and account can be served as "accounts" param.
                For LocalAccount type param, ensure chain_id and LocalAccount is consistent
        """
        validate_chain_id(chain_id)
        self._chain_id = chain_id
        self._accounts_map :Dict[str, LocalAccount] = {}
        
        if isinstance(account_or_accounts, Sequence):
            for account in account_or_accounts:
                self.add_account(account)
        else:
            self.add_account(account_or_accounts)
    
    @property
    def chain_id(self):
        return self._chain_id
    
    def __call__(self, make_request, w3: "Web3"):
        def inner(method, params):
            if method != RPC.cfx_sendTransaction:
                return make_request(method, params)
            
            transaction = params[0]
            if "from" not in transaction:
                return make_request(method, params)
            elif transaction.get("from") not in self._accounts_map:
                return make_request(method, params)
            
            account = self._accounts_map[transaction["from"]]
            raw_tx = account.sign_transaction(transaction).rawTransaction
            # because param formatting has been done before middleware process
            # we do the param formatting manually
            response = make_request(RPC.cfx_sendRawTransaction, [raw_tx.hex()])
            return response
        return inner
    
    def add_account(self, account):
        local_account = normalize_private_key_to_account(account, self.chain_id)
        # assert Address.has_network_prefix
        if local_account.address in self._accounts_map:
            warnings.warn(f"Duplicate account: {local_account.address} is already in the wallet, this operation overwrites the existed old account")
        self._accounts_map[local_account.address] = local_account

    def add_accounts(self, accounts):
        for account in accounts:
            self.add_account(account)
