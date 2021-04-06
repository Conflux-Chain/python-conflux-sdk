from conflux._utils.rpc_abi import (
    RPC,
)
from web3.manager import (
    RequestManager as DefaultRequestManager,
)
from web3.providers import (
    BaseProvider,
)
from web3.providers.ipc import (
    IPCProvider,
)
from web3.providers.rpc import (
    HTTPProvider,
)
from web3.providers.websocket import (
    WebsocketProvider,
)
from typing import (
    Any,
    cast,
    Dict,
    List,
    Optional,
    Sequence,
    TYPE_CHECKING
)
from web3._utils.module import (
    attach_modules,
)
from eth_abi.codec import (
    ABICodec,
)
from web3._utils.abi import (
    build_default_registry,
    build_strict_registry,
    map_abi_data,
)
from conflux.cfx import Cfx
from eth_utils import (
    to_wei,
    from_wei,
)

def get_default_modules() -> Dict[str, Sequence[Any]]:
    return {
        "cfx": (Cfx,),
    }

class Conflux:
    # Providers
    HTTPProvider = HTTPProvider
    IPCProvider = IPCProvider
    WebsocketProvider = WebsocketProvider

    # Managers
    RequestManager = DefaultRequestManager

    # Currency Utility
    toDrip = staticmethod(to_wei)
    fromDrip = staticmethod(from_wei)

    cfx: Cfx

    def __init__(
        self,
        provider: Optional[BaseProvider] = None,
        middlewares: Optional[Sequence[Any]] = None,
        modules: Optional[Dict[str, Sequence[Any]]] = None,
    ) -> None:
        self.manager = self.RequestManager(self, provider, middlewares)

        self.codec = ABICodec(build_default_registry())

        if modules is None:
            modules = get_default_modules()

        attach_modules(self, modules)

    @property
    def clientVersion(self) -> str:
        return self.manager.request_blocking(RPC.cfx_clientVersion, [])
