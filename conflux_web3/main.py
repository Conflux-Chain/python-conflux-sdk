from typing import (
    Any,
    Optional,
    Sequence,
    cast,
)

from eth_abi.codec import ABICodec
from web3 import Web3 as OriWeb3
from web3 import HTTPProvider
from web3.providers.base import (
    BaseProvider,
)
from web3 import (
    HTTPProvider,
)
from web3.types import (
    RPCEndpoint
)
from web3._utils.empty import (
    empty,
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
from conflux_web3._utils.abi import (
    build_cfx_default_registry
)

# The module name __name__ should be Web3 
class Web3(OriWeb3):
    cfx: ConfluxClient
    txpool: Txpool
    
    def __init__(
        self,
        provider: Optional[BaseProvider] = None,
        middlewares: Optional[Sequence[Any]] = None,
        # modules: Optional[Dict[str, Union[Type[Module], Sequence[Any]]]] = None,
        # external_modules: Optional[Dict[str, Union[Type[Module], Sequence[Any]]]] = None,
        # ens: ENS = cast(ENS, empty)
    ):
        # ConfluxClient as eth provider, default middlewares as [] rather than None
        # OriWeb3.__init__(self, provider=provider, middlewares=middlewares, modules={
        #     "eth": ConfluxClient
        # })
        if middlewares is None:
            middlewares = conflux_default_middlewares
        self.manager = self.RequestManager(self, provider, middlewares)
        # this codec gets used in the module initialization,
        # so it needs to come before attach_modules
        self.codec = ABICodec(build_cfx_default_registry())

        # if modules is None:
        #     modules = get_default_modules()
        modules = {
            "eth": ConfluxClient,
            "txpool": Txpool,
        }

        self.attach_modules(modules)  # type: ignore

        # if external_modules is not None:
        #     self.attach_modules(external_modules)

        self.ens = empty  # type: ignore
        
        # use __setattr__ to avoid language server type hint
        self.__setattr__("cfx", self.eth)
        
        # provide easy access
        Web3.account = self.cfx.account
        Web3.account.set_w3(self)
        Web3.address = self.cfx.address
        
        # TODO: set contract

    @property
    def middleware_onion(self) -> MiddlewareOnion:
        return cast(MiddlewareOnion, self.manager.middleware_onion)
    
    @property
    def clientVersion(self) -> str:
        return self.client_version
    
    @property
    def client_version(self) -> str:
        return self.cfx.client_version
    
    def isConnected(self) -> bool:
        return self.is_connected()
    
    def is_connected(self) -> bool:
        try:
            response = self.provider.make_request(RPCEndpoint("cfx_clientVersion"), [])
        except OSError:
            return False

        assert response["jsonrpc"] == "2.0" # type: ignore
        assert "error" not in response # type: ignore

        return True
