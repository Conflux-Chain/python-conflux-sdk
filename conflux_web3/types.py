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
)
from eth_typing.encoding import (
    HexStr,
)

from web3.types import (
    Nonce,
    RPCEndpoint,
    RPCResponse,
    _Hash32,
)
from web3.datastructures import (
    NamedElementOnion,
)

from cfx_address import Address as CfxAddress
from cfx_account import Account as CfxAccount

if TYPE_CHECKING:
    from conflux_web3 import Web3

Drip = NewType("Drip", int)
CFX = NewType("CFX", int)
Base32Address = NewType("Base32Address", str)
AddressParam = Union[Base32Address, str]

EpochLiteral = Literal["latest_checkpoint", "earliest", "latest_finalized", "latest_confirmed", "latest_state", "latest_mined"]
EpochNumberParam = Union[EpochLiteral, _Hash32, int]
ChainId = Union[int, HexStr]
Storage = NewType("Storage", int)

class NodeStatus(TypedDict):
    bestHash: HexBytes
    chainId: int
    networkId: int
    blockNumber: int
    epochNumber: int
    latestCheckpoint: int
    latestConfirmed: int
    latestState: int
    latestFinalized: int
    ethereumSpaceChainId: int
    pendingTxNumber: int

class EstimateResult(TypedDict):    
    gasLimit: int
    gasUsed: int
    storageCollateralized: Storage


# syntax b/c "from" keyword not allowed w/ class construction
TxDict = TypedDict(
    "TxDict",
    {
        "chainId": int,
        "data": Union[bytes, HexStr],
        # addr or ens
        "from": AddressParam,
        "gas": int,
        "gasPrice": Drip,
        "nonce": Nonce,
        "to": AddressParam,
        "value": Drip,
        "epochHeight": int,
        "storageLimit": Storage
    },
    total=False,
)

class FilterParams(TypedDict, total=False):
    fromEpoch: EpochNumberParam
    toEpoch: EpochNumberParam
    blockHashes: Sequence[_Hash32]
    address: Union[Base32Address, List[Base32Address]]
    topics: Sequence[Optional[Union[_Hash32, Sequence[_Hash32]]]]
    limit: int
    offset: int


class LogReceipt(TypedDict):
    address: Base32Address
    topics: Sequence[HexBytes]
    data: HexBytes
    blockHash: HexBytes
    epochNumber: int
    transactionHash: HexBytes
    transactionIndex: int
    logIndex: int
    transactionLogIndex: int

# syntax b/c "from" keyword not allowed w/ class construction
TxReceipt = TypedDict(
    "TxReceipt",
    {
        "transactionHash": _Hash32,
        "index": int,
        "blockHash": _Hash32,
        "epochNumber": int,
        "from": AddressParam,
        "to": AddressParam,
        "gasUsed": Drip,
        "gasFee": Drip,
        "gasCoveredBySponsor": bool,
        "storageCollateralized": Storage,
        "storageCoveredBySponsor": bool,
        "storageReleased": List[Storage],
        "contractCreated": Union[AddressParam, None],
        
        "stateRoot": _Hash32,
        "outcomeStatus": int,
        "logsBloom": HexBytes,
        
        "logs": List[LogReceipt]
    },
)

# syntax b/c "from" keyword not allowed w/ class construction
TxData = TypedDict(
    "TxData",
    {
        "blockHash": Union[None, HexBytes],
        "chainId": int,
        "contractCreated": Union[None, AddressParam],
        "data": HexBytes,
        "epochHeight": int,
        "from": AddressParam,
        "gas": int,
        "gasPrice": Drip,
        "hash": _Hash32,
        "nonce": Nonce,
        "r": HexBytes,
        "s": HexBytes,
        "status": Union[None, int],
        "storageLimit": Storage,
        "to": Union[None, AddressParam],
        "transactionIndex": Union[None, int],
        "v": int,
        "value": Drip,
    },
    total=False,
)

TxParam = Union[TxDict, dict[str, Any]]

Middleware = Callable[[Callable[[RPCEndpoint, Any], RPCResponse], "Web3"], Any]
MiddlewareOnion = NamedElementOnion[str, Middleware]
