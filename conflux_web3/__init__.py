from web3 import Web3 as OriWeb3
from conflux_module import ConfluxClient

from web3.providers.base import (
    BaseProvider,
)

from typing import (
    Any,
    Optional,
    Sequence,
)

class Web3(OriWeb3):
    cfx: ConfluxClient
    
    def __init__(
        self,
        provider: Optional[BaseProvider] = None,
        middlewares: Optional[Sequence[Any]] = []
    ):
        # ConfluxClient as eth provider, default middlewares as [] rather than None
        OriWeb3.__init__(self, provider=provider, middlewares=middlewares, modules={
            "eth": ConfluxClient
        })
        # use __setattr__ to avoid language server type hint
        self.__setattr__("cfx", self.eth)
        
        # provide easy access
        self.account = self.cfx.account
        self.address = self.cfx.address
        
        # TODO: set contract
