from typing import (  # noqa: F401
    TYPE_CHECKING,
    Any,
    Optional,
)
from eth_utils.toolz import (
    assoc, # type: ignore
)
from eth_utils import (
    to_bytes, # type: ignore
)
from ethpm.contract import (
    LinkableContract
)
from ethpm.exceptions import (
    BytecodeLinkingError,
)
from ethpm.contract import (
    is_prelinked_bytecode,
    
)
from conflux_web3.contract import (
    ConfluxContract,
    ConfluxContractConstructor,
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

# totally borrows the implementation of LinkableContract except for base class
# used to hack ethpm Package
# hack activated in conflux_web3._hook

# the implementation below does not work because super() won't work
# ConfluxLinkableContract = type(
#     'LinkableContract', (ConfluxContract, ), dict(LinkableContract.__dict__)
# )
class ConfluxLinkableContract(LinkableContract, ConfluxContract):
    def __init__(self, address: bytes, **kwargs: Any) -> None:
        if self.needs_bytecode_linking:
            raise BytecodeLinkingError(
                "Contract cannot be instantiated until its bytecode is linked."
            )

        # type ignored to allow for undefined **kwargs on `Contract` base class __init__
        super().__init__(address=address, **kwargs)  # type: ignore

    @classmethod
    def factory(cls, w3: "Web3", class_name: Optional[str] = None, **kwargs: Any) -> ConfluxContract:
        dep_link_refs = kwargs.get("unlinked_references")
        bytecode = kwargs.get("bytecode")
        needs_bytecode_linking = False
        if dep_link_refs and bytecode:
            if not is_prelinked_bytecode(to_bytes(hexstr=bytecode), dep_link_refs):
                needs_bytecode_linking = True
        kwargs = assoc(kwargs, "needs_bytecode_linking", needs_bytecode_linking)
        return super().factory(w3, class_name, **kwargs) # type: ignore

    @classmethod
    def constructor(cls, *args: Any, **kwargs: Any) -> ConfluxContractConstructor:
        if cls.needs_bytecode_linking:
            raise BytecodeLinkingError(
                "Contract cannot be deployed until its bytecode is linked."
            )
        return super().constructor(*args, **kwargs) # type: ignore
