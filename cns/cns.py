from audioop import add
from typing import (
    Type,
    Union,
    cast,
    Optional,
    Sequence,
    Tuple,
    TYPE_CHECKING
)
from typing_extensions import (
    Self
)

from web3._utils.empty import (
    Empty,
    empty,
)
from ens import (
    ENS,
    abis,
)
from ens.utils import (
    default,
)
from cns.utils import (
    init_web3
)
from cfx_address import (
    Base32Address,
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
    )

class CNS(ENS):
    w3: "Web3"

    def __init__(
        self,
        provider: "BaseProvider" = cast("BaseProvider", default),
        addr: Optional[Base32Address]=None,
        middlewares: Optional[Sequence[Tuple["Middleware", str]]] = None,
    ) -> None:
        """
        :param provider: a single provider used to connect to Ethereum
        :type provider: instance of `web3.providers.base.BaseProvider`
        :param hex-string addr: the address of the ENS registry on-chain.
            If not provided, ENS.py will default to the mainnet ENS
            registry address.
        """
        self.w3 = init_web3(provider, middlewares)

        # if addr is None, propriate address will be automatically selected
        # see conflux_web3.contract.metadata.DEPLOYMENT_INFO for more infomation
        if addr:
            self.ens = cast("ConfluxContract", self.w3.cfx.contract(addr, name="ENS"))
        else:
            self.ens = cast("ConfluxContract", self.w3.cfx.contract(addr, name="ENS", with_deployment_info=True))
        # TODO: use contract to init
        self._resolver_contract = self.w3.cfx.contract(abi=abis.RESOLVER)
        self._reverse_resolver_contract = self.w3.cfx.contract(
            abi=abis.REVERSE_RESOLVER
        )
    
    def address(self, name: str) -> Optional[Base32Address]:
        address = self._resolve(name, "addr")
        if address is not None:
            # TODO: remove this part if returned contract address is encoded in Base32
            return Base32Address(address, self.w3.cfx.chain_id)
        return address

    @classmethod
    def fromWeb3(cls, w3: "Web3", addr: Optional[Base32Address] = None) -> Self:
        return cls.from_web3(w3, addr)

    @classmethod
    def from_web3(cls, w3: "Web3", addr: Optional[Base32Address] = None) -> Self:
        return cast(Type[Self], super().fromWeb3(w3, addr)) # type: ignore
