from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Literal,
    NewType,
    Optional,
    Sequence,
    TypedDict,
    Union,
    Dict
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
    Hash32, # Hash32 as specific output data type
    _Hash32, # _Hash32 as robust input data type
    Nonce,
    Drip,
    CFX,
    AddressParam,
    Storage,
    EpochNumberParam,
    EpochLiteral,
    EpochNumber
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

class NodeStatus(TypedDict):
    bestHash: Hash32
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
        "transactionHash": Hash32,
        "index": int,
        "blockHash": Hash32,
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
        "stateRoot": Hash32,
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
        "hash": Hash32,
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


class RequiredEventData(TypedDict):
    address: Base32Address
    args: Dict[str, Any]
    event: str

class EventData(RequiredEventData, total=False):
    blockHash: HexBytes
    epochNumber: int
    logIndex: int
    transactionHash: HexBytes
    transactionIndex: int


class BlockData(TypedDict):
    hash: Hash32
    parentHash: Hash32
    height: int
    miner: Base32Address
    deferredStateRoot: Hash32
    deferredReceiptsRoot: Hash32
    deferredLogsBloomHash: Hash32
    blame: int
    transactionsRoot: Hash32
    epochNumber: Union[int, None]
    blockNumber: Union[int, None]
    gasLimit: int
    gasUsed: Union[int, None]
    timestamp: int
    difficulty: int
    powQuality: Union[HexBytes, None]
    refereeHashes: Sequence[Hash32]
    adaptive: bool
    nonce: HexBytes # block nonce put by miner rather than the nonce in the transaction
    size: int
    custom: Sequence[HexBytes]
    posReference: Hash32
    transactions: Sequence[Union[Hash32, TxData]]
    

Middleware = Callable[[Callable[[RPCEndpoint, Any], RPCResponse], "Web3"], Any]
MiddlewareOnion = NamedElementOnion[str, Middleware]

class StorageRoot(TypedDict):
    delta: Union[Hash32, Literal["TOMBSTONE", None]]
    intermediate: Union[Hash32, Literal["TOMBSTONE", None]]
    snapshot: Union[Hash32, Literal["TOMBSTONE", None]]

class SponsorInfo(TypedDict):
    sponsorBalanceForCollateral: Drip
    sponsorBalanceForGas: Drip
    sponsorForCollateral: Base32Address
    sponsorForGas: Base32Address
    sponsorGasBound: Drip
    
class AccountInfo(TypedDict):
    address: Base32Address
    balance: Drip
    nonce: Nonce
    codeHash: Hash32
    stakingBalance: Drip
    collateralForStorage: Storage
    accumulatedInterestReturn: Drip
    admin: Base32Address
    
class DepositInfo(TypedDict):
    accumulatedInterestRate: Drip
    amount: Drip
    depositTime: int # assumed blockNumber
    
class VoteInfo(TypedDict):
    amount: Drip
    unlockBlockNumber: int

class BlockRewardInfo(TypedDict):
    blockHash: Hash32
    author: Base32Address
    totalReward: Drip
    baseReward: Drip
    txFee: Drip

PoSBlockNumber = NewType("PoSBlockNumber", int)
PoSEpochNumber = NewType("PoSEpochNumber", int)

class PoSEconomicsInfo(TypedDict):
    distributablePosInterest: Drip
    lastDistributeBlock: PoSBlockNumber
    totalPosStakingTokens: Drip
    
class PoSAccountRewardsInfo(TypedDict):
    posAddress: Base32Address
    powAddress: Base32Address
    reward: Drip

class PoSEpochRewardInfo(TypedDict):
    accountRewards: Sequence[PoSAccountRewardsInfo]
    powEpochHash: Hash32

class DAOVoteInfo(TypedDict):
    powBaseReward: Drip
    interestRate: int

class SupplyInfo(TypedDict):
    totalIssued: Drip
    totalCollateral: Drip
    totalStaking: Drip
    totalCirculating: Drip
    totalEspaceTokens: Drip

class PendingInfo(TypedDict):
    localNonce: Nonce
    pendingNonce: Nonce
    pendingCount: int
    nextPendingTx: Hash32

class PendingTransactionStatus(TypedDict):
    pending: Literal["futureNonce", "notEnoughCash", "ready"]

class PendingTransactionsInfo(TypedDict):
    firstTxStatus: PendingTransactionStatus
    pendingCount: int
    pendingTransactions: Sequence[TxData]

class TransactionPaymentInfo(TypedDict):
    isBalanceEnough: bool
    willPayCollateral: bool
    willPayTxFee: bool
