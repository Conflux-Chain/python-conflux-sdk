from web3.module import (
    Module,
    ModuleV2,
)
from web3.method import (
    Method,
    default_root_munger,
)
from typing import (
    Any,
    Callable,
    List,
    NoReturn,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    cast,
    overload,
)
from conflux.types import (
    Drip,
    EpochNumber,
    EpochIdentifier,
    BlockIdentifier,
    BlockData,
    TxData,
    _Hash32,
    TxReceipt,
    TxParams,
    LogReceipt,
    FilterParams,
    Log,
    ChainStatus,
    Account,
    EstimateResult,
    SponsorInfo,
    RewardInfo
)
from conflux._utils.rpc_abi import RPC
from web3._utils.compat import (
    Literal,
)
from hexbytes import (
    HexBytes,
)
from conflux._utils.method_formatters import (
    get_result_formatters,
    get_request_formatters
)
from eth_typing import (
    # Address,
    # BlockNumber,
    # ChecksumAddress,
    HexStr,
)

from conflux.consts import (
    LATEST_STATE,
    LATEST_MINED
)


class Cfx(ModuleV2, Module):
    defaultEpoch: EpochIdentifier = LATEST_STATE

    gas_price: Method[Callable[[], Drip]] = Method(
        RPC.cfx_gasPrice,
        mungers=None,
        result_formatters=get_result_formatters
    )

    @property
    def gasPrice(self) -> Drip:
        return self.gas_price()

    get_accounts: Method[Callable[[], Tuple[str]]] = Method(
        RPC.accounts,
        mungers=None,
    )

    @property
    def accounts(self) -> Tuple[str]:
        return self.get_accounts()

    def epoch_munger(
            self,
            epoch_identifier: Optional[EpochIdentifier] = None
    ) -> Tuple[EpochIdentifier]:
        if epoch_identifier is None:
            epoch_identifier = LATEST_MINED
        return (epoch_identifier,)

    epochNumber: Method[Callable[[Optional[EpochIdentifier]], EpochNumber]] = Method(
        RPC.cfx_epochNumber,
        mungers=[epoch_munger],
        result_formatters=get_result_formatters,
    )

    def account_id_munger(
            self,
            account: str,
            epoch_identifier: Optional[EpochIdentifier] = None
    ) -> Tuple[str, EpochIdentifier]:
        if epoch_identifier is None:
            epoch_identifier = self.defaultEpoch
        return (account, epoch_identifier)

    getBalance: Method[Callable[..., Drip]] = Method(
        RPC.cfx_getBalance,
        mungers=[account_id_munger],
        request_formatters=get_request_formatters,
        result_formatters=get_result_formatters,
    )

    getStakingBalance: Method[Callable[..., Drip]] = Method(
        RPC.cfx_getStakingBalance,
        mungers=[account_id_munger],
        request_formatters=get_request_formatters,
        result_formatters=get_result_formatters,
    )

    getCollateralForStorage: Method[Callable[..., int]] = Method(
        RPC.cfx_getCollateralForStorage,
        mungers=[account_id_munger],
        request_formatters=get_request_formatters,
        result_formatters=get_result_formatters,
    )

    getAdmin: Method[Callable[..., str]] = Method(
        RPC.cfx_getAdmin,
        mungers=[account_id_munger],
        request_formatters=get_request_formatters,
    )

    getCode: Method[Callable[..., str]] = Method(
        RPC.cfx_getCode,
        mungers=[account_id_munger],
        request_formatters=get_request_formatters,
    )

    getSponsorInfo: Method[Callable[..., SponsorInfo]] = Method(
        RPC.cfx_getSponsorInfo,
        mungers=[account_id_munger],
        request_formatters=get_request_formatters,
    )

    getNextNonce: Method[Callable[..., int]] = Method(
        RPC.cfx_getNextNonce,
        mungers=[account_id_munger],
        request_formatters=get_request_formatters,
        result_formatters=get_result_formatters,
    )

    getAccount: Method[Callable[..., Account]] = Method(
        RPC.cfx_getAccount,
        mungers=[account_id_munger],
        request_formatters=get_request_formatters,
        result_formatters=get_result_formatters,
    )

    getStatus: Method[Callable[..., ChainStatus]] = Method(
        RPC.cfx_getStatus,
        result_formatters=get_result_formatters,
    )

    def get_block_munger(
            self, block_identifier: BlockIdentifier, full_transactions: bool = False
    ) -> Tuple[BlockIdentifier, bool]:
        return (block_identifier, full_transactions)

    """
    `cfx_getBlockByHash`
    """
    getBlockByHash: Method[Callable[..., BlockData]] = Method(
        RPC.cfx_getBlockByHash,
        mungers=[get_block_munger],
        result_formatters=get_result_formatters,
    )

    """
    `cfx_getBlockByEpochNumber`
    """
    getBlockByEpochNumber: Method[Callable[..., BlockData]] = Method(
        RPC.cfx_getBlockByEpochNumber,
        mungers=[get_block_munger],
        request_formatters=get_request_formatters,
        result_formatters=get_result_formatters,
    )

    getBlocksByEpoch: Method[Callable[..., List[str]]] = Method(
        RPC.cfx_getBlocksByEpoch,
        mungers=[default_root_munger],
        request_formatters=get_request_formatters,
    )

    getBlockRewardInfo: Method[Callable[..., List[RewardInfo]]] = Method(
        RPC.cfx_getBlockRewardInfo,
        mungers=[default_root_munger],
        request_formatters=get_request_formatters,
    )

    getTransactionByHash: Method[Callable[[_Hash32], TxData]] = Method(
        RPC.cfx_getTransactionByHash,
        mungers=[default_root_munger],
        request_formatters=get_request_formatters,
        result_formatters=get_result_formatters,
    )

    # def waitForTransactionReceipt(
    #     self, transaction_hash: _Hash32, timeout: int = 120, poll_latency: float = 0.1
    # ) -> TxReceipt:
    #     try:
    #         return wait_for_transaction_receipt(self.web3, transaction_hash, timeout, poll_latency)
    #     except Timeout:
    #         raise TimeExhausted(
    #             "Transaction {} is not in the chain, after {} seconds".format(
    #                 to_hex(transaction_hash),
    #                 timeout,
    #             )
    #         )

    getTransactionReceipt: Method[Callable[[_Hash32], TxReceipt]] = Method(
        RPC.cfx_getTransactionReceipt,
        mungers=[default_root_munger],
        result_formatters=get_result_formatters,
    )

    def send_transaction_munger(self, transaction: TxParams) -> Tuple[TxParams]:
        # if 'from' not in transaction and is_checksum_address(self.defaultAccount):
        #     transaction = assoc(transaction, 'from', self.defaultAccount)
        #
        # # TODO: move gas estimation in middleware
        # if 'gas' not in transaction:
        #     transaction = assoc(
        #         transaction,
        #         'gas',
        #         get_buffered_gas_estimate(self.web3, transaction),
        #     )
        return (transaction,)

    sendTransaction: Method[Callable[[TxParams], HexBytes]] = Method(
        RPC.cfx_sendTransaction,
        mungers=[send_transaction_munger],
        result_formatters=get_result_formatters,
    )

    sendRawTransaction: Method[Callable[[Union[HexStr, bytes]], HexBytes]] = Method(
        RPC.cfx_sendRawTransaction,
        mungers=[default_root_munger],
        result_formatters=get_result_formatters,
    )

    def call_munger(
            self,
            transaction: TxParams,
            block_identifier: Optional[BlockIdentifier] = None
    ) -> Tuple[TxParams, BlockIdentifier]:
        # if 'from' not in transaction and is_checksum_address(self.defaultAccount):
        #     transaction = assoc(transaction, 'from', self.defaultAccount)

        if block_identifier is None:
            block_identifier = self.defaultEpoch

        return (transaction, block_identifier)

    call: Method[Callable[..., Union[bytes, bytearray]]] = Method(
        RPC.cfx_call,
        mungers=[call_munger]
    )

    def estimate_gas_munger(
            self,
            transaction: TxParams,
            block_identifier: Optional[BlockIdentifier] = None
    ) -> Sequence[Union[TxParams, BlockIdentifier]]:
        # if 'from' not in transaction and is_checksum_address(self.defaultAccount):
        #     transaction = assoc(transaction, 'from', self.defaultAccount)

        if block_identifier is None:
            params: Sequence[Union[TxParams, BlockIdentifier]] = [transaction]
        else:
            params = [transaction, block_identifier]

        return params

    estimateGasAndCollateral: Method[Callable[..., EstimateResult]] = Method(
        RPC.cfx_estimateGasAndCollateral,
        mungers=[estimate_gas_munger],
        request_formatters=get_request_formatters,
        result_formatters=get_result_formatters,
    )

    getLogs: Method[Callable[[FilterParams], List[Log]]] = Method(
        RPC.cfx_getLogs,
        mungers=[default_root_munger],
        request_formatters=get_request_formatters,
        result_formatters=get_result_formatters,
    )

    getBestBlockHash: Method[Callable[..., str]] = Method(
        RPC.cfx_getBestBlockHash,
        mungers=[default_root_munger],
    )

    def populate_transaction(self, tx):
        if "nonce" not in tx:
            tx["nonce"] = self.getNextNonce(tx["from"])
        if "chainId" not in tx:
            status = self.getStatus()
            tx["chainId"] = status["chainId"]
        if "epochHeight" not in tx:
            tx["epochHeight"] = self.epochNumber()
        if "gasPrice" not in tx:
            tx["gasPrice"] = 1
        if "gas" not in tx or "storageLimit" not in tx:
            estimate = self.estimateGasAndCollateral(tx)
            if "gas" not in tx:
                tx["gas"] = estimate["gasLimit"]
            if "storageLimit" not in tx:
                tx["storageLimit"] = estimate["storageCollateralized"]

    # getConfirmationRiskByHash: Method[Callable[..., str]] = Method(
    #     RPC.cfx_getConfirmationRiskByHash,
    #     mungers=[default_root_munger],
    #     result_formatters=get_result_formatters,
    # )
