from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
    Dict,
    cast,
    overload
)
import functools
# from eth_typing import Address
from hexbytes import HexBytes

from eth_utils.toolz import (
    keyfilter  # type: ignore
)
from web3.eth import (
    BaseEth, 
    Eth
)
from web3._utils.empty import (
    Empty,
    empty,
)
from web3._utils.threads import (
    Timeout,
)
from web3.method import (
    # DeprecatedMethod,
    default_root_munger,
)
from web3.datastructures import (
    AttributeDict,
)
from web3.types import (
    _Hash32,
)
from web3.exceptions import (
    TransactionNotFound,
    TimeExhausted
)

from eth_typing.encoding import HexStr
from eth_utils.toolz import assoc  # type: ignore

from cfx_address import Base32Address as CfxAddress
from cfx_account import Account as CfxAccount
from cfx_account.account import LocalAccount

from conflux_web3._utils.rpc_abi import RPC
from conflux_web3._utils.method_formatters import cfx_request_formatters
from conflux_web3.types import (
    Drip,
    EpochLiteral,
    EpochNumberParam,
    AddressParam,
    EstimateResult,
    Base32Address,
    TxParam,
    TxReceipt,
    TxData,
    NodeStatus,
    FilterParams,
    LogReceipt,
    BlockData
)
from conflux_web3.contract import (
    ConfluxContract
)
from conflux_web3._utils.validation import (
    validate_base32
)
from conflux_web3._utils.transactions import (
    fill_formal_transaction_defaults
)
from conflux_web3.method import (
    ConfluxMethod
)
from conflux_web3.middleware.pending import (
    TransactionHash
)
from conflux_web3._utils.decorators import (
    disabled_api,
    use_instead
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

class BaseCfx(BaseEth):
    _default_block: EpochNumberParam = "latest_state"
    _default_account: Union[AddressParam, Empty] = empty
    w3: "Web3"
    
    @property
    def default_account(self) -> Union[AddressParam, Empty]:
        """default account address rather than a local account with private key
        """
        return self._default_account
    

    @default_account.setter
    def default_account(self, account: Union[AddressParam, LocalAccount, Empty]) -> None:
        """set default account address
        Args:
            account: an address or a local account (but only address field works)
        """
        if getattr(account, "address", None):
            validate_base32(account.address) # type: ignore
            self._default_account = account.address # type: ignore
        else:
            validate_base32(account)
            self._default_account = account # type: ignore
    
    def remove_default_account(self):
        self._default_account = empty
    
    def send_transaction_munger(self, transaction: TxParam) -> Tuple[TxParam]:
        if 'from' not in transaction and self.default_account :
            transaction = assoc(transaction, 'from', self.default_account)
        transaction = fill_formal_transaction_defaults(self.w3, transaction)
        return (transaction,)
    
    def estimate_gas_and_collateral_munger(
        self, transaction: TxParam, block_identifier: Optional[EpochNumberParam]=None
    ) -> Sequence[Union[TxParam, EpochNumberParam]]:
        if "from" not in transaction and self.default_account:
            transaction = assoc(transaction, "from", self.default_account)

        if block_identifier is None:
            params = [transaction]
        else:
            params = [transaction, block_identifier]

        return params
    
    def default_account_munger(
        self, address: Optional[Union[AddressParam, LocalAccount, Empty]]=None, block_identifier: Optional[EpochNumberParam]=None
    ) -> Sequence[Union[AddressParam, Empty, EpochNumberParam]]:
        if not address:
            if self.default_account:
                address = self.default_account
            else:
                raise ValueError(
                    "address parameter is required, set address or set 'web3.cfx.default_account'"
                )

        return [address, block_identifier] # type: ignore
    
    _clientVersion: ConfluxMethod[Callable[[], str]] = ConfluxMethod(
        RPC.cfx_clientVersion,
    )
    
    _get_status: ConfluxMethod[Callable[[], AttributeDict]] = ConfluxMethod(
        RPC.cfx_getStatus,
    )

    _gas_price: ConfluxMethod[Callable[[], int]] = ConfluxMethod(
        RPC.cfx_gasPrice,
    )
    
    
    _estimate_gas_and_collateral: ConfluxMethod[Callable[..., EstimateResult]] = ConfluxMethod(
        RPC.cfx_estimateGasAndCollateral, mungers=[estimate_gas_and_collateral_munger]
    )
    
    _accounts: ConfluxMethod[Callable[[], Tuple[Base32Address]]] = ConfluxMethod(
        RPC.accounts
    )
    
    _call: ConfluxMethod[Callable[[TxParam, EpochNumberParam], Any]] = ConfluxMethod(
        RPC.cfx_call,
        mungers=[default_account_munger]
    )
    
    _get_balance: ConfluxMethod[Callable[..., int]] = ConfluxMethod(
        RPC.cfx_getBalance,
        mungers=[default_account_munger]
    )
    
    _epoch_number: ConfluxMethod[Callable[..., EpochLiteral]] = ConfluxMethod(
        RPC.cfx_epochNumber,
    )
    
    _get_next_nonce: ConfluxMethod[Callable[..., int]] = ConfluxMethod(
        RPC.cfx_getNextNonce,
        mungers=[default_account_munger]
    )
    
    _send_raw_transaction: ConfluxMethod[Callable[[Union[HexStr, bytes]], HexBytes]] = ConfluxMethod(
        RPC.cfx_sendRawTransaction
    )
    
    _send_transaction: ConfluxMethod[Callable[[TxParam], HexBytes]] = ConfluxMethod(
        RPC.cfx_sendTransaction,
        mungers=[send_transaction_munger],
    )
    
    _get_confirmation_risk_by_hash: ConfluxMethod[Callable[[_Hash32], float]] = ConfluxMethod(
        RPC.cfx_getConfirmationRiskByHash,
    )
    
    _get_transaction_receipt: ConfluxMethod[Callable[[_Hash32], TxReceipt]] = ConfluxMethod(
        RPC.cfx_getTransactionReceipt
    )
    
    _get_transaction_by_hash: ConfluxMethod[Callable[[_Hash32], TxData]] = ConfluxMethod(
        RPC.cfx_getTransactionByHash
    )
    
    _get_block_by_hash: ConfluxMethod[Callable[[_Hash32, bool], BlockData]] = ConfluxMethod(
        RPC.cfx_getBlockByHash
    )
    
    _get_block_by_epoch_number: ConfluxMethod[Callable[[EpochNumberParam, bool], BlockData]] = ConfluxMethod(
        RPC.cfx_getBlockByEpochNumber
    )
    
    _get_block_by_block_number: ConfluxMethod[Callable[[int, bool], BlockData]] = ConfluxMethod(
        RPC.cfx_getBlockByBlockNumber
    )
    
    _get_best_block_hash: ConfluxMethod[Callable[[None], HexBytes]] = ConfluxMethod(
        RPC.cfx_getBestBlockHash
    )
    
    _get_blocks_by_epoch: ConfluxMethod[Callable[[EpochNumberParam], Sequence[HexBytes]]] = ConfluxMethod(
        RPC.cfx_getBlocksByEpoch
    )
    
    _get_skipped_blocks_by_epoch: ConfluxMethod[Callable[[EpochNumberParam], Sequence[HexBytes]]] = ConfluxMethod(
        RPC.cfx_getSkippedBlocksByEpoch
    )
    
    _get_block_by_hash_with_pivot_assumptions: ConfluxMethod[Callable[[_Hash32, _Hash32, int], BlockData]] = ConfluxMethod(
        RPC.cfx_getBlockByHashWithPivotAssumption
    )
    
    _get_logs: ConfluxMethod[Callable[[FilterParams], List[LogReceipt]]] = ConfluxMethod(
        RPC.cfx_getLogs
    )
    
    @overload
    def contract(
        self, address: None = None, **kwargs: Any
    ) -> Type[ConfluxContract]:
        ...  # noqa: E704,E501

    @overload  # noqa: F811
    def contract(
        self, address: AddressParam, **kwargs: Any
    ) -> ConfluxContract:
        ...  # noqa: E704,E501

    def contract(  # noqa: F811
        self,
        address: Optional[AddressParam] = None,
        **kwargs: Any,
    ) -> Union[Type[ConfluxContract], ConfluxContract]:
        return super().contract(address, **kwargs)  # type: ignore
    

class ConfluxClient(BaseCfx, Eth):
    """RPC entry defined provides friendlier APIs for users
    """
    # an instance of CfxAccount, which means the class variable won't be changed
    account = CfxAccount()
    address = CfxAddress
    defaultContractFactory = ConfluxContract
    
    def get_status(self) -> NodeStatus:
        """
        Returns:
            AttributeDict: node status
            e.g.
            {
                "bestHash": "0xe4bf02ad95ad5452c7676d3dfc2e57fde2a70806c2e68231c58c77cdda5b7c6c",
                "chainId": "0x1",
                "networkId": "0x1",
                "blockNumber": "0x1a80325",
                "epochNumber": "0xaf28ab",
                "latestCheckpoint": "0xada520",
                "latestConfirmed": "0xaf2885",
                "latestState": "0xaf28a7",
                "latestFinalized": "0x2a420c",
                "ethereumSpaceChainId": "0x22b9",
                "pendingTxNumber": "0x0"
            },
        """
        return self._get_status()
    
    @property
    def gas_price(self) -> Drip:
        return self._gas_price()
    
    @property
    def accounts(self) -> Tuple[Base32Address]:
        return self._accounts()
    
    @property
    def epoch_number(self) -> int:
        return self._epoch_number()
    
    def epoch_number_by_tag(self, epochTag: EpochLiteral):
        return self._epoch_number(epochTag)
    
    @functools.cached_property
    def cahched_chain_id(self) -> int:
        return self._get_status()["chainId"]
    
    @property
    def chain_id(self) -> int:
        """We don't use functools.cached_property here in case provider changes network.
        Always get status to avoid unexpected circumstances
        """
        return self._get_status()["chainId"]

    @property
    def client_version(self):
        return self._clientVersion()
    
    # def is_connected(self):
    #     return 
    
    def get_balance(self,
                    address: Optional[AddressParam]=None, 
                    block_identifier: Optional[EpochNumberParam] = None) -> Drip:
        return Drip(self._get_balance(address, block_identifier))
    
    def call(self, 
             transaction: TxParam, 
             block_identifier: Optional[EpochNumberParam]=None, 
             **kwargs):
        """
        Args:
            transaction (TxParam): _description_
            block_identifier (Optional[EpochNumberParam], optional): _description_. Defaults to None.
            kwargs is provided for web3 internal api compatiblity, they will be ignored
        Returns:
            _type_: _description_
        """
        return self._call(transaction, block_identifier)
    
    def get_next_nonce(self, address: Optional[AddressParam]=None, block_identifier: Optional[EpochNumberParam] = None) -> Drip:
        return self._get_next_nonce(address, block_identifier)

    def estimate_gas_and_collateral(self, transaction: TxParam, block_identifier: Optional[EpochNumberParam]=None):
        return self._estimate_gas_and_collateral(transaction, block_identifier)

    def send_raw_transaction(self, raw_transaction: Union[HexStr, bytes]) -> TransactionHash:
        return self._send_raw_transaction(raw_transaction)
    
    def send_transaction(self, transaction: TxParam) -> TransactionHash:
        return self._send_transaction(transaction)
    
    def get_transaction_receipt(self, transaction_hash: _Hash32) -> TxReceipt:
        return self._get_transaction_receipt(transaction_hash)
    
    def wait_till_transaction_mined(
        self, transaction_hash: _Hash32, timeout: float = 60, poll_latency: float = 0.5
    ) -> TxData:
        try:
            with Timeout(timeout) as _timeout:
                while True:
                    try:
                        tx_data = self.get_transaction_by_hash(transaction_hash)
                    except TransactionNotFound:
                        tx_data = None
                    if tx_data is not None and tx_data["blockHash"]:
                        break
                    _timeout.sleep(poll_latency)
            return tx_data

        except Timeout:
            raise TimeExhausted(
                f"Transaction {HexBytes(transaction_hash) !r} is not in the chain "
                f"after {timeout} seconds"
            )
    
    def wait_for_transaction_receipt(
        self, transaction_hash: _Hash32, timeout: float = 300, poll_latency: float = 0.5
    ) -> TxReceipt:
        """_summary_

        Args:
            transaction_hash (_Hash32): _description_
            timeout (float, optional): _description_. Defaults to 300.
            poll_latency (float, optional): _description_. Defaults to 0.5.

        Returns:
            TxReceipt
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
        """
        try:
            receipt = cast(TxReceipt, super().wait_for_transaction_receipt(transaction_hash, timeout, poll_latency))
        except TimeExhausted:
            raise TimeExhausted(
                f"Transaction {HexBytes(transaction_hash) !r} is not executed"
                f"after {timeout} seconds"
            )
        if receipt["outcomeStatus"] != 0:
            raise RuntimeError(f'transaction "${transaction_hash}" execution failed, outcomeStatus ${receipt["outcomeStatus"]}')
        return receipt
    
    def wait_till_transaction_executed(
        self, transaction_hash: _Hash32, timeout: float = 300, poll_latency: float = 0.5
    ) -> TxReceipt:
        return self.wait_for_transaction_receipt(transaction_hash, timeout, poll_latency)
        
    
    def wait_till_transaction_confirmed(
        self, transaction_hash: _Hash32, timeout: float = 600, poll_latency: float = 0.5
    ) -> TxReceipt:
        try:
            with Timeout(timeout) as _timeout:
                while True:
                    try:
                        tx_receipt = self.wait_till_transaction_executed(transaction_hash)
                    except TransactionNotFound:
                        tx_receipt = None
                    if tx_receipt is not None:
                        tx_epoch = tx_receipt["epochNumber"]
                        confirmed_epoch = self.epoch_number_by_tag("latest_confirmed")
                        if tx_epoch <= confirmed_epoch:
                            break
                    _timeout.sleep(poll_latency)
            return tx_receipt
        except Timeout:
            raise TimeExhausted(
                f"Transaction {HexBytes(transaction_hash) !r} is not confirmed "
                f"after {timeout} seconds"
            )
    
    def wait_till_transaction_finalized(
        self, transaction_hash: _Hash32, timeout: float = 1200, poll_latency: float = 0.5
    ) -> TxReceipt:
        try:
            with Timeout(timeout) as _timeout:
                while True:
                    try:
                        tx_receipt = self.wait_till_transaction_executed(transaction_hash)
                    except TransactionNotFound:
                        tx_receipt = None
                    if tx_receipt is not None:
                        tx_epoch = tx_receipt["epochNumber"]
                        finalized_epoch = self.epoch_number_by_tag("latest_finalized")
                        if tx_epoch <= finalized_epoch:
                            break
                    _timeout.sleep(poll_latency)
            return tx_receipt
        except Timeout:
            raise TimeExhausted(
                f"Transaction {HexBytes(transaction_hash) !r} is not finalized "
                f"after {timeout} seconds"
            )
    
    def get_transaction_by_hash(self, transaction_hash: _Hash32) -> TxData:
        return self._get_transaction_by_hash(transaction_hash)
    
    # same as web3.py
    def get_transaction(self, transaction_hash: _Hash32) -> TxData:
        return self.get_transaction_by_hash(transaction_hash)
    
    def get_block_by_hash(
        self, block_hash: _Hash32, full_transactions: bool=False
    ) -> BlockData:
        return self._get_block_by_hash(block_hash, full_transactions)
    
    def get_block_by_epoch_number(
        self, epoch_number_param: EpochNumberParam, full_transactions: bool=False
    ) -> BlockData:
        return self._get_block_by_epoch_number(epoch_number_param, full_transactions)
    
    def get_block_by_block_number(
        self, block_number: int, full_transactions: bool=False
    ) -> BlockData:
        return self._get_block_by_block_number(block_number, full_transactions)
    
    def get_best_block_hash(self) -> HexBytes:
        return self._get_best_block_hash()
    
    def get_blocks_by_epoch(self, epoch_number_param: EpochNumberParam) -> Sequence[HexBytes]:
        return self._get_blocks_by_epoch(epoch_number_param)
    
    def get_skipped_blocks_by_epoch(self, epoch_number_param: EpochNumberParam) -> Sequence[HexBytes]:
        return self._get_skipped_blocks_by_epoch(epoch_number_param)

    def get_block_by_hash_with_pivot_assumptions(self, block_hash: _Hash32, assumed_pivot_hash: _Hash32, epoch_number: int) -> BlockData:
        return self._get_block_by_hash_with_pivot_assumptions(block_hash, assumed_pivot_hash, epoch_number)
    
    def get_confirmation_risk_by_hash(self, block_hash: _Hash32) -> float:
        return self._get_confirmation_risk_by_hash(block_hash)
    
    def get_logs(self, filter_params: Optional[FilterParams]=None, **kwargs):
        if filter_params is None:
            filter_params = keyfilter(lambda key: key in FilterParams.__annotations__.keys(), kwargs)
            return self._get_logs(filter_params)
        else:
            if len(kwargs.keys()) != 0:
                raise ValueError("Redundant Param: FilterParams as get_logs first parameter is already provided")
            return self._get_logs(filter_params)
    
    
    
    @use_instead("estimate_gas_and_collateral")
    def estimate_gas(self, *args, **kwargs):
        """disabled in conflux network. use "estimate_gas_and_collateral" instead
        """
        pass
    
    # @disabled_api
    # def _get
