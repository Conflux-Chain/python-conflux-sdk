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

BlockParam = Literal["latest_checkpoint", "earliest", "latest_finalized", "latest_confirmed", "latest_state", "latest_mined"]
BlockIdentifier = Union[BlockParam, BlockNumber, _Hash32, int]
ChainId = Union[int, HexStr]
Storage = NewType("Storage", int)

NodeStatus = TypedDict(
    "NodeStatus",
    {
        "bestHash": HexBytes,
        "chainId": int,
        "networkId": int,
        "blockNumber": int,
        "epochNumber": int,
        "latestCheckpoint": int,
        "latestConfirmed": int,
        "latestState": int,
        "latestFinalized": int,
        "ethereumSpaceChainId": int,
        "pendingTxNumber": int,
    }
)

EstimateResult = TypedDict(
    "EstimateResult",
    {
        "gasLimit": int,
        "gasUsed": int,
        "storageCollateralized": Storage,
    }
)

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


class LogReceipt(TypedDict):
    address: AddressParam
    blockHash: HexBytes
    blockNumber: BlockNumber
    data: HexStr
    logIndex: int
    payload: HexBytes
    removed: bool
    topic: HexBytes
    topics: Sequence[HexBytes]
    transactionHash: HexBytes
    transactionIndex: int

TxReceipt = TypedDict(
    "TxReceipt",
    {
        "transactionHash": _Hash32,
        "index": int,
        "blockHash": _Hash32,
        "blockNumber": int,
        "from": AddressParam,
        "to": AddressParam,
        "gasUsed": Drip,
        "gasFee": Drip,
        "gasCoveredBySponsor": bool,
        "storageCollateralized": Storage,
        "storageCoveredBySponsor": bool,
        "storageReleased": Sequence[Storage],
        "contractAddress": AddressParam,
        
        "stateRoot": _Hash32,
        "outcomStatus": int,
        "logsBloom": HexBytes,
        
        "logs": List[LogReceipt]
    },
)

# class OutcomStatus(Enum)


TxData = TypedDict(
    "TxData",
    {
        "blockHash": HexBytes,
        "chainId": int,
        "contracCreated": AddressParam,
        "data": HexBytes,
        "epochHeight": int,
        "from": AddressParam,
        "gas": int,
        "gasPrice": Drip,
        "hash": _Hash32,
        "nonce": Nonce,
        "r": HexBytes,
        "s": HexBytes,
        "status": int,
        "storageLimit": Storage,
        "to": AddressParam,
        "transactionIndex": int,
        "v": int,
        "value": Drip,
    },
    total=False,
)

TxParam = Union[TxDict, dict[str, Any]]

Middleware = Callable[[Callable[[RPCEndpoint, Any], RPCResponse], "Web3"], Any]
MiddlewareOnion = NamedElementOnion[str, Middleware]
