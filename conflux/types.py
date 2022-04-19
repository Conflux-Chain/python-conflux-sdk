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
    Union,
)
from eth_typing import (
    BlockNumber,
    Hash32,
    HexStr,
)
from hexbytes import (
    HexBytes,
)
from web3._utils.compat import (
    Literal,
    TypedDict,
)
from web3.types import (
    Nonce,
    Timestamp,
    _Hash32,
)

# if TYPE_CHECKING:
#     from web3 import Web3  # noqa: F401

EpochTags = Literal["earliest", "latest_checkpoint", "latest_confirmed", "latest_state", "latest_mined"]
EpochIdentifier = Union[EpochTags, int, HexStr]
BlockIdentifier = Union[EpochIdentifier, Hash32, HexStr, HexBytes]
LatestEpochParam = Literal["latest_state"]

Drip = NewType('Drip', int)
EpochNumber = NewType("EpochNumber", int)


class FilterParams(TypedDict, total=False):
    address: Union[str, List[str]]
    blockHashes: List[HexBytes]
    fromEpoch: EpochIdentifier
    toEpoch: EpochIdentifier
    topics: Sequence[Optional[Union[_Hash32, Sequence[_Hash32]]]]
    limit: int


class LogReceipt(TypedDict):
    address: str
    data: HexStr
    topics: Sequence[HexBytes]


class ChainStatus:
    bestHash: str
    blockNumber: int
    chainId: int
    networkId: int
    epochNumber: int
    pendingTxNumber: int
    latestCheckpoint: int
    latestConfirmed: int
    latestState: int


class Account:
    balance: int
    nonce: int
    codeHash: str
    admin: str
    stakingBalance: int
    collateralForStorage: int
    accumulatedInterestReturn: int


class Log(TypedDict):
    address: str
    topics: Sequence[HexBytes]
    data: HexStr
    blockHash: HexBytes
    epochNumber: BlockNumber
    transactionHash: HexBytes
    transactionIndex: int
    logIndex: int
    transactionLogIndex: int


TxData = TypedDict("TxData", {
    "blockHash": HexBytes,
    "contractCreated": str,
    "epochHeight": BlockNumber,
    "chainId": int,
    "data": Union[bytes, HexStr],
    "from": str,
    "gas": Drip,
    "gasPrice": Drip,
    "hash": HexBytes,
    "nonce": Nonce,
    "r": HexBytes,
    "s": HexBytes,
    "status": int,
    "storageLimit": int,
    "to": str,
    "transactionIndex": int,
    "v": int,
    "value": Drip,
}, total=False)

TxParams = TypedDict("TxParams", {
    "chainId": int,
    "data": Union[bytes, HexStr],
    "from": str,
    "gas": Drip,
    "gasPrice": Drip,
    "nonce": Nonce,
    "to": str,
    "value": Drip,
    "epochHeight": int,
    "storageLimit": int,
}, total=False)


class StorageRelease:
    address: str
    collaterals: int


TxReceipt = TypedDict("TxReceipt", {
    "blockHash": HexBytes,
    "epochNumber": BlockNumber,
    "gasUsed": Drip,
    "gasFee": Drip,
    "gasCoveredBySponsor": bool,
    "storageCoveredBySponsor": bool,
    "storageCollateralized": int,
    "storageReleased": List[StorageRelease],
    "contractCreated": str,
    "stateRoot": HexBytes,
    "from": str,
    "logs": List[LogReceipt],
    "logsBloom": HexBytes,
    "outcomeStatus": int,
    "to": str,
    "transactionHash": HexBytes,
    "index": int,
})


class BlockData(TypedDict, total=False):
    adaptive: bool
    blame: int
    deferredLogsBloomHash: HexBytes
    deferredReceiptsRoot: HexBytes
    deferredStateRoot: HexBytes
    difficulty: int
    gasLimit: Drip
    powQuality: HexBytes
    refereeHashes: List[HexBytes]
    gasUsed: Drip
    hash: HexBytes
    miner: str
    nonce: HexBytes
    epochNumber: BlockNumber
    height: BlockNumber
    parentHash: HexBytes
    size: int
    timestamp: Timestamp
    transactions: Union[Sequence[HexBytes], Sequence[TxData]]
    transactionsRoot: HexBytes


class EstimateResult(TypedDict):
    gasUsed: int
    storageCollateralized: int


class SponsorInfo(TypedDict):
    sponsorBalanceForCollateral: int
    sponsorBalanceForGas: int
    sponsorGasBound: int
    sponsorForCollateral: str
    sponsorForGas: str


class RewardInfo:
    author: str
    baseReward: int
    blockHash: str
    totalReward: int
    txFee: int
