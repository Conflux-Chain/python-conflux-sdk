from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    NewType,
    Optional,
    Sequence,
    Type,
    TypeVar,
    TypedDict,
    Union,
    Literal
)
import cfx_account
import cfx_address
# from eth_typing import AnyAddress
from hexbytes import HexBytes

from eth_typing.evm import (
    Address,
    HexAddress,
    ChecksumAddress,
    BlockNumber,
    ChecksumAddress,
    Hash32,
)
from eth_typing.encoding import (
    HexStr,
)

from cfx_address import Address as CfxAddress
from cfx_account import Account as CfxAccount

Drip = NewType("Drip", int)
CFX = NewType("CFX", int)
Base32Address = NewType("Base32Address", str)
AddressParam = Union[Base32Address, CfxAccount, CfxAddress]

BlockParams = Literal["latest_checkpoint", "earliest", "latest_finalized", "latest_confirmed", "latest_state", "latest_mined"]
BlockIdentifier = Union[BlockParams, BlockNumber, Hash32, HexStr, HexBytes, int, None]

EstimateResult = TypedDict(
    "EstimateResult",
    {
        "gasLimit": int,
        "gasUsed": int,
        "storageCollateralized": int,
    }
)

__all__ = (
    "Drip",
    "BlockParams",
    "BlockIdentifier",
    "Base32Address",
    "EstimateResult",
)