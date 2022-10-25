from copy import deepcopy
from typing import (
    Type,
    cast,
    Optional,
    Sequence,
    Tuple,
    TYPE_CHECKING,
    Union,
)
from typing_extensions import (
    Self
)

from hexbytes import (
    HexBytes
)

from ens import (
    ENS,
)
from ens.utils import (
    default,
    normal_name_to_hash,
    raw_name_to_hash,
    label_to_hash,
    normalize_name,
    is_none_or_zero_address, # already hooked
)
from ens.exceptions import (
    UnauthorizedError,
    ResolverNotFound,
)

from cfx_address import (
    Base32Address,
)
from cfx_address.utils import (
    normalize_to
)
from cns.exceptions import (
    InterfaceNotSupported,
    MissingTransactionSender,
    UnstableAPI,
)
from cns.utils import (
    init_web3
)

if TYPE_CHECKING:
    from conflux_web3 import Web3  # noqa: F401
    from conflux_web3.contract import (  # noqa: F401
        ConfluxContract,
    )
    from web3.providers.base import (  # noqa: F401
        BaseProvider,
    )
    from conflux_web3.types import (  # noqa: F401
        Middleware,
        TxParam,
        AddressParam,
    )
    from conflux_web3.types.transaction_hash import (
        TransactionHash
    )

