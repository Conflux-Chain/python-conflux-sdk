from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    NewType,
    Optional,
    Sequence,
    TypedDict,
    Union,
)
from hexbytes import HexBytes

from web3.types import (
    RPCEndpoint,
    RPCResponse,
)
from web3.datastructures import (
    NamedElementOnion,
)

from cfx_address import Base32Address
from cfx_utils.types import (
    TxDict,
    TxParam,
    HexAddress,
    _Hash32,
    Nonce,
    Drip,
    CFX,
    AddressParam,
    Storage,
    EpochNumberParam,
    EpochLiteral,
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

class NodeStatus(TypedDict):
    bestHash: _Hash32
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


class FilterParams(TypedDict, total=False):
    fromEpoch: EpochNumberParam
    toEpoch: EpochNumberParam
    blockHashes: Sequence[_Hash32]
    address: Union[Base32Address, List[Base32Address]]
    topics: Sequence[Optional[Union[_Hash32, Sequence[_Hash32]]]]


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
        "logs": List[LogReceipt],
        "txExecErrorMsg": Union[str, None]
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

class EventData(TypedDict, total=False):
    address: Base32Address
    args: Dict[str, Any]
    blockHash: HexBytes
    epochNumber: int
    event: str
    logIndex: int
    transactionHash: HexBytes
    transactionIndex: int

class BlockData(TypedDict):
    hash: _Hash32
    parentHash: _Hash32
    height: int
    miner: Base32Address
    deferredStateRoot: _Hash32
    deferredReceiptsRoot: _Hash32
    deferredLogsBloomHash: _Hash32
    blame: int
    transactionsRoot: _Hash32
    epochNumber: Union[int, None]
    blockNumber: Union[int, None]
    gasLimit: int
    gasUsed: Union[int, None]
    timestamp: int
    difficulty: int
    powQuality: Union[HexBytes, None]
    refereeHashes: Sequence[_Hash32]
    adaptive: bool
    nonce: HexBytes
    size: int
    custom: Sequence[HexBytes]
    posReference: _Hash32
    transactions: Sequence[Union[_Hash32, TxData]]
    

Middleware = Callable[[Callable[[RPCEndpoint, Any], RPCResponse], "Web3"], Any]
MiddlewareOnion = NamedElementOnion[str, Middleware]
