from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
    Sequence,
    Type,
    Union,
    cast,
)

from eth_abi.codec import (
    ABICodec
)
from web3 import (
    Web3 as OriWeb3
)
from web3.providers.base import (
    BaseProvider,
)
from web3.types import (
    RPCEndpoint
)
from web3._utils.empty import (
    empty,
    Empty,
)
from web3.module import (
    Module,
)

from cfx_address import (
    Base32Address
)
from cfx_account import (
    Account
)
from conflux_web3.types import (
    MiddlewareOnion
)
from conflux_web3.middleware import (
    conflux_default_middlewares
)

from conflux_web3.client import (
    ConfluxClient
)
from conflux_web3.txpool import (
    Txpool
)
from conflux_web3.exceptions import (
    DeploymentInfoNotFound
)
from conflux_web3._utils.abi import (
    build_cfx_default_registry
)
from cns import (
    CNS
)
if TYPE_CHECKING:
    from conflux_web3.middleware.wallet import Wallet

# The module name __name__ should be Web3 
class Web3(OriWeb3):
    cfx: ConfluxClient
    txpool: Txpool
    
    def __init__(
        self,
        provider: BaseProvider,
        middlewares: Optional[Sequence[Any]] = None,
        modules: Optional[Dict[str, Union[Type[Module], Sequence[Any]]]] = None,
        # external_modules: Optional[Dict[str, Union[Type[Module], Sequence[Any]]]] = None,
        cns: CNS = cast(CNS, empty),
        **kwargs,
    ):
        """
        initialize a ``Web3`` instance to interact with the blockchain
        
        >>> w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:12537"))
        >>> w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
        >>> w3 = Web3(Web3.HTTPProvider("https://main.confluxrpc.com"))

        Parameters
        ----------
        provider : BaseProvider
            ``provider`` decides on how to connect to the blockchain, 
        middlewares : Optional[Sequence[Any]], optional
            middlewares to use, recommended not to specify
        modules : Optional[Dict[str, Union[Type[Module], Sequence[Any]]]], optional
            modules to use, recommended not to specify
        cns : CNS, optional
            a cns object. If cns is not specified, w3.cns will be inited with default setting
        """        
        # ConfluxClient as eth provider, default middlewares as [] rather than None
        # OriWeb3.__init__(self, provider=provider, middlewares=middlewares, modules={
        #     "eth": ConfluxClient
        # })
        if middlewares is None:
            middlewares = conflux_default_middlewares(self)
        # TODO: finish provider default value logic
        self.manager = self.RequestManager(self, provider, middlewares)
        # this codec gets used in the module initialization,
        # so it needs to come before attach_modules
        self.codec = ABICodec(build_cfx_default_registry())

        if modules is None:
            # modules = get_default_modules()
            modules = {
                "cfx": ConfluxClient,
                "txpool": Txpool,
            }
        
        if "cfx" not in modules:
            raise ValueError("cfx module is missing in modules: cfx module is required to initialze a web3 instance")

        self.attach_modules(modules)  # type: ignore

        # if external_modules is not None:
        #     self.attach_modules(external_modules)

        
        # use __setattr__ to avoid language server type hint
        self.__setattr__("eth", self.cfx)
        
        # provide easy access
        # self.account = self.cfx.account
        # self.address = self.cfx.address
        
        # ens argument is remained for compatibility
        # but it is not allowed to specify ens AND cns at the same time

        # kwargs["ens"] might be None, we assume a developer will not deliberately pass empty
        if kwargs.get("ens", empty) is not empty:
            ens = kwargs["ens"]
            if cns is empty:
                cns = ens
            else:
                raise ValueError("Redundant arguments: ens and cns argument are both specified. Only ens argument OR cns argument is allowed")
        
        if cns == empty and self.is_connected():
            try:
                cns = CNS.from_web3(self)
            except DeploymentInfoNotFound:
                pass

        self.cns = cns
        
        # TODO: set contract
        
    @property
    def account(self) -> Account:
        return self.cfx.account
        
    @property
    def address(self) -> Type[Base32Address]:
        return self.cfx.address

    @property
    def api(self) -> str:
        from conflux_web3 import __version__
        return __version__

    @property
    def ens(self) -> CNS:
        return self.cns
    
    @property
    def cns(self) -> CNS:
        return self._ens # type: ignore
    
    @cns.setter
    def cns(self, new_cns: CNS) -> None:
        # TODO: check middlewares, modules and default account if cns is inited in this way
        self._ens = new_cns
        
    @ens.setter
    def ens(self, new_cns: CNS) -> None:
        self.cns = new_cns

    @property
    def middleware_onion(self) -> MiddlewareOnion:
        return cast(MiddlewareOnion, self.manager.middleware_onion)
    
    @property
    def clientVersion(self) -> str:
        return self.client_version
    
    @property
    def client_version(self) -> str:
        return self.cfx.client_version
    
    @property
    def wallet(self) -> "Wallet":
        return self.middleware_onion.get("wallet", None) # type: ignore
    
    def is_connected(self) -> bool:
        try:
            response = self.provider.make_request(RPCEndpoint("cfx_clientVersion"), [])
        except OSError:
            return False

        assert response["jsonrpc"] == "2.0" # type: ignore
        assert "error" not in response # type: ignore

        return True
