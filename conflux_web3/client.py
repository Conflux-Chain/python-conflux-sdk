from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Literal,
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
import warnings
from hexbytes import HexBytes

from toolz import (
    keyfilter,
    merge,
    dissoc,
)
from eth_typing.encoding import (
    HexStr
)
from eth_utils.toolz import (
    assoc  # type: ignore
)

from web3.eth import (
    BaseEth, 
    Eth
)
# empty means a empty address but is not None
from web3._utils.empty import (
    Empty,
    empty,
)
from web3._utils.threads import (
    Timeout,
)
from web3.exceptions import (
    TransactionNotFound,
    TimeExhausted
)
from web3._utils.blocks import is_hex_encoded_block_hash as is_hash32_str

from cfx_utils.token_unit import (
    to_int_if_drip_units,
    AbstractDerivedTokenUnit
)
from cfx_address import (
    Base32Address as CfxAddress,
    validate_base32
)
from cfx_account import Account as CfxAccount
from cfx_account.account import (
    LocalAccount
)

from conflux_web3._utils.rpc_abi import (
    RPC
)
from conflux_web3._utils.disabled_eth_apis import (
    disabled_method_list,
)
from conflux_web3.types import (
    _Hash32,
    Drip,
    CFX,
    GDrip,
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
    BlockData,
    SponsorInfo,
    AccountInfo,
    DepositInfo,
    VoteInfo,
    Storage,
    StorageRoot,
    EpochNumber,
    BlockRewardInfo,
    PendingInfo,
    PoSEconomicsInfo,
    PoSEpochRewardInfo,
    DAOVoteInfo,
    SupplyInfo,
    PendingInfo,
    PendingTransactionsInfo,
    TransactionPaymentInfo,
)
from conflux_web3.contract import (
    ConfluxContract
)
from conflux_web3.contract.metadata import (
    get_contract_metadata
)
from conflux_web3._utils.transactions import (
    fill_transaction_defaults
)
from conflux_web3.method import (
    ConfluxMethod
)
from conflux_web3.middleware.pending import (
    TransactionHash
)
from conflux_web3._utils.decorators import (
    use_instead,
)
from conflux_web3._utils.cns import (
    resolve_if_cns_name,
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

class BaseCfx(BaseEth):
    _default_block: EpochNumberParam = "latest_state"
    _default_account: Union[AddressParam, Empty] = empty
    w3: "Web3"
    
    @property
    def default_account(self) -> Base32Address:
        """default account ADDRESS rather than a local account with private key
        """
        return self._default_account # type: ignore
    

    @default_account.setter
    def default_account(self, account: Union[AddressParam, LocalAccount]) -> None:
        """set default account address
        """
        if isinstance(account, LocalAccount):
            self._default_account = Base32Address(account.address)
            if (self.w3.wallet is not None and account.address not in self.w3.wallet):
                self.w3.wallet.add_account(account)
        else:
            self._default_account = Base32Address(resolve_if_cns_name(self.w3, account))
    
    def remove_default_account(self):
        self._default_account = empty
    
    def send_transaction_munger(self, transaction: TxParam) -> Tuple[TxParam]:
        if 'from' not in transaction and self.default_account:
            transaction = assoc(transaction, 'from', self.default_account)
        if 'value' in transaction:
            transaction['value'] = to_int_if_drip_units(transaction['value'])
        if 'gasPrice' in transaction:
            transaction['gasPrice'] = to_int_if_drip_units(transaction['gasPrice'])
        transaction = fill_transaction_defaults(self.w3, transaction)
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
    
    _get_status: ConfluxMethod[Callable[[], NodeStatus]] = ConfluxMethod(
        RPC.cfx_getStatus,
    )

    _gas_price: ConfluxMethod[Callable[[], Drip]] = ConfluxMethod(
        RPC.cfx_gasPrice,
    )
    
    
    _estimate_gas_and_collateral: ConfluxMethod[Callable[..., EstimateResult]] = ConfluxMethod(
        RPC.cfx_estimateGasAndCollateral, mungers=[estimate_gas_and_collateral_munger]
    )
    
    _accounts: ConfluxMethod[Callable[[], Tuple[Base32Address]]] = ConfluxMethod(
        RPC.accounts
    )
    
    _call: ConfluxMethod[Callable[[TxParam, Optional[EpochNumberParam]], Any]] = ConfluxMethod(
        RPC.cfx_call,
        mungers=[default_account_munger]
    )
    
    _get_balance: ConfluxMethod[Callable[..., Drip]] = ConfluxMethod(
        RPC.cfx_getBalance,
        # mungers=[default_account_munger]
    )
    
    _get_staking_balance: ConfluxMethod[Callable[[AddressParam, Optional[EpochNumberParam]], Drip]] = ConfluxMethod(
        RPC.cfx_getStakingBalance
    )
    
    _epoch_number: ConfluxMethod[Callable[[Optional[EpochLiteral]], EpochNumber]] = ConfluxMethod(
        RPC.cfx_epochNumber,
    )
    
    _get_next_nonce: ConfluxMethod[Callable[..., int]] = ConfluxMethod(
        RPC.cfx_getNextNonce,
        # mungers=[default_account_munger]
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
    
    _get_best_block_hash: ConfluxMethod[Callable[[], HexBytes]] = ConfluxMethod(
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
    
    
    _get_code: ConfluxMethod[Callable[[AddressParam, EpochNumberParam], HexBytes]] = ConfluxMethod(
        RPC.cfx_getCode
    )
    
    _get_storage_at: ConfluxMethod[Callable[[AddressParam, int, EpochNumberParam], Union[HexBytes, None]]] = ConfluxMethod(
        RPC.cfx_getStorageAt
    )
    
    _get_storage_root: ConfluxMethod[Callable[[AddressParam, EpochNumberParam], Union[HexBytes, None]]] = ConfluxMethod(
        RPC.cfx_getStorageRoot
    )
    
    _get_collateral_for_storage: ConfluxMethod[Callable[[AddressParam, EpochNumberParam], Storage]] = ConfluxMethod(
        RPC.cfx_getCollateralForStorage
    )
    
    _get_admin: ConfluxMethod[Callable[[AddressParam, EpochNumberParam], Union[Base32Address, None]]] = ConfluxMethod(
        RPC.cfx_getAdmin
    )
    
    _get_sponsor_info: ConfluxMethod[Callable[[AddressParam, EpochNumberParam], SponsorInfo]] = ConfluxMethod(
        RPC.cfx_getSponsorInfo
    )
    
    _get_account: ConfluxMethod[Callable[[AddressParam, EpochNumberParam], AccountInfo]] = ConfluxMethod(
        RPC.cfx_getAccount
    )
    
    _get_deposit_list: ConfluxMethod[Callable[[AddressParam, EpochNumberParam], Sequence[DepositInfo]]] = ConfluxMethod(
        RPC.cfx_getDepositList
    )
    
    _get_vote_list: ConfluxMethod[Callable[[AddressParam, EpochNumberParam], Sequence[VoteInfo]]] = ConfluxMethod(
        RPC.cfx_getVoteList
    )
    
    _get_interest_rate = ConfluxMethod(
        RPC.cfx_getInterestRate
    )
    
    _get_accumulate_interest_rate = ConfluxMethod(
        RPC.cfx_getAccumulateInterestRate
    )
    
    _get_block_reward_info = ConfluxMethod(
        RPC.cfx_getBlockRewardInfo
    )
    
    _get_pos_economics = ConfluxMethod(
        RPC.cfx_getPoSEconomics
    )
    
    _get_pos_reward_by_epoch = ConfluxMethod(
        RPC.cfx_getPoSRewardByEpoch
    )
    
    _get_params_from_vote = ConfluxMethod(
        RPC.cfx_getParamsFromVote
    )
    
    _get_supply_info = ConfluxMethod(
        RPC.cfx_getSupplyInfo
    )
    
    _get_account_pending_info = ConfluxMethod(
        RPC.cfx_getAccountPendingInfo
    )
    
    _get_account_pending_transactions = ConfluxMethod(
        RPC.cfx_getAccountPendingTransactions
    )
    
    _check_balance_against_transaction = ConfluxMethod(
        RPC.cfx_checkBalanceAgainstTransaction
    )
    
    _get_logs: ConfluxMethod[Callable[[FilterParams], List[LogReceipt]]] = ConfluxMethod(
        RPC.cfx_getLogs
    )
    
    # TODO: change overload definitions with name parameter
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
        name: Optional[str] = None,
        with_deployment_info: Optional[bool] = None,
        **kwargs: Any,
    ) -> Union[Type[ConfluxContract], ConfluxContract]:
        metadata = {}
        if name is not None:
            metadata = get_contract_metadata(name, self.chain_id, with_deployment_info) # type: ignore
            # the latter one shares greater priority when merging
            kwargs = merge(metadata, kwargs)
        if address is not None:
            kwargs["address"] = address
        return super().contract(**kwargs)  # type: ignore
    

class ConfluxClient(BaseCfx, Eth):
    """RPC entry defined provides friendlier APIs for users
    """
    # an instance of CfxAccount, which means the class variable won't be changed
    account = CfxAccount()
    address = CfxAddress
    defaultContractFactory = ConfluxContract
    
    def __init__(self, w3: "Web3") -> None:
        super().__init__(w3)
        self.disable_eth_methods(disabled_method_list)
        
    def disable_eth_methods(self, disabled_method_list: Sequence[str]):
        for api in disabled_method_list:
            self.__setattr__(
                api,
                use_instead(origin=api)(
                    lambda *args, **kwargs: 0    
                ),
            )
    
    @use_instead
    @property
    def syncing(self):
        pass
    
    @use_instead
    @property
    def coinbase(self):
        pass
    
    @use_instead
    @property
    def mining(self):
        pass
    
    @use_instead
    @property
    def hashrate(self):
        pass
    
    @use_instead(origin="web3.eth.block_number", substitute="web3.cfx.epoch_number")
    @property
    def block_number(self):
        pass
    
    @use_instead
    @property
    def max_priority_fee(self):
        pass
    
    @use_instead
    @property
    def get_work(self):
        pass
    
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
    def gas_price(self) -> GDrip:
        return self._gas_price().to(GDrip)
    
    @property
    def accounts(self) -> Tuple[Base32Address]:
        return self._accounts()
    
    @property
    def epoch_number(self) -> EpochNumber:
        return self._epoch_number()
    
    def epoch_number_by_tag(self, epochTag: EpochLiteral) -> EpochNumber:
        return self._epoch_number(epochTag)
    
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
                    address: AddressParam, 
                    block_identifier: Optional[EpochNumberParam] = None) -> CFX:
        return self._get_balance(address, block_identifier).to(CFX)
    
    def get_staking_balance(self,
                    address: AddressParam, 
                    block_identifier: Optional[EpochNumberParam] = None) -> CFX:
        return self._get_staking_balance(address, block_identifier).to(CFX)
    
    
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
    
    def get_next_nonce(self, address: Optional[AddressParam]=None, block_identifier: Optional[EpochNumberParam] = None) -> int:
        return self._get_next_nonce(address, block_identifier)

    def get_transaction_count(self, address: Optional[AddressParam]=None, block_identifier: Optional[EpochNumberParam] = None) -> int:
        return self.get_next_nonce(address, block_identifier)

    def estimate_gas_and_collateral(self, transaction: TxParam, block_identifier: Optional[EpochNumberParam]=None) -> EstimateResult:
        return self._estimate_gas_and_collateral(transaction, block_identifier)

    def estimate_gas(self, transaction: TxParam, block_identifier: Optional[EpochNumberParam] = None) -> EstimateResult:
        """
        Compatibility API for conflux. Equivalent to estimate_gas_and_collateral

        Parameters
        ----------
        transaction : TxParam
            {
                "chainId": int,
                "data": Union[bytes, HexStr],
                "from": Base32Address,
                "gas": int,
                "gasPrice": Drip,
                "nonce": Nonce,
                "to": Base32Address,
                "value": Drip,
                "epochHeight": int,
                "storageLimit": int
            }
        block_identifier : Optional[EpochNumberParam], optional
            _description_, by default None

        Returns
        -------
        EstimateResult
        
        e.g.
        {
            "gasLimit": 28000,
            "gasUsed": 21000,
            "storageCollateralized": 0
        }
        """        
        return self.estimate_gas_and_collateral(transaction, block_identifier)

    def send_raw_transaction(self, raw_transaction: Union[HexStr, bytes]) -> TransactionHash:
        # TODO: remove pending middleware and changes here
        return self._send_raw_transaction(raw_transaction)
    
    def send_transaction(self, transaction: TxParam) -> TransactionHash:
        # TODO: remove pending middleware and changes here
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
                "gasUsed": int,
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
            receipt = cast(TxReceipt, super().wait_for_transaction_receipt(transaction_hash, timeout, poll_latency)) # type: ignore
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
        warnings.warn("10 ~ 15 minutes are required to finalize a transaction", UserWarning)
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
    
    def get_block(self, block_identifier: Union[_Hash32, EpochNumberParam], full_transactions: bool = False) -> BlockData:
        """
        a simple wrapper combining web3.cfx.get_block_by_hash and web3.cfx.get_block_by_epoch_number

        Parameters
        ----------
        block_identifier : Union[_Hash32, EpochNumberParam]
            block hash or epoch number parameter(e.g. string "latest_state" or epoch number)
            # note: DON'T USE BLOCK NUMBER as the parameter #
        full_transactions : bool, optional
            whether the return block data contains full transaction info or just transaction hash, by default False

        Returns
        -------
        BlockData
            e.g.
            {
                "adaptive": false,
                "blame": 0,
                "deferredLogsBloomHash": "0xd397b3b043d87fcd6fad1291ff0bfd16401c274896d8c63a923727f077b8e0b5",
                "deferredReceiptsRoot": "0x522717233b96e0a03d85f02f8127aa0e23ef2e0865c95bb7ac577ee3754875e4",
                "deferredStateRoot": "0xd449df4ba49f5ab02abf261e976197beecf93c5198a6f0b6bd2713d84115c4ec",
                "difficulty": "0xeee440",
                "epochNumber": "0x1394cb",
                "gasLimit": "0xb2d05e00",
                "gasUsed": "0xad5ae8",
                "hash": "0x692373025c7315fa18b2d02139d08e987cd7016025920f59ada4969c24e44e06",
                "height": "0x1394c9",
                "miner": "CFX:TYPE.USER:AARC9ABYCUE0HHZGYRR53M6CXEDGCCRMMYYBJGH4XG",
                "nonce": "0x329243b1063c6773",
                "parentHash": "0xd1c2ff79834f86eb4bc98e0e526de475144a13719afba6385cf62a4023c02ae3",
                "powQuality": "0x2ab0c3513",
                "refereeHashes": [
                "0xcc103077ede14825a5667bddad79482d7bbf1f1a658fed6894fa0e9287fc6be1"
                ],
                "size": "0x180",
                "timestamp": "0x5e8d32a1",
                "transactions": [
                "0xedfa5b9c38ba51e791cc72b8f75ff758533c8c38f426eddee3fd95d984dd59ff"
                ],
                "custom": ["0x12"],
                "transactionsRoot": "0xfb245dae4539ea49812e822adbffa9dd2ee9b3de8f3d9a7d186d351dcc9a6ed4",
                "posReference": "0xd1c2ff79834f86eb4bc98e0e526de475144a13719afba6385cf62a4023c02ae3",
            } 
        """
        # TODO: more fine-grained munger
        if block_identifier == "latest":
            block_identifier = "latest_state"  
        elif isinstance(block_identifier, bytes) or is_hash32_str(block_identifier):
            return self.get_block_by_hash(block_identifier, full_transactions) # type: ignore
        return self.get_block_by_epoch_number(block_identifier, full_transactions) # type: ignore
    
    def get_code(
        self, address: AddressParam, block_identifier: Optional[EpochNumberParam] = None
    ) -> HexBytes:
        return self._get_code(address, block_identifier)
    
    def get_storage_at(
        self, address: AddressParam, storage_position: int, block_identifier: Optional[EpochNumberParam] = None
    ) -> Union[HexBytes, None]:
        return self._get_storage_at(address, storage_position, block_identifier)
    
    def get_storage_root(
        self, address: AddressParam, block_identifier: Optional[EpochNumberParam] = None
    ) -> StorageRoot:
        return self._get_storage_root(address, block_identifier)
    
    def get_collateral_for_storage(
        self, address: AddressParam, block_identifier: Optional[EpochNumberParam] = None
    ) -> Storage:
        return self._get_collateral_for_storage(address, block_identifier)
    
    def get_sponsor_info(
        self, address: AddressParam, block_identifier: Optional[EpochNumberParam] = None
    ) -> SponsorInfo:
        return self._get_sponsor_info(address, block_identifier)
    
    def get_account(
        self, address: AddressParam, block_identifier: Optional[EpochNumberParam] = None
    ) -> AccountInfo:
        return self._get_account(address, block_identifier)
    
    def get_deposit_list(
        self, address: AddressParam, block_identifier: Optional[EpochNumberParam] = None
    ) -> Sequence[DepositInfo]:
        return self._get_deposit_list(address, block_identifier)
    
    def get_vote_list(
        self, address: AddressParam, block_identifier: Optional[EpochNumberParam] = None
    ) -> Sequence[VoteInfo]:
        return self._get_vote_list(address, block_identifier)
    
    def get_interest_rate(
        self, block_identifier: Optional[EpochNumberParam] = None
    ) -> int:
        return self._get_interest_rate(block_identifier)
    
    def get_accumulate_interest_rate(
        self, block_identifier: Optional[EpochNumberParam] = None
    ) -> int:
        return self._get_accumulate_interest_rate(block_identifier)
    
    def get_block_reward_info(
        self, block_identifier: Union[EpochNumber, int, Literal["latest_checkpoint"] ]
    ) -> Sequence[BlockRewardInfo]:
        return self._get_block_reward_info(block_identifier)
    
    def get_pos_economics(
        self, block_identifier: Optional[EpochNumberParam] = None
    ) -> PoSEconomicsInfo:
        return self._get_pos_economics(block_identifier)
    
    def get_pos_reward_by_epoch(
        self, epoch_number: Union[EpochNumber, int]
    ) -> Union[PoSEpochRewardInfo, None]:
        return self._get_pos_reward_by_epoch(epoch_number)
    
    def get_params_from_vote(
        self, block_identifier: Optional[EpochNumberParam] = None
    ) -> DAOVoteInfo:
        return self._get_params_from_vote(block_identifier)
    
    def get_supply_info(self) -> SupplyInfo:
        return self._get_supply_info()
    
    def get_account_pending_info(
        self, address: AddressParam
    ) -> PendingInfo:
        return self._get_account_pending_info(address)
    
    def get_account_pending_transactions(
        self, address: AddressParam, start_nonce: Optional[int]=None, limit: Optional[int]=None
    ) -> PendingTransactionsInfo:
        return self._get_account_pending_transactions(address, start_nonce, limit)
    
    def check_balance_against_transaction(
        self,
        account_address: AddressParam,
        contract_address: AddressParam, 
        gas_limit: int,
        gas_price: Union[Drip, AbstractDerivedTokenUnit[Drip], int],
        storage_limit: Union[Storage, int],
        block_identifier: Optional[EpochNumberParam] = None
    ) -> TransactionPaymentInfo:
        gas_price = to_int_if_drip_units(gas_price)
        return self._check_balance_against_transaction(
            account_address, contract_address, gas_limit, gas_price, storage_limit, block_identifier
        )
    
    def get_logs(self, filter_params: Optional[FilterParams]=None, **kwargs):
        if filter_params is None:
            filter_params = keyfilter(lambda key: key in FilterParams.__annotations__.keys(), kwargs) # type: ignore
            return self._get_logs(filter_params)
        else:
            if len(kwargs.keys()) != 0:
                raise ValueError("Redundant Param: FilterParams as get_logs first parameter is already provided")
            return self._get_logs(filter_params)

