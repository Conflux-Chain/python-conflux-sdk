# Note that ERC1319 is not a finalized standard. We only provide VERY BASIC support for it
from typing import (
    TYPE_CHECKING,
)
from cfxpm.contract import ConfluxLinkableContract

from ethpm.package import Package as EthPackage

if TYPE_CHECKING:
    from conflux_web3 import Web3

# used to hook Package
def set_conflux_linkable_contract(self: "Package", *args, **kwargs):
    self.w3.cfx.defaultContractFactory = ConfluxLinkableContract

class Package(EthPackage):
    w3: "Web3"
        
    def get_contract_factory(self, name: str) -> ConfluxLinkableContract:
        return super().get_contract_factory(name) # type: ignore