class CNS(ENS):
    w3: "Web3"
    ens: "ConfluxContract"
    allow_unstable_api: bool = False
    _resolver_contract: Type["ConfluxContract"]

    def __init__(
        self,
        provider: "BaseProvider" = cast("BaseProvider", default),
        addr: Optional[Union[Base32Address, str]]=None,
        middlewares: Optional[Sequence[Tuple["Middleware", str]]] = None,
        default_account: Optional[Base32Address] = None,
    ) -> None:
        """
        :param provider: a single provider used to connect to Ethereum
        :type provider: instance of `web3.providers.base.BaseProvider`
        :param hex-string addr: the address of the ENS registry on-chain.
            If not provided, ENS.py will default to the mainnet ENS
            registry address.
        """
        self.w3 = init_web3(provider, middlewares, default_account)

        # if addr is None, propriate address will be automatically selected
        # see conflux_web3.contract.metadata.DEPLOYMENT_INFO for more infomation
        if addr:
            self.ens = self.w3.cfx.contract(addr, name="ENS")
        else:
            self.ens = self.w3.cfx.contract(name="ENS", with_deployment_info=True)
        
        self._resolver_contract = self.w3.cfx.contract(name="RESOLVER", with_deployment_info=False)
        self._reverse_resolver_contract = self.w3.cfx.contract(name="REVERSE_RESOLVER", with_deployment_info=False)
        self._name_wrapper_contract = self.w3.cfx.contract(name="NameWrapper", with_deployment_info=False)
    
    def address(self, name: str) -> Union[Base32Address, None]:
        address = self._resolve(name, "addr")
        return cast(Base32Address, address)
    
    def owner(self, name: str, wrapped: bool=False) -> Base32Address:
        """
        returns the owner of the name.
        pass wrapped = True to know the owner of the name if the the name is wrapped by a NameWrapper

        Parameters
        ----------
        name : str
            the domain name
        wrapped : bool, optional
            whether further get the name from name wrapper, by default False

        Returns
        -------
        Base32Address
            the owner of the name
        """        
        owner = cast(Base32Address, super().owner(name))
        if not wrapped:
            return owner
        return self._owner_from_name_wrapper(owner, name)
    
    def resolver(self, name: str) -> Optional["ConfluxContract"]:
        return cast("ConfluxContract", super().resolver(name))
    
    def setup_owner(
        self,
        name: str,
        new_owner: Union[Base32Address, str] = cast(Base32Address, default),
        transact: Optional["TxParam"] = None,
        wrapped: bool = False
    ) -> Optional[Base32Address]:
        self._check_unstable_api("setup_owner")
        name = normalize_name(name)

        transact = deepcopy(transact) if transact else {}
        (super_owner, unowned, owned) = self._first_owner(name)
        if new_owner == default:
            new_owner = self._tx_sender(transact)
        elif not new_owner:
            new_owner = Base32Address.zero_address(network_id=self.w3.cfx.chain_id)
        # claim subdomain if needed
        self._claim_ownership(new_owner, unowned, owned, transact=transact, wrapped=wrapped)
        return cast(Base32Address, new_owner)
    
    def setup_address(
        self,
        name: str,
        address: Union[Base32Address, str, None] = cast(Base32Address, default),
        transact: Optional["TxParam"] = None,
        wrapped: bool = False
    ) -> Optional["TransactionHash"]:
        """
        NOTE: This api is not stable, you should set ``w3.cns.allow_unstable_api = True`` to enable this api.
        Set up the name to point to the supplied address.
        Make sure the sender of the transaction has the permission to set the address or the transaction execution will fail.

        Parameters
        ----------
        name : str
            name to setup
        address : Union[Base32Address, str, None], optional
            name will point to this address.
            If ``None``, erase the record. 
            If not specified, name will point to the sender of the transaction
        transact : Optional[TxParam], optional
            Specify the non-default transaction execution information.
            Specifically, ``from`` field to specify the transaction sender.
            Required if ``w3.cfx.default_account`` is not set.
            By default None
        wrapped : bool, optional
            whether the name is wrapped by a name wrapper, by default False

        Returns
        -------
        Optional[TransactionHash]
            The transaction hash object of the transaction to set the address. 
            None if the name was already pointed to the target address

        Raises
        ------
        ResolverNotFound
            the resolver of the address is not found
        """
        self._check_unstable_api("setup_address")
        # simple implementation without subnode setup
        transact = deepcopy(transact) if transact else {}
        name = normalize_name(name)
        # address is not provided, so set "from" as the target address
        # NOTE: difference to web3.py - we do not use owner as address, sender is used as address
        if address == default:
            address = self._tx_sender(transact)
        elif address is None:
            address = Base32Address.zero_address(network_id=self.w3.cfx.chain_id)
        if self.address(name) == address:
            return None
        
        self.setup_owner(name, transact=transact, wrapped=wrapped)

        resolver, current_name = self._get_resolver(name)
        assert resolver is not None
        self._set_resolver(name, resolver.address, transact, wrapped=wrapped)
        
        return resolver.functions.setAddr(normal_name_to_hash(name), address).transact(transact)

    def _get_resolver(self, normal_name: str, fn_name: str = "addr") -> Tuple[Optional["ConfluxContract"], str]:
        return super()._get_resolver(normal_name, fn_name) # type: ignore

    def _set_resolver(self, name: str, resolver_addr: Base32Address, transact: "TxParam", wrapped: bool=False) -> "ConfluxContract":
        # if is_none_or_zero_address(resolver_addr):
        #     resolver_addr = self.address("resolver.eth")
        namehash = raw_name_to_hash(name)
        if self.ens.caller.resolver(namehash) != resolver_addr:
            if wrapped:
                self._name_wrapper_contract(self.owner(name)).functions.setResolver(namehash, resolver_addr).transact(transact).executed()
            else:
                self.ens.functions.setResolver(namehash, resolver_addr).transact(transact).executed()
        return self._resolver_contract(address=resolver_addr)

    def setup_name(self, name: str, address: Optional[Base32Address] = None, transact: Optional["TxParam"] = None) -> HexBytes:
        self._check_unstable_api("setup_name")
        return super().setup_name(name, address, transact) # type: ignore
    
    def set_text(self, name: str, key: str, value: str, transact: Optional["TxParam"] = None) -> HexBytes:
        self._check_unstable_api("set_text")
        return super().set_text(name, key, value, transact) # type: ignore

    def _claim_ownership(
        self,
        owner: "AddressParam",
        unowned: Sequence[str],
        owned: str,
        old_owner: Optional[Base32Address] = None,
        transact: Optional["TxParam"] = None,
        wrapped: bool = False,
    ) -> None:
        if not transact:
            transact = {}
        transact = deepcopy(transact)
        # transact["from"] = old_owner or owner
        if wrapped:
            name_wrapper = self._name_wrapper_contract(
                self.owner(owned)
            )
        for label in reversed(unowned):
            # TODO: manually specify nonce
            if wrapped:
                name_wrapper.functions.setSubnodeOwner( # type: ignore
                    raw_name_to_hash(owned), label, owner, 0, 2**64-1
                ).transact(transact).executed()
            else:
                self.ens.functions.setSubnodeOwner(
                    raw_name_to_hash(owned), label_to_hash(label), owner
                ).transact(transact).executed()
            owned = f"{label}.{owned}"
    
    def _tx_sender(self, transact: "TxParam") -> Base32Address:
        if 'from' in transact:
            return cast(Base32Address, transact['from'])
        elif self.w3.cfx.default_account:
            return self.w3.cfx.default_account
        else:
            raise MissingTransactionSender("Transaction sender is not specified: please set w3.cfx.default_account or transact['from'])")

    def _first_owner(self, name: str) -> Tuple[Optional[Base32Address], Sequence[str], str]:
        return cast(Tuple[Optional[Base32Address], Sequence[str], str], super()._first_owner(name))

    def _owner_from_name_wrapper(self, address: Base32Address, name: str) -> Base32Address:
        name_wrapper = self._name_wrapper_contract(address)
        try:
            return name_wrapper.caller.ownerOf(
                int.from_bytes(raw_name_to_hash(name), "big")
            )
        except:
            # TODO: use supportInterface to judge
            raise InterfaceNotSupported(f"Interface ownerOf is not invoked successfully: please check if {address} is a NameWrapper")

    @classmethod
    def fromWeb3(cls, w3: "Web3", addr: Optional[Base32Address] = None) -> Self:
        return cls.from_web3(w3, addr)

    @classmethod
    def from_web3(cls, w3: "Web3", addr: Optional[Base32Address] = None) -> Self:
        """
        Generate an ENS instance with web3

        :param `web3.Web3` w3: to infer connection information
        :param hex-string addr: the address of the ENS registry on-chain. If not
            provided, defaults to the mainnet ENS registry address.
        """
        provider = w3.manager.provider
        middlewares = w3.middleware_onion.middlewares
        default_account = w3.cfx.default_account
        return cls(cast("BaseProvider", provider), addr=addr, middlewares=middlewares, default_account=default_account)

    def _check_unstable_api(self, api_name):
        if not self.allow_unstable_api:
            raise UnstableAPI(f"API {api_name} is forbidden because it is still unstable. You can enable it by setting w3.cns.allow_unstable_api = True")

    def _assert_control(self, account: Base32Address, name: str, parent_owned: Optional[str] = None) -> None:
        # if is contract, check if it is a name wrapper
        # if account.address_type == 'contract':
        #     try:
        #         # we assume 
        #         account = self._owner_from_name_wrapper(account, name)
        #     except InterfaceNotSupported:
        #         raise UnauthorizedError(
        #             f"in order to modify {name!r}, you must control account"
        #             f" {account!r}, which is a contract"
        #         )
        accounts_in_control: Sequence[Base32Address] = [normalize_to(item, self.w3.cfx.chain_id) for item in self.w3.wallet.accounts]
        try:
            accounts_in_control += list(self.w3.cfx.accounts)
        except ValueError as e:
            if e.args[0]['code'] == 32601 and e.args[0]['message'] == 'the method accounts does not exist/is not available':
                pass
        
        for item in accounts_in_control:
            if account == item:
                return # account
        raise UnauthorizedError(
            f"in order to modify {name!r}, you must control account"
            f" {account!r}, which owns {parent_owned or name!r}"
        )

