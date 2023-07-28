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
from typing_extensions import (
    Literal
)
import warnings
from hexbytes import HexBytes

from cytoolz import ( keyfilter, merge ) # type:ignore
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
from cfx_utils.types import (
    _Hash32,
    Drip,
    EpochLiteral,
    EpochNumberParam,
    AddressParam,
    TxParam,
    EpochNumber,
    Storage,
)
from cfx_address import (
    Base32Address,
)
from cfx_address.address import (
    get_base32_address_factory,
)
from cfx_account import (
    Account,
    LocalAccount,
)

from conflux_web3._utils.decorators import (
    cached_property
)
from conflux_web3._utils.rpc_abi import (
    RPC
)
from conflux_web3._utils.disabled_eth_apis import (
    disabled_method_list,
)
from conflux_web3.types import (
    EstimateResult,
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
    StorageRoot,
    BlockRewardInfo,
    PendingInfo,
    PoSEconomicsInfo,
    PoSEpochRewardInfo,
    DAOVoteInfo,
    SupplyInfo,
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
    def default_block(self) -> EpochNumberParam:
        return self._default_block

    @default_block.setter
    def default_block(self, value: EpochNumberParam) -> None:
        self._default_block = value
    
    @property
    def default_account(self) -> Base32Address:
        """default account address, this address will be used as default `from` address if transaction `from` field is empty
        """
        return self._default_account # type: ignore
    

    @default_account.setter
    def default_account(self, account: Union[Base32Address, str, LocalAccount]) -> None:
        """set default account address
        """
        if isinstance(account, LocalAccount):
            normalized_address = Base32Address(account.address)
            self._default_account = normalized_address
            if (self.w3.wallet is not None and account.address not in self.w3.wallet):
                self.w3.wallet.add_account(account)
            if self.w3.cns:
                self.w3.cns.w3.cfx.default_account = normalized_address
        else:
            normalized_address = Base32Address(resolve_if_cns_name(self.w3, account))
            self._default_account = normalized_address
            if self.w3.cns:
                self.w3.cns.w3.cfx.default_account = normalized_address
    
    def remove_default_account(self) -> None:
        self._default_account = empty
        if self.w3.cns:
            self.w3.cns.w3.cfx.remove_default_account()
    
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
    ) -> Tuple[TxParam, Optional[EpochNumberParam]]:
        if "from" not in transaction and self.default_account:
            transaction = assoc(transaction, "from", self.default_account)

        if block_identifier is None:
            params = (transaction, self._default_block)
        else:
            params = (transaction, block_identifier)

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
    
    _get_balance: ConfluxMethod[Callable[[AddressParam, Optional[EpochNumberParam]], Drip]] = ConfluxMethod(
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
    
    _transaction_receipt: ConfluxMethod[Callable[[_Hash32], TxReceipt]] = ConfluxMethod(
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
    
    
    _get_code: ConfluxMethod[Callable[[AddressParam, Optional[EpochNumberParam]], HexBytes]] = ConfluxMethod(
        RPC.cfx_getCode
    )
    
    _get_storage_at: ConfluxMethod[Callable[[AddressParam, int, Optional[EpochNumberParam]], Union[HexBytes, None]]] = ConfluxMethod(
        RPC.cfx_getStorageAt
    )
    
    _get_storage_root: ConfluxMethod[Callable[[AddressParam, Optional[EpochNumberParam]], Union[StorageRoot, None]]] = ConfluxMethod(
        RPC.cfx_getStorageRoot
    )
    
    _get_collateral_for_storage: ConfluxMethod[Callable[[AddressParam, Optional[EpochNumberParam]], Storage]] = ConfluxMethod(
        RPC.cfx_getCollateralForStorage
    )
    
    _get_admin: ConfluxMethod[Callable[[AddressParam, Optional[EpochNumberParam]], Union[Base32Address, None]]] = ConfluxMethod(
        RPC.cfx_getAdmin
    )
    
    _get_sponsor_info: ConfluxMethod[Callable[[AddressParam, Optional[EpochNumberParam]], SponsorInfo]] = ConfluxMethod(
        RPC.cfx_getSponsorInfo
    )
    
    _get_account: ConfluxMethod[Callable[[AddressParam, Optional[EpochNumberParam]], AccountInfo]] = ConfluxMethod(
        RPC.cfx_getAccount
    )
    
    _get_deposit_list: ConfluxMethod[Callable[[AddressParam, Optional[EpochNumberParam]], Sequence[DepositInfo]]] = ConfluxMethod(
        RPC.cfx_getDepositList
    )
    
    _get_vote_list: ConfluxMethod[Callable[[AddressParam, Optional[EpochNumberParam]], Sequence[VoteInfo]]] = ConfluxMethod(
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
    _get_collateral_info: ConfluxMethod[Callable[[Optional[EpochNumberParam]], CollateralInfo]] = ConfluxMethod(RPC.cfx_getCollateralInfo)

    @overload  
    def contract(
        self, address: Union[Base32Address, str], *, name: Optional[str]=None, with_deployment_info: Optional[bool]=None, **kwargs: Any
    ) -> ConfluxContract:
        ...

    @overload
    def contract(
        self, address: None=None, *, name: None=None, with_deployment_info: Optional[bool]=None, **kwargs: Any
    ) -> Type[ConfluxContract]:
        ...
    
    @overload  
    def contract(
        self, address: None=None, *, name: str=..., with_deployment_info: None=None, **kwargs: Any  
    ) -> Union[Type[ConfluxContract], ConfluxContract]:
        ...
    
    @overload  
    def contract(
        self, address: None=None, *, name: str=..., with_deployment_info: Literal[False]=..., **kwargs: Any 
    ) -> Type[ConfluxContract]:
        ...

    @overload  
    def contract(
        self, address: None=None, *, name: str=..., with_deployment_info: Literal[True]=..., **kwargs: Any
    ) -> ConfluxContract:
        ...

    def contract(
        self,
        address: Optional[Union[Base32Address, str]] = None,
        *,
        name: Optional[str] = None,
        with_deployment_info: Optional[bool] = None,
        **kwargs: Any,
    ) -> Union[Type[ConfluxContract], ConfluxContract]:
        """
        Produce a contract factory (address is not specified) or a contract(address is not specified).
        Address is specified by:

            1. explicitly using address param
            2. embedded contract deployment info if 
                (1) "name" parameter specified and corresponding contract has deployment info 
                (2) with_deployment_info is not False

        >>> from conflux_web3.dev import get_mainnet_web3
        >>> w3 = get_mainnet_web3()
        >>> from conflux_web3.contract import get_contract_metadata
        >>> abi = get_contract_metadata("ERC20")["abi"]
        >>> bytecode = get_contract_metadata("ERC20")["bytecode"]
        >>> erc20_factory = w3.cfx.contract(abi=abi, bytecode=bytecode)

        >>> c1 = w3.cfx.contract(name="AdminControl")
        >>> assert c1.address # address is added by default
        >>> c2 = w3.cfx.contract(name="AdminControl", with_deployment_info=False)
        >>> assert not c2.address # address is not added by explicitly specified

        Parameters
        ----------
        address : Optional[Union[Base32Address, str]], optional
            the address of the contract, by default None
        name : Optional[str], optional
            the name of the contract, which is used to specify abi, bytecode, or deployed contract address, by default None
        with_deployment_info : Optional[bool], optional
            whether address will be specified if name parameter is provided, 
            if True, the address will always be specified if name argument is provided
            if False, the address will never be specified if name argument is provided
            if None, the address will be specified depending on if corresponding address exists
            by default None
        **kwargs: Dict[str, Any]
            used to specify abi and bytecode argument
        Returns
        -------
        Union[Type[ConfluxContract], ConfluxContract]
            returns a contract factory or contract
        """        
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
    account: Account
    _default_contract_factory: Type[ConfluxContract] = ConfluxContract
    
    def __init__(self, w3: "Web3") -> None:
        super().__init__(w3)
        self.account = Account()
        self.account.set_w3(w3)
        self._disable_eth_methods(disabled_method_list)
    
    # lazy initialize self.address
    @cached_property
    def address(self) -> Type[Base32Address]:
        return get_base32_address_factory(self.chain_id)
        
    def _disable_eth_methods(self, disabled_method_list: Sequence[str]):
        for api in disabled_method_list:
            always_returns_zero: Callable[..., Literal[0]] = lambda *args, **kwargs: 0
            self.__setattr__(
                api,
                use_instead(origin=api)(
                    always_returns_zero
                ),
            )
            
    @property
    @use_instead
    def syncing(self):
        """
        Unsupported API
        """
        pass
    
    @property
    @use_instead
    def coinbase(self):
        """
        # WARNING: Unsupported API
        """
        pass

    
    @property
    @use_instead
    def mining(self):
        """
        # WARNING: Unsupported API
        """
        pass
    
    @property
    @use_instead
    def hashrate(self):
        """
        # WARNING: Unsupported API
        """
        pass
    
    @property
    @use_instead(origin="web3.eth.block_number", substitute="web3.cfx.epoch_number")
    def block_number(self):
        """
        # WARNING: Unsupported API, use `web3.cfx.epoch_number` instead
        """
        pass
    
    @property
    @use_instead
    def max_priority_fee(self):
        """
        # WARNING: Unsupported API
        """
        pass
    
    @property
    @use_instead
    def get_work(self):
        """
        # WARNING: Unsupported API
        """
        pass
    
    def get_status(self) -> NodeStatus:
        """
        get the blockchain status from the provider
        
        >>> w3.cfx.get_status()
        AttributeDict({'bestHash': HexBytes('0xb91109cc301209921b33533f8ae228615016b9104e8229ddaad55b370fe586d3'),
            'chainId': 1,
            'ethereumSpaceChainId': 71,
            'networkId': 1,
            'epochNumber': 97105091,
            'blockNumber': 124293823,
            'pendingTxNumber': 69,
            'latestCheckpoint': 97000000,
            'latestConfirmed': 97105034,
            'latestState': 97105087,
            'latestFinalized': 97104660})
        >>> w3.cfx.get_status().chainId # support but not recommended because of missing type hints
        1
        >>> w3.cfx.get_status()['chainId'] # recommended
        1

        Returns
        -------
        NodeStatus
            a dict representing node status
        """        
        return self._get_status()
    
    @property
    def gas_price(self) -> Drip:
        """
        Get the current gas price
        
        >>> w3.cfx.gas_price
        1000000000 Drip
        >>> w3.cfx.gas_price.value
        1000000000
        >>> w3.cfx.gas_price.to("GDrip")
        1 GDrip

        Returns
        -------
        Drip
            gas price wrapped by Drip, which can be used as transaction value or gas price
        """        
        return self._gas_price()
    
    @property
    def accounts(self) -> Tuple[Base32Address]:
        """
        Returns the accounts controlled by the provider 
        ## this method is not supported by public rpcs

        Returns
        -------
        Tuple[Base32Address]
            a Tuple containing the address of the accounts
        """
        return self._accounts()
    
    @property
    def epoch_number(self) -> EpochNumber:
        """
        Returns latest_mined epoch number

        Returns
        -------
        EpochNumber
            latest mined epoch number
        """
        return self._epoch_number(None)
    
    def epoch_number_by_tag(self, epoch_tag: EpochLiteral) -> EpochNumber:
        """
        Returns the epoch numebr with the provided epoch tag

        Parameters
        ----------
        epoch_tag : EpochLiteral
            String "latest_mined", "latest_state", "latest_confirmed", "latest_checkpoint" or "earliest"

        Returns
        -------
        EpochNumber
            the epoch number corrensponding to the epoch tag
        """        
        return self._epoch_number(epoch_tag)
    
    @cached_property
    def chain_id(self) -> int:
        """
        Get the chain id of the current network.
        This property is cached and won't be changed unless it is deleted

        Returns
        -------
        int
            chain id of the blockchain, 1 for conflux testnet and 1029 for conflux mainnet
        """
        return self._get_status()["chainId"]

    @property
    def client_version(self):
        return self._clientVersion()
    
    # def is_connected(self):
    #     return 
    
    def get_balance(self,
                    address: Union[Base32Address, str], 
                    block_identifier: Optional[EpochNumberParam] = None) -> Drip:
        """
        Returns the balance of the given account, identified by its address.

        >>> balance = w3.cfx.get_balance("cfx:type.user:aarc9abycue0hhzgyrr53m6cxedgccrmmyybjgh4xg")
        >>> balance
        "1000000000000000000 Drip"
        >>> balance.value
        1000000000000000000
        >>> balance.to("CFX")
        "1 CFX"

        Parameters
        ----------
        address : Union[Base32Address, str]
            the address of the account 
        block_identifier : Optional[EpochNumberParam], optional
            integer epoch number, or the string "latest_state", "latest_confirmed", "latest_checkpoint" or "earliest", by default None

        Returns
        -------
        Drip
            balance wrapped by Drip
        """        
        return self._get_balance(address, block_identifier)
    
    def get_staking_balance(self,
                    address: Union[Base32Address, str], 
                    block_identifier: Optional[EpochNumberParam] = None) -> Drip:
        """
        Returns the staking balance of the given account, identified by its address.

        Parameters
        ----------
        address : Union[Base32Address, str]
            the address of the account 
        block_identifier : Optional[EpochNumberParam], optional
            integer epoch number, or the string "latest_state", "latest_confirmed", "latest_checkpoint" or "earliest", by default None

        Returns
        -------
        Drip
            balance wrapped by Drip
        """        
        return self._get_staking_balance(address, block_identifier)
    
    
    def call(self, 
             transaction: TxParam, 
             block_identifier: Optional[EpochNumberParam]=None, 
             **kwargs: Dict[str, Any]) -> Any:
        """
        Virtually calls a contract, returns the output data. The transaction will not be added to the blockchain.

        Parameters
        ----------
        transaction : TxParam
        block_identifier : Optional[EpochNumberParam], optional
            integer epoch number, or the string "latest_state", "latest_confirmed", "latest_checkpoint" or "earliest", by default None

        Returns
        -------
        Any
        """        
        return self._call(transaction, block_identifier)
    
    def get_next_nonce(self, address: Union[Base32Address, str], block_identifier: Optional[EpochNumberParam] = None) -> int:
        """
        Returns the next nonce that should be used by the given account when sending a transaction.

        Parameters
        ----------
        address : Union[Base32Address, str]
            the address of the account
        block_identifier : Optional[EpochNumberParam], optional
            integer epoch number, or the string "latest_state", "latest_confirmed", "latest_checkpoint" or "earliest", by default None

        Returns
        -------
        int
        """        
        return self._get_next_nonce(address, block_identifier)

    def get_transaction_count(self, address: Union[Base32Address, str], block_identifier: Optional[EpochNumberParam] = None) -> int:
        """
        Compatibility API for conflux. Equivalent to `get_next_nonce`
        """        
        return self.get_next_nonce(address, block_identifier)

    def estimate_gas_and_collateral(self, transaction: TxParam, block_identifier: Optional[EpochNumberParam]=None) -> EstimateResult:
        """
        Virtually executes a transaction, returns an estimate for the size of storage collateralized and the gas used by the transaction. The transaction will not be added to the blockchain.
        For most cases, you don't need to invoke this api to fill the transaction fields unless you need to manually sign the transactions.

        >>> w3.cfx.estimate_gas_and_collateral({"to": "cfx:type.contract:acc7uawf5ubtnmezvhu9dhc6sghea0403y2dgpyfjp"})
        >>> {"gasLimit": 21000, "gasUsed": 21000, "storageCollateralized": 0}

        Parameters
        ----------
        transaction: TxParam
        block_identifier : Optional[EpochNumberParam], optional
            integer epoch number, or the string "latest_state", "latest_confirmed", "latest_checkpoint" or "earliest", by default None

        Returns
        -------
        EstimateResult
        """        
        return self._estimate_gas_and_collateral(transaction, block_identifier)

    def estimate_gas(self, transaction: TxParam, block_identifier: Optional[EpochNumberParam] = None) -> EstimateResult:
        """
        Compatibility API for conflux. Equivalent to `estimate_gas_and_collateral`
        """        
        return self.estimate_gas_and_collateral(transaction, block_identifier)

    def send_raw_transaction(self, raw_transaction: Union[HexStr, bytes]) -> TransactionHash:
        """
        Sends a signed transaction into the network for processing
        
        >>> tx_hash = w3.cfx.send_raw_transaction("0xf86eea8201a28207d0830f4240943838197c0c88d0d5b13b67e1bfdbdc132d4842e389056bc75e2d631000008080a017b8b26f473820475edc49bd153660e56b973b5985bbdb2828fceacb4c91f389a03452f9a69da34ef35acc9c554d7b1d63e9041141674b42c3abb1b57b9f83a2d3")
        >>> tx_hash.executed() # equivalent to w3.cfx.wait_for_transaction_receipt(tx_hash)

        Parameters
        ----------
        raw_transaction : Union[HexStr, bytes]
            a signed transaction as hex string or bytes

        Returns
        -------
        TransactionHash
            the hash of the transaction in bytes and wrapped by TransactionHash object which provides chained operations
        """        
        # TODO: remove pending middleware and changes here
        return cast(TransactionHash, self._send_raw_transaction(raw_transaction))
    
    def send_transaction(self, transaction: TxParam) -> TransactionHash:
        """
        Send a transaction by using transaction params. 
        ## The node MUST support cfx_sendTransaction rpc (which is typically not supported by public rpc services)
        ## or account is added to w3.wallet
        
        >>> account = w3.account.create()
        >>> w3.wallet.add_account(account)
        >>> w3.cfx.send_transaction({
        ...    "to": w3.address.zero_address(),
        ...    "from": account.address,
        ...    "value": 100,
        ... }).executed()

        Parameters
        ----------
        transaction : TxParam

        Returns
        -------
        TransactionHash
            the hash of the transaction in bytes and wrapped by TransactionHash object which provides chained operations
        """        
        # TODO: remove pending middleware and changes here
        return cast(TransactionHash, self._send_transaction(transaction))
    
    def get_transaction_receipt(self, transaction_hash: _Hash32) -> TxReceipt:
        """
        Returns a transaction receipt, identified by the corresponding transaction hash.
        
        >>> w3.cfx.get_transaction_receipt("0x5ffa11a44c6db42cc30967d4de5949b17ee319c4aba72f3380c60136993a8980")
        AttributeDict({'transactionHash': HexBytes('0x5ffa11a44c6db42cc30967d4de5949b17ee319c4aba72f3380c60136993a8980'),
            'index': 227,
            'blockHash': HexBytes('0xceda961d541c78fa2c99907620bb2b13707f72b004b7c70362a5642177e6aae2'),
            'epochNumber': 97108737,
            'from': 'cfxtest:aaksxj04phv0hp02jh3cbym9vghwkzap867jagb043',
            'to': 'cfxtest:aaksxj04phv0hp02jh3cbym9vghwkzap867jagb043',
            'gasUsed': 21000,
            'gasFee': 21000000000000 Drip,
            'contractCreated': None,
            'logs': [],
            'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
            'stateRoot': HexBytes('0x89dd70006e4714eb81a210a20badf4c37adc7fcbe992b8458460876fcac38ea3'),
            'outcomeStatus': 0,
            'txExecErrorMsg': None,
            'gasCoveredBySponsor': False,
            'storageCoveredBySponsor': False,
            'storageCollateralized': 0,
            'storageReleased': []})

        Parameters
        ----------
        transaction_hash : _Hash32
            the hash of the transaction, could be byte or hex string

        Returns
        -------
        TxReceipt
            the receipt of the transaction
        """        
        return self._get_transaction_receipt(transaction_hash)
    
    def wait_till_transaction_mined(
        self, transaction_hash: _Hash32, timeout: float = 60, poll_latency: float = 0.5
    ) -> TxData:
        """
        Returns information about a transaction when it is mined.
        If TxData is returned, the transaction is found contained in a block, but might not be executed.
        (Transaction will only be executed after 5 epochs)
        
        >>> w3.cfx.wait_till_transaction_mined("0x5ffa11a44c6db42cc30967d4de5949b17ee319c4aba72f3380c60136993a8980")
        AttributeDict({'hash': HexBytes('0x5ffa11a44c6db42cc30967d4de5949b17ee319c4aba72f3380c60136993a8980'),
            'nonce': 8230,
            'blockHash': HexBytes('0xceda961d541c78fa2c99907620bb2b13707f72b004b7c70362a5642177e6aae2'),
            'transactionIndex': 227,
            'from': 'cfxtest:aaksxj04phv0hp02jh3cbym9vghwkzap867jagb043',
            'to': 'cfxtest:aaksxj04phv0hp02jh3cbym9vghwkzap867jagb043',
            'value': 0 Drip,
            'gasPrice': 1000000000 Drip,
            'gas': 21000,
            'contractCreated': None,
            'data': HexBytes('0x'),
            'storageLimit': 0,
            'epochHeight': 97108719,
            'chainId': 1,
            'status': 0,
            'v': 1,
            'r': HexBytes('0x1d16cb28acf3973df4f4cc29ffffdba5d36ca1e38f1904f64780fa505691c1b7'),
            's': HexBytes('0x1549267bc4f60af38d23112b47a54dc36481e77eb44dd5ee2c3277810c1c6297')})


        Parameters
        ----------
        transaction_hash : _Hash32
            the hash of the transaction, could be byte or hex string
        timeout : float, optional
            maximum wait time before timeout in seconds, by default 60
        poll_latency : float, optional
            time interval to query transaction status in seconds, by default 0.5

        Returns
        -------
        TxData
            the transaction data as a dict

        Raises
        ------
        TimeExhausted
            if timeout
        """        
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
        """
        Alias for `wait_till_transaction_executed`
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
        """
        Returns transaction receipt after it is executed.
        If TxReceipt is returned, the transaction is found executed successfully
        
        >>> w3.cfx.wait_till_transaction_executed("0x5ffa11a44c6db42cc30967d4de5949b17ee319c4aba72f3380c60136993a8980")
        AttributeDict({'transactionHash': HexBytes('0x5ffa11a44c6db42cc30967d4de5949b17ee319c4aba72f3380c60136993a8980'),
            'index': 227,
            'blockHash': HexBytes('0xceda961d541c78fa2c99907620bb2b13707f72b004b7c70362a5642177e6aae2'),
            'epochNumber': 97108737,
            'from': 'cfxtest:aaksxj04phv0hp02jh3cbym9vghwkzap867jagb043',
            'to': 'cfxtest:aaksxj04phv0hp02jh3cbym9vghwkzap867jagb043',
            'gasUsed': 21000,
            'gasFee': 21000000000000 Drip,
            'contractCreated': None,
            'logs': [],
            'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
            'stateRoot': HexBytes('0x89dd70006e4714eb81a210a20badf4c37adc7fcbe992b8458460876fcac38ea3'),
            'outcomeStatus': 0,
            'txExecErrorMsg': None,
            'gasCoveredBySponsor': False,
            'storageCoveredBySponsor': False,
            'storageCollateralized': 0,
            'storageReleased': []})

        Parameters
        ----------
        transaction_hash : _Hash32
            the hash of the transaction, could be byte or hex string
        timeout : float, optional
            maximum wait time before timeout in seconds, by default 300
        poll_latency : float, optional
            time interval to query transaction status in seconds, by default 0.5

        Returns
        -------
        TxReceipt
            transaction receipt as a dict

        Raises
        ------
        TimeExhausted
            if timeout
        RuntimeError
            if transaction is not executed successfully
        """  
        return self.wait_for_transaction_receipt(transaction_hash, timeout, poll_latency)
        
    
    def wait_till_transaction_confirmed(
        self, transaction_hash: _Hash32, timeout: float = 600, poll_latency: float = 0.5
    ) -> TxReceipt:
        """
        Returns transaction receipt after a transaction is confirmed.
        If TxReceipt is returned, the chances that the transaction execution result to be reverted is tiny.
        But there are still chances that the transaction might be reverted.
        ## Developers should use `wait_till_transaction_finalized` if the transaction is REALLY IMPORTANT.
        
        >>> w3.cfx.get_transaction_receipt("0x5ffa11a44c6db42cc30967d4de5949b17ee319c4aba72f3380c60136993a8980")
        AttributeDict({'transactionHash': HexBytes('0x5ffa11a44c6db42cc30967d4de5949b17ee319c4aba72f3380c60136993a8980'),
            'index': 227,
            'blockHash': HexBytes('0xceda961d541c78fa2c99907620bb2b13707f72b004b7c70362a5642177e6aae2'),
            'epochNumber': 97108737,
            'from': 'cfxtest:aaksxj04phv0hp02jh3cbym9vghwkzap867jagb043',
            'to': 'cfxtest:aaksxj04phv0hp02jh3cbym9vghwkzap867jagb043',
            'gasUsed': 21000,
            'gasFee': 21000000000000 Drip,
            'contractCreated': None,
            'logs': [],
            'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
            'stateRoot': HexBytes('0x89dd70006e4714eb81a210a20badf4c37adc7fcbe992b8458460876fcac38ea3'),
            'outcomeStatus': 0,
            'txExecErrorMsg': None,
            'gasCoveredBySponsor': False,
            'storageCoveredBySponsor': False,
            'storageCollateralized': 0,
            'storageReleased': []})

        Parameters
        ----------
        transaction_hash : _Hash32
            the hash of the transaction, could be byte or hex string
        timeout : float, optional
            maximum wait time before timeout in seconds, by default 600
        poll_latency : float, optional
            time interval to query transaction status in seconds, by default 0.5

        Returns
        -------
        TxReceipt
            transaction receipt as a dict

        Raises
        ------
        TimeExhausted
            if timeout
        RuntimeError
            if transaction is not executed successfully
        """  
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
        """
        Returns transaction receipt after a transaction is finalized by PoS chain.
        It will take 5 ~ 10 minutes to finalize a transaction but the finalized transaction won't be reverted.
        It is recommended for developers to use this api to confirm important transactions.

        Parameters
        ----------
        transaction_hash : _Hash32
            the hash of the transaction, could be byte or hex string
        timeout : float, optional
            maximum wait time before timeout in seconds, by default 1200
        poll_latency : float, optional
            time interval to query transaction status in seconds, by default 0.5

        Returns
        -------
        TxReceipt
            transaction receipt as a dict

        Raises
        ------
        TimeExhausted
            If timeout
        """        
        warnings.warn("5 ~ 10 minutes are required to finalize a transaction", UserWarning)
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
        """
        Returns information about a transaction, identified by its hash.
        ## Note: the transaction is not mined if `blockHash` field is None
        
        >>> w3.cfx.get_transaction_by_hash('0x5ffa11a44c6db42cc30967d4de5949b17ee319c4aba72f3380c60136993a8980')
        AttributeDict({'hash': HexBytes('0x5ffa11a44c6db42cc30967d4de5949b17ee319c4aba72f3380c60136993a8980'),
            'nonce': 8230,
            'blockHash': HexBytes('0xceda961d541c78fa2c99907620bb2b13707f72b004b7c70362a5642177e6aae2'),
            'transactionIndex': 227,
            'from': 'cfxtest:aaksxj04phv0hp02jh3cbym9vghwkzap867jagb043',
            'to': 'cfxtest:aaksxj04phv0hp02jh3cbym9vghwkzap867jagb043',
            'value': 0 Drip,
            'gasPrice': 1000000000 Drip,
            'gas': 21000,
            'contractCreated': None,
            'data': HexBytes('0x'),
            'storageLimit': 0,
            'epochHeight': 97108719,
            'chainId': 1,
            'status': 0,
            'v': 1,
            'r': HexBytes('0x1d16cb28acf3973df4f4cc29ffffdba5d36ca1e38f1904f64780fa505691c1b7'),
            's': HexBytes('0x1549267bc4f60af38d23112b47a54dc36481e77eb44dd5ee2c3277810c1c6297')})


        Parameters
        ----------
        transaction_hash : _Hash32
            the hash of the transaction, could be byte or hex string

        Returns
        -------
        TxData
            transaction data as a dict
        """        
        return self._get_transaction_by_hash(transaction_hash)
    
    # same as web3.py
    def get_transaction(self, transaction_hash: _Hash32) -> TxData:
        """Alias for `get_transaction_by_hash`
        """
        return self.get_transaction_by_hash(transaction_hash)
    
    def get_block_by_hash(
        self, block_hash: _Hash32, full_transactions: bool=False
    ) -> Union[BlockData, None]:
        """
        Returns information about a block, identified by its hash.

        >>> w3.cfx.get_block_by_hash("0x4752f93f61b43e3b09bcbcd36871d4894ac64254df367fa9d7a6253cfb618ece")
        AttributeDict({'hash': HexBytes('0x4752f93f61b43e3b09bcbcd36871d4894ac64254df367fa9d7a6253cfb618ece'),
            'parentHash': HexBytes('0x06a695ab273255341f24f955ce696d45007df4df66f0c61b1818965926c2e808'),
            'height': 97111729,
            'miner': 'cfxtest:aanpu16mtgc7dke5xhuktyfyef8f00pz8a2z5mc14g',
            'deferredStateRoot': HexBytes('0xeaf792fff684ce3f04c84614442ab38e8bb4622bacba1c01e857449ef97425f2'),
            'deferredReceiptsRoot': HexBytes('0x09f8709ea9f344a810811a373b30861568f5686e649d6177fd92ea2db7477508'),
            'deferredLogsBloomHash': HexBytes('0xd397b3b043d87fcd6fad1291ff0bfd16401c274896d8c63a923727f077b8e0b5'),
            'blame': 0,
            'transactionsRoot': HexBytes('0x6058a7cf739d94882638cada6e15a4f3b53b757c7195c5cafd04c2061f6de00d'),
            'epochNumber': 97111729,
            'blockNumber': 124302546,
            'gasLimit': 30000000,
            'gasUsed': 75291,
            'timestamp': 1666755747,
            'difficulty': 57822922,
            'powQuality': HexBytes('0x04ebbe82'),
            'refereeHashes': [],
            'adaptive': False,
            'nonce': HexBytes('0x14b30ccfa7cf95b2'),
            'size': 311,
            'custom': [HexBytes('0x02')],
            'posReference': HexBytes('0x2bac96d8e4205badeab4138d1f7b671a436a68ab50c54e7b154243cbf0c9205b'),
            'transactions': [HexBytes('0x70d17ef32c0544075078cb1ca777dab3728d443f00826cf3d05b9c01b76b5f5c')]})
                    
        Parameters
        ----------
        block_hash : _Hash32
            hash of a block
        full_transactions : bool, optional
            if true, it returns the full transaction objects. If false, only the hashes of the transactions are returned, by default False

        Returns
        -------
        Union[BlockData, None]
            the block data as a dict, or None if no block was found
        """        
        return self._get_block_by_hash(block_hash, full_transactions)
    
    def get_block_by_epoch_number(
        self, epoch_number_param: EpochNumberParam, full_transactions: bool=False
    ) -> BlockData:
        """
        Returns information about a pivot block, identified by its epoch number.

        >>> w3.cfx.get_block_by_epoch_number(97111729)
        AttributeDict({'hash': HexBytes('0x4752f93f61b43e3b09bcbcd36871d4894ac64254df367fa9d7a6253cfb618ece'),
            'parentHash': HexBytes('0x06a695ab273255341f24f955ce696d45007df4df66f0c61b1818965926c2e808'),
            'height': 97111729,
            'miner': 'cfxtest:aanpu16mtgc7dke5xhuktyfyef8f00pz8a2z5mc14g',
            'deferredStateRoot': HexBytes('0xeaf792fff684ce3f04c84614442ab38e8bb4622bacba1c01e857449ef97425f2'),
            'deferredReceiptsRoot': HexBytes('0x09f8709ea9f344a810811a373b30861568f5686e649d6177fd92ea2db7477508'),
            'deferredLogsBloomHash': HexBytes('0xd397b3b043d87fcd6fad1291ff0bfd16401c274896d8c63a923727f077b8e0b5'),
            'blame': 0,
            'transactionsRoot': HexBytes('0x6058a7cf739d94882638cada6e15a4f3b53b757c7195c5cafd04c2061f6de00d'),
            'epochNumber': 97111729,
            'blockNumber': 124302546,
            'gasLimit': 30000000,
            'gasUsed': 75291,
            'timestamp': 1666755747,
            'difficulty': 57822922,
            'powQuality': HexBytes('0x04ebbe82'),
            'refereeHashes': [],
            'adaptive': False,
            'nonce': HexBytes('0x14b30ccfa7cf95b2'),
            'size': 311,
            'custom': [HexBytes('0x02')],
            'posReference': HexBytes('0x2bac96d8e4205badeab4138d1f7b671a436a68ab50c54e7b154243cbf0c9205b'),
            'transactions': [HexBytes('0x70d17ef32c0544075078cb1ca777dab3728d443f00826cf3d05b9c01b76b5f5c')]})

        Parameters
        ----------
        epoch_number_param : EpochNumberParam
            the epoch number, or the string "latest_mined", "latest_state", "latest_confirmed", "latest_checkpoint" or "earliest"
        full_transactions : bool, optional
            if true, it returns the full transaction objects. If false, only the hashes of the transactions are returned, by default False

        Returns
        -------
        BlockData
            the block data as a dict
        """        
        return self._get_block_by_epoch_number(epoch_number_param, full_transactions)
    
    def get_block_by_block_number(
        self, block_number: int, full_transactions: bool=False
    ) -> BlockData:
        """
        Returns information about a block, identified by its block number.

        >>> w3.cfx.get_block_by_block_number(124302546)
        AttributeDict({'hash': HexBytes('0x4752f93f61b43e3b09bcbcd36871d4894ac64254df367fa9d7a6253cfb618ece'),
            'parentHash': HexBytes('0x06a695ab273255341f24f955ce696d45007df4df66f0c61b1818965926c2e808'),
            'height': 97111729,
            'miner': 'cfxtest:aanpu16mtgc7dke5xhuktyfyef8f00pz8a2z5mc14g',
            'deferredStateRoot': HexBytes('0xeaf792fff684ce3f04c84614442ab38e8bb4622bacba1c01e857449ef97425f2'),
            'deferredReceiptsRoot': HexBytes('0x09f8709ea9f344a810811a373b30861568f5686e649d6177fd92ea2db7477508'),
            'deferredLogsBloomHash': HexBytes('0xd397b3b043d87fcd6fad1291ff0bfd16401c274896d8c63a923727f077b8e0b5'),
            'blame': 0,
            'transactionsRoot': HexBytes('0x6058a7cf739d94882638cada6e15a4f3b53b757c7195c5cafd04c2061f6de00d'),
            'epochNumber': 97111729,
            'blockNumber': 124302546,
            'gasLimit': 30000000,
            'gasUsed': 75291,
            'timestamp': 1666755747,
            'difficulty': 57822922,
            'powQuality': HexBytes('0x04ebbe82'),
            'refereeHashes': [],
            'adaptive': False,
            'nonce': HexBytes('0x14b30ccfa7cf95b2'),
            'size': 311,
            'custom': [HexBytes('0x02')],
            'posReference': HexBytes('0x2bac96d8e4205badeab4138d1f7b671a436a68ab50c54e7b154243cbf0c9205b'),
            'transactions': [HexBytes('0x70d17ef32c0544075078cb1ca777dab3728d443f00826cf3d05b9c01b76b5f5c')]})

        Parameters
        ----------
        epoch_number_param : EpochNumberParam
            the epoch number, or the string "latest_mined", "latest_state", "latest_confirmed", "latest_checkpoint" or "earliest"
        full_transactions : bool, optional
            if true, it returns the full transaction objects. If false, only the hashes of the transactions are returned, by default False

        Returns
        -------
        BlockData
            the block data as a dict
        """  
        return self._get_block_by_block_number(block_number, full_transactions)
    
    def get_best_block_hash(self) -> HexBytes:
        """
        Returns the best block hash, which is the block hash of the latest pivot block

        Returns
        -------
        HexBytes
            best block hash in bytes
        """        
        return self._get_best_block_hash()
    
    def get_blocks_by_epoch(self, epoch_number_param: EpochNumberParam) -> Sequence[HexBytes]:
        """
        Returns the block hashes in the specified epoch.

        Parameters
        ----------
        epoch_number_param : EpochNumberParam
            the epoch number, or the string "latest_mined", "latest_state", "latest_confirmed", "latest_checkpoint" or "earliest"

        Returns
        -------
        Sequence[HexBytes]
            a list of block hash in bytes
        """        
        return self._get_blocks_by_epoch(epoch_number_param)
    
    def get_skipped_blocks_by_epoch(self, epoch_number_param: EpochNumberParam) -> Sequence[HexBytes]:
        """
        Returns the list of non-executed blocks in an epoch. By default, Conflux only executes the last 200 blocks in each epoch (note that under normal circumstances, epochs should be much smaller).

        Parameters
        ----------
        epoch_number_param : EpochNumberParam
            the epoch number, or the string "latest_mined", "latest_state", "latest_confirmed", "latest_checkpoint" or "earliest"

        Returns
        -------
        Sequence[HexBytes]
            a list of block hash in bytes
        """        
        return self._get_skipped_blocks_by_epoch(epoch_number_param)

    def get_block_by_hash_with_pivot_assumptions(self, block_hash: _Hash32, assumed_pivot_hash: _Hash32, epoch_number: int) -> BlockData:
        """
        Returns the requested block if the provided pivot hash is correct, returns an error otherwise.

        Parameters
        ----------
        block_hash : _Hash32
            block hash
        assumed_pivot_hash : _Hash32
            assumed pivot hash
        epoch_number : int
            integer epoch number

        Returns
        -------
        BlockData
            returns block data if pivot hash is correct
        """        
        return self._get_block_by_hash_with_pivot_assumptions(block_hash, assumed_pivot_hash, epoch_number)
    
    def get_confirmation_risk_by_hash(self, block_hash: _Hash32) -> float:
        """
        Returns the confirmation risk of a given block, identified by its hash

        Parameters
        ----------
        block_hash : _Hash32
            block hash

        Returns
        -------
        float
            the confirmation risk in float
        """        
        return self._get_confirmation_risk_by_hash(block_hash)
    
    def get_block(self, block_identifier: Union[_Hash32, EpochNumberParam], full_transactions: bool = False) -> BlockData:
        """
        a simple wrapper combining `get_block_by_hash` and `get_block_by_epoch_number`
        # note: DON'T USE *BLOCK NUMBER* as the parameter. A number will be considered as epoch number
        
        >>> block_data = w3.cfx.get_block(97112003)
        >>> block_data_ = w3.cfx.get_block("0x1aa5c0d8d6778bd72ac842a52fd26042458b4f70a4d969dfa0d80f81f5eac790")
        >>> assert block_data == block_data_

        Parameters
        ----------
        block_identifier : Union[_Hash32, EpochNumberParam]
            block hash or epoch number parameter(e.g. string "latest_state" or epoch number)
        full_transactions : bool, optional
            whether the return block data contains full transaction info or just transaction hash, by default False

        Returns
        -------
        BlockData
        """
        # TODO: more fine-grained munger
        if block_identifier == "latest":
            block_identifier = "latest_state"  
        elif isinstance(block_identifier, bytes) or is_hash32_str(block_identifier):
            return self.get_block_by_hash(block_identifier, full_transactions) # type: ignore
        return self.get_block_by_epoch_number(block_identifier, full_transactions) # type: ignore
    
    def get_code(
        self, address: Union[Base32Address, str], block_identifier: Optional[EpochNumberParam] = None
    ) -> HexBytes:
        """
        Returns the code of the specified contract. If contract does not exist will return :const:`0x0`

        Parameters
        ----------
        address : Union[Base32Address, str]
            address of the contract
        block_identifier : Optional[EpochNumberParam], optional
            integer epoch number, or the string "latest_state", "latest_confirmed", 
            "latest_checkpoint" or "earliest", by default None

        Returns
        -------
        HexBytes
            byte code of the contract, or :const:`0x` if the account has no code
        """        
        return self._get_code(address, block_identifier)
    
    def get_storage_at(
        self, address: Union[Base32Address, str], storage_position: int, block_identifier: Optional[EpochNumberParam] = None
    ) -> Union[HexBytes, None]:
        """
        Returns storage entries from a given contract.

        Parameters
        ----------
        address : Union[Base32Address, str]
            address of the contract
        storage_position : int
            a storage position (refer to https://solidity.readthedocs.io/en/v0.7.1/internals/layout_in_storage.html for more info)
        block_identifier : Optional[EpochNumberParam], optional
            integer epoch number, or the string "latest_state", "latest_confirmed", "latest_checkpoint" or "earliest", by default None

        Returns
        -------
        Union[HexBytes, None]
            32 Bytes - the contents of the storage position, or :const:`None` if the contract does not exist
        """        
        return self._get_storage_at(address, storage_position, block_identifier)
    
    def get_storage_root(
        self, address: Union[Base32Address, str], block_identifier: Optional[EpochNumberParam] = None
    ) -> Union[StorageRoot, None]:
        return self._get_storage_root(address, block_identifier)
    
    def get_collateral_for_storage(
        self, address: Union[Base32Address, str], block_identifier: Optional[EpochNumberParam] = None
    ) -> Storage:
        return self._get_collateral_for_storage(address, block_identifier)
    
    def get_sponsor_info(
        self, address: Union[Base32Address, str], block_identifier: Optional[EpochNumberParam] = None
    ) -> SponsorInfo:
        return self._get_sponsor_info(address, block_identifier)
    
    def get_account(
        self, address: Union[Base32Address, str], block_identifier: Optional[EpochNumberParam] = None
    ) -> AccountInfo:
        return self._get_account(address, block_identifier)
    
    def get_deposit_list(
        self, address: Union[Base32Address, str], block_identifier: Optional[EpochNumberParam] = None
    ) -> Sequence[DepositInfo]:
        return self._get_deposit_list(address, block_identifier)
    
    def get_vote_list(
        self, address: Union[Base32Address, str], block_identifier: Optional[EpochNumberParam] = None
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
        self, address: Union[Base32Address, str]
    ) -> PendingInfo:
        return self._get_account_pending_info(address)
    
    def get_account_pending_transactions(
        self, address: Union[Base32Address, str], start_nonce: Optional[int]=None, limit: Optional[int]=None
    ) -> PendingTransactionsInfo:
        return self._get_account_pending_transactions(address, start_nonce, limit)
    
    def check_balance_against_transaction(
        self,
        account_address: Union[Base32Address, str],
        contract_address: Union[Base32Address, str], 
        gas_limit: int,
        gas_price: Union[Drip, AbstractDerivedTokenUnit[Drip], int],
        storage_limit: Union[Storage, int],
        block_identifier: Optional[EpochNumberParam] = None
    ) -> TransactionPaymentInfo:
        gas_price = to_int_if_drip_units(gas_price)
        return self._check_balance_against_transaction(
            account_address, contract_address, gas_limit, gas_price, storage_limit, block_identifier
        )
    
    @overload
    def get_logs(self, filter_params: FilterParams) -> List[LogReceipt]:...
    
    @overload
    def get_logs(self, filter_params: None=None, **kwargs: Any) -> List[LogReceipt]:...
    
    def get_logs(self, filter_params: Optional[FilterParams]=None, **kwargs: Any) -> List[LogReceipt]:
        """
        Returns logs matching the filter provided.
        It is accepted to pass filter_params as a dict or by direclty specifying field name (but cannot mix)

        >>> logs = w3.cfx.get_logs({"fromEpoch": 97134060, "toEpoch: 97134160"})
        >>> assert logs == w3.cfx.get_logs(fromEpoch=97134060, toEpoch=97134160})

        Parameters
        ----------
        filter_params : Optional[FilterParams], optional
            visit https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc/#cfx_getlogs for more information

        Returns
        -------
        List[LogReceipt]
            a list of LogReceipt. It is recommended to read https://github.com/Conflux-Chain/python-conflux-sdk/blob/v1/examples/04-interact_with_contracts_and_logs.py to know how to process the returned logs
        """        
        if filter_params is None:
            filter_params = cast(FilterParams, keyfilter(lambda key: key in FilterParams.__annotations__.keys(), kwargs)) # type: ignore
            return self._get_logs(filter_params)
        else:
            if len(kwargs.keys()) != 0:
                raise ValueError("Redundant Param: FilterParams as get_logs first parameter is already provided")
            return self._get_logs(filter_params)

    def get_collateral_info(self, block_identifier: Optional[EpochNumberParam] = None) -> CollateralInfo:
        return self._get_collateral_info(block_identifier)
