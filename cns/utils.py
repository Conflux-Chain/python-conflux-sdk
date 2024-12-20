from typing import (
    TYPE_CHECKING,
    Optional,
    Sequence,
    Tuple,
    cast,
    Collection,
)

from ens.utils import (
    default,
)
from ens.constants import (
    ACCEPTABLE_STALE_HOURS,
)

from web3.exceptions import (
    Web3ValueError,
)
from web3.middleware.stalecheck import StalecheckMiddlewareBuilder
from cfx_address import (
    Base32Address
)

if TYPE_CHECKING:
    from conflux_web3 import Web3 as _Web3  # noqa: F401
    from web3.providers.base import (  # noqa: F401
        # AsyncBaseProvider,
        BaseProvider,
    )
    from conflux_web3.types import (
        Middleware
    )

def init_web3(
    provider: "BaseProvider" = cast("BaseProvider", default),
    middlewares: Optional[Sequence[Tuple["Middleware", str]]] = None,
    default_account: Optional[Base32Address] = None
) -> "_Web3":
    from conflux_web3 import Web3 as Web3Main
    from conflux_web3.client import ConfluxClient as CfxMain

    if provider is default:
        w3 = Web3Main(ens=None, modules={"cfx": (CfxMain)})   # type: ignore
    else:
        w3 = Web3Main(provider, middlewares, ens=None, modules={"cfx": (CfxMain)})  # type: ignore
    if default_account:
        w3.cfx._default_account = default_account
    return customize_web3(w3)

def build_stalecheck_middleware(allowable_delay: int, skip_stalecheck_for_methods: Collection[str]):
    def inner(w3):
        if allowable_delay <= 0:
            raise Web3ValueError(
                "You must set a positive allowable_delay in seconds for this middleware"
            )
        middleware = StalecheckMiddlewareBuilder(w3)
        middleware.allowable_delay = allowable_delay
        middleware.skip_stalecheck_for_methods = skip_stalecheck_for_methods
        middleware.cache = {"latest": None}
        return middleware
    return inner
    

def customize_web3(w3: "_Web3") -> "_Web3":
    if w3.middleware_onion.get("name_to_address"):
        w3.middleware_onion.remove("name_to_address")

    if not w3.middleware_onion.get("stalecheck"):
        w3.middleware_onion.add(
            build_stalecheck_middleware(ACCEPTABLE_STALE_HOURS * 3600, ["cfx_getBlockByEpochNumber", "cfx_getStatus"]), name="stalecheck"
        )
    return w3

# is_none_or_base_32_zero_address is implemented in _web3_hook
# def is_none_or_base_32_zero_address(addr) -> bool:
#     ...