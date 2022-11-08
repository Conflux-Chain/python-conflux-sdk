from typing import (
    TYPE_CHECKING,
    Dict,
    Iterable,
    Optional,
    Sequence,
    Union,
    Callable,
    Any,
)
import warnings

from eth_keys.datatypes import (
    PrivateKey,
)

from cfx_utils.types import (
    HexAddress,
    TxDict,
)
from cfx_account.account import (
    LocalAccount,
    Account,
)
from cfx_address import (
    Base32Address
)
from cfx_address.utils import (
    validate_network_id as validate_chain_id,
    normalize_to
)
from conflux_web3._utils.cns import (
    resolve_if_cns_name,
)
from conflux_web3._utils.rpc_abi import (
    RPC
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

_PrivateKey = Union[LocalAccount, PrivateKey, str, bytes]


class Wallet:
    def __init__(self, 
                account_or_accounts: Union[Iterable[_PrivateKey], _PrivateKey]=[],
                forced_chain_id: Optional[int]=None,
                ):
        """
        generate a wallet middleware object with specific chain_id and accounts to use.
        Note: this CLASS is not a web3.middleware. 
        A Wallet-type INSTANCE is the actual middleware

        Parameters
        ----------
        account_or_accounts : Union[Sequence[_PrivateKey], _PrivateKey], optional, by default []
            Any param could be private key source. 
            Both [account] and account can be served as "accounts" param.
            For LocalAccount type param, ensure chain_id and LocalAccount is consistent. 
        forced_chain_id : Optional[int], optional, by default None
            The network id of the wallet, all account will be set at the specified network, 
            and network checking will be applied to every added account. 
            If is None, then no default network id is set, and this wallet can be used in any network.
        """
        if forced_chain_id is not None:
            validate_chain_id(forced_chain_id)

        self._chain_id = forced_chain_id
        self._accounts_map: Dict[str, LocalAccount] = {}
        
        if isinstance(account_or_accounts, Iterable):
            for account in account_or_accounts:
                self.add_account(account)
        else:
            self.add_account(account_or_accounts)
    
    @property
    def chain_id(self):
        return self._chain_id
    
    @property
    def forced_chain_id(self):
        return self._chain_id
    
    @forced_chain_id.setter
    def forced_chain_id(self, new_chain_id: Union[None, int]):
        """
        the forced chain id of the wallet.
        if set to not None, all account in the wallet will be converted to the corresponding network.
        After that, accounts from incompatible network cannot be added to this wallet,
        and signing requests from network other than forced_chain_id will be ignored 

        Parameters
        ----------
        new_chain_id : Union[None, int] 
            _description_
        """        
        self._chain_id = new_chain_id
        for old_address, account in self._accounts_map.copy().items():
            account.network_id = new_chain_id
            self._accounts_map.pop(old_address)
            self.add_account(account)
        self._chain_id = new_chain_id
    
    @property
    def accounts(self) -> Sequence[Union[Base32Address, HexAddress]]:
        """
        returns all accounts address in the wallet

        Returns
        -------
        Sequence[Union[Base32Address, HexAddress]]
            a sequence of Base32Address if wallet.forced_chain_id is not None
            or HexAddress if wallet.forced_chain_id is None
        """            
        return self._accounts_map.keys() # type: ignore
    
    
    def normalize_private_key_to_account(self, private_key: _PrivateKey) -> LocalAccount:
        if isinstance(private_key, LocalAccount):
            local_account = private_key
            # if self._chain_id is set, check if local_account.network_id is same as self._network_id
            if self._chain_id:
                if local_account.network_id and local_account.network_id != self._chain_id:
                    raise ValueError("wallet's chain_id and local_account's chain_id is supposed to be consistent")
            private_key = local_account._private_key
        # any account added to wallet is a brand new object
        return Account.from_key(private_key, self._chain_id)
    
    def __call__(self, make_request: Callable[..., Dict[str, Any]], w3: "Web3"):
        def inner(method: str, params: Sequence[Any]):
            if method != RPC.cfx_sendTransaction:
                return make_request(method, params)
            
            transaction: TxDict = params[0]
            if "from" not in transaction:
                return make_request(method, params)
            else:
                transaction["from"] = resolve_if_cns_name(w3, transaction["from"])
                if transaction["from"] not in self:
                    return make_request(method, params)
            
            account = self[transaction["from"]]
            raw_tx = account.sign_transaction(transaction).rawTransaction
            # because param formatting has been done before middleware process
            # we do the param formatting manually
            response = make_request(RPC.cfx_sendRawTransaction, [raw_tx.hex()])
            return response
        return inner

    def add_account(self, account: _PrivateKey):
        local_account = self.normalize_private_key_to_account(account)
        # assert Address.has_network_prefix
        if local_account.address in self._accounts_map:
            warnings.warn(f"Duplicate account: {local_account.address} is already in the wallet, this operation overwrites the existed old account")
        self._accounts_map[local_account.address] = local_account

    def add_accounts(self, accounts: Iterable[_PrivateKey]):
        for account in accounts:
            self.add_account(account)
    
    def __getitem__(self, address: str) -> LocalAccount:
        if self._chain_id is None:
            return self._accounts_map[normalize_to(address, None)]
        else:
            return self._accounts_map[address]
    
    def __contains__(self, address: str) -> bool:
        try:
            self[address]
            return True
        except KeyError:
            return False


def construct_sign_and_send_raw_middleware(
    account_or_accounts: Union[Sequence[_PrivateKey], _PrivateKey], 
    forced_chain_id: Optional[int]=None
) -> Wallet:
    return Wallet(account_or_accounts, forced_chain_id)
