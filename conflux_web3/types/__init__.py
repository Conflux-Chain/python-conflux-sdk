from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    NewType,
    Optional,
    Sequence,
    Union,
    Dict
)
from typing_extensions import (
    Literal,
    TypedDict,
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
    GDrip,
    AddressParam,
    Storage,
    EpochNumberParam,
    EpochLiteral,
    EpochNumber
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

class NodeStatus(TypedDict):
    """
    Node status as dict

    Dict keys and corresponding value type
    ----------
    bestHash: bytes
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
    """    
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
    """
    Estimation result of a transaction as dict

    Parameters
    ----------
    gasLimit: int
    gasUsed: int
    storageCollateralized: Storage
    """       
    gasLimit: int
    gasUsed: int
    storageCollateralized: Storage


class FilterParams(TypedDict, total=False):
    """
    Parameter dict to filter logs, more information at https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc/#cfx_getlogs

    Key and type of corresponding value
    ----------
    fromEpoch: EpochNumberParam, optional
    toEpoch: EpochNumberParam, optional
    blockHashes: Sequence[_Hash32], optional
    address: Union[Base32Address, List[Base32Address]], optional
    topics: Sequence[Optional[Union[_Hash32, Sequence[_Hash32]]]], optional
    """
    fromEpoch: EpochNumberParam
    toEpoch: EpochNumberParam
    blockHashes: Sequence[_Hash32]
    address: Union[Base32Address, List[Base32Address]]
    topics: Sequence[Optional[Union[_Hash32, Sequence[_Hash32]]]]


class TransactionLogReceipt(TypedDict):
    """
    Log receipt in transaction receipt

    Key and type of corresponding value
    ----------
    address: Base32Address
    topics: Sequence[HexBytes]
    data: HexBytes
    """
    address: Base32Address
    topics: Sequence[HexBytes]
    data: HexBytes


class LogReceipt(TypedDict):
    """
    Full log receipt

    Key and type of corresponding value
    ----------
    address: Base32Address
    topics: Sequence[HexBytes]
    data: HexBytes
    blockHash: Hash32
    epochNumber: int
    transactionHash: Hash32
    transactionIndex: int
    logIndex: int
    transactionLogIndex: int
    """
    address: Base32Address
    topics: Sequence[HexBytes]
    data: HexBytes
    blockHash: Hash32
    epochNumber: int
    transactionHash: Hash32
    transactionIndex: int
    logIndex: int
    transactionLogIndex: int

class TransactionEventData(TypedDict):
    """
    Transaction event data as a dict

    Key and type of corresponding value
    ----------
    address: Base32Address
    args: Dict[str, Any]
    event: str
    blockHash: Hash32
    epochNumber: int
    transactionHash: Hash32
    transactionIndex: int
    transactionLogIndex: int
    """
    address: Base32Address
    args: Dict[str, Any]
    event: str
    blockHash: Hash32
    epochNumber: int
    transactionHash: Hash32
    transactionIndex: int
    transactionLogIndex: int

class EventData(TransactionEventData, total=False):
    """
    Transaction event data

    Key and type of corresponding value
    ----------
    address: Base32Address
    args: Dict[str, Any]
    event: str
    blockHash: Hash32
    epochNumber: int
    transactionHash: Hash32
    transactionIndex: int
    transactionLogIndex: int
    logIndex: int, Optional
    """
    logIndex: int


# syntax b/c "from" keyword not allowed w/ class construction
TxReceipt = TypedDict(
    "TxReceipt",
    {
        "transactionHash": Hash32,
        "index": int,
        "blockHash": Hash32,
        "epochNumber": int,
        "from": Base32Address,
        "to": Base32Address,
        "gasUsed": int,
        "gasFee": Drip,
        "gasCoveredBySponsor": bool,
        "storageCollateralized": Storage,
        "storageCoveredBySponsor": bool,
        "storageReleased": List[Storage],
        "contractCreated": Union[Base32Address, None],
        "stateRoot": Hash32,
        "outcomeStatus": int,
        "logsBloom": HexBytes,
        "logs": List[TransactionLogReceipt],
        "txExecErrorMsg": Union[str, None]
    },
)
"""
Transaction receipt as a dict

Key and type of corresponding value
----------
"transactionHash": Hash32,
"index": int,
"blockHash": Hash32,
"epochNumber": int,
"from": Base32Address,
"to": Base32Address,
"gasUsed": int,
"gasFee": Drip,
"gasCoveredBySponsor": bool,
"storageCollateralized": Storage,
"storageCoveredBySponsor": bool,
"storageReleased": List[Storage],
"contractCreated": Union[Base32Address, None],
"stateRoot": Hash32,
"outcomeStatus": int,
"logsBloom": HexBytes,
"logs": List[TransactionLogReceipt],
"txExecErrorMsg": Union[str, None]
"""


# syntax b/c "from" keyword not allowed w/ class construction
TxData = TypedDict(
    "TxData",
    {
        "blockHash": Union[None, Hash32],
        "chainId": int,
        "contractCreated": Union[None, Base32Address],
        "data": HexBytes,
        "epochHeight": int,
        "from": Base32Address,
        "gas": int,
        "gasPrice": Drip,
        "hash": Hash32,
        "nonce": Nonce,
        "r": HexBytes,
        "s": HexBytes,
        "status": Union[None, int],
        "storageLimit": Storage,
        "to": Union[None, Base32Address],
        "transactionIndex": Union[None, int],
        "v": int,
        "value": Drip,
    },
    total=False,
)
"""
Transaction data as a dict

Key and type of corresponding value
----------
"blockHash": Union[None, Hash32],
"chainId": int,
"contractCreated": Union[None, Base32Address],
"data": HexBytes,
"epochHeight": int,
"from": Base32Address,
"gas": int,
"gasPrice": Drip,
"hash": Hash32,
"nonce": Nonce,
"r": HexBytes,
"s": HexBytes,
"status": Union[None, int],
"storageLimit": Storage,
"to": Union[None, Base32Address],
"transactionIndex": Union[None, int],
"v": int,
"value": Drip,
"""

class BlockData(TypedDict):
    """
    Block data as a dict

    Key and type of corresponding value
    ----------
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
    nonce: HexBytes
    size: int
    custom: Sequence[HexBytes]
    posReference: Hash32
    transactions: Sequence[Union[Hash32, TxData]]
    """
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
    """

    Key and type of corresponding value
    ----------
    delta: Union[Hash32, Literal["TOMBSTONE", None]]
    intermediate: Union[Hash32, Literal["TOMBSTONE", None]]
    snapshot: Union[Hash32, Literal["TOMBSTONE", None]]
    """
    delta: Union[Hash32, Literal["TOMBSTONE", None]]
    intermediate: Union[Hash32, Literal["TOMBSTONE", None]]
    snapshot: Union[Hash32, Literal["TOMBSTONE", None]]

class SponsorInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    sponsorBalanceForCollateral: Drip
    sponsorBalanceForGas: Drip
    sponsorForCollateral: Base32Address
    sponsorForGas: Base32Address
    sponsorGasBound: Drip
    """
    sponsorBalanceForCollateral: Drip
    sponsorBalanceForGas: Drip
    sponsorForCollateral: Base32Address
    sponsorForGas: Base32Address
    sponsorGasBound: Drip
    
class AccountInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    address: Base32Address
    balance: Drip
    nonce: Nonce
    codeHash: Hash32
    stakingBalance: Drip
    collateralForStorage: Storage
    accumulatedInterestReturn: Drip
    admin: Base32Address
    """
    address: Base32Address
    balance: Drip
    nonce: Nonce
    codeHash: Hash32
    stakingBalance: Drip
    collateralForStorage: Storage
    accumulatedInterestReturn: Drip
    admin: Base32Address
    
class DepositInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    accumulatedInterestRate: int
    amount: Drip
    depositTime: int
    """
    accumulatedInterestRate: int
    amount: Drip
    depositTime: int # assumed blockNumber
    
class VoteInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    amount: Drip
    unlockBlockNumber: int
    """
    amount: Drip
    unlockBlockNumber: int

class BlockRewardInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    blockHash: Hash32
    author: Base32Address
    totalReward: Drip
    baseReward: Drip
    txFee: Drip
    """
    blockHash: Hash32
    author: Base32Address
    totalReward: Drip
    baseReward: Drip
    txFee: Drip

PoSBlockNumber = NewType("PoSBlockNumber", int)
PoSEpochNumber = NewType("PoSEpochNumber", int)

class PoSEconomicsInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    distributablePosInterest: Drip
    lastDistributeBlock: PoSBlockNumber
    totalPosStakingTokens: Drip
    """
    distributablePosInterest: Drip
    lastDistributeBlock: PoSBlockNumber
    totalPosStakingTokens: Drip
    
class PoSAccountRewardsInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    posAddress: Base32Address
    powAddress: Base32Address
    reward: Drip
    """
    posAddress: Base32Address
    powAddress: Base32Address
    reward: Drip

class PoSEpochRewardInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    accountRewards: Sequence[PoSAccountRewardsInfo]
    powEpochHash: Hash32
    """
    accountRewards: Sequence[PoSAccountRewardsInfo]
    powEpochHash: Hash32

class DAOVoteInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    powBaseReward: Drip
    interestRate: int
    """
    powBaseReward: Drip
    interestRate: int

class SupplyInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    totalIssued: Drip
    totalCollateral: Drip
    totalStaking: Drip
    totalCirculating: Drip
    totalEspaceTokens: Drip
    """
    totalIssued: Drip
    totalCollateral: Drip
    totalStaking: Drip
    totalCirculating: Drip
    totalEspaceTokens: Drip

class PendingInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    localNonce: Nonce
    pendingNonce: Nonce
    pendingCount: int
    nextPendingTx: Hash32
    """
    localNonce: Nonce
    pendingNonce: Nonce
    pendingCount: int
    nextPendingTx: Hash32

class PendingTransactionStatus(TypedDict):
    pending: Literal["futureNonce", "notEnoughCash"]

class PendingTransactionsInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    firstTxStatus: Union[PendingTransactionStatus, Literal["ready"]]
    pendingCount: int
    pendingTransactions: Sequence[TxData]
    """
    firstTxStatus: Union[PendingTransactionStatus, Literal["ready"]]
    pendingCount: int
    pendingTransactions: Sequence[TxData]

class TransactionPaymentInfo(TypedDict):
    """

    Key and type of corresponding value
    ----------
    isBalanceEnough: bool
    willPayCollateral: bool
    willPayTxFee: bool
    """
    isBalanceEnough: bool
    willPayCollateral: bool
    willPayTxFee: bool

__all__ = [
    "TxDict",
    "TxParam",
    "HexAddress",
    "Drip",
    "CFX",
    "GDrip",
    "AddressParam",
    "Storage",
    "EpochNumberParam",
    "EpochLiteral",
    "EpochNumber",
    "NodeStatus",
    "EstimateResult",
    "FilterParams",
    "TransactionLogReceipt",
    "LogReceipt",
    "TransactionEventData",
    "EventData",
    "TxReceipt",
    "TxData",
    "BlockData",
    "MiddlewareOnion",
    "StorageRoot",
    "SponsorInfo",
    "AccountInfo",
    "DepositInfo",
    "VoteInfo",
    "BlockRewardInfo",
    "PoSEconomicsInfo",
    "PoSAccountRewardsInfo",
    "PoSEpochRewardInfo",
    "DAOVoteInfo",
    "SupplyInfo",
    "PendingInfo",
    "PendingTransactionsInfo",
    "TransactionPaymentInfo"
]
