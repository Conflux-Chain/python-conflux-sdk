import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Optional,
    Sequence,
    Type,
    Union,
    cast,
)
from hexbytes import HexBytes

from eth_utils.functional import (
    to_tuple,
)
from web3.contract.base_contract import (
    BaseContractEvent,
    BaseContractEvents,
)
from web3.datastructures import (
    AttributeDict,
    MutableAttributeDict,
)
from web3.types import (
    ABI,
)
from web3.logs import (
    DISCARD,
    IGNORE,
    STRICT,
    WARN,
)
from web3._utils.events import (
    EventLogErrorFlags,
)
from web3._utils.filters import (
    construct_event_filter_params
)
from web3.exceptions import (
    InvalidEventABI,
    LogTopicError,
    MismatchedABI,
)

from cfx_address import (
    Base32Address
)
from cfx_utils.decorators import (
    combomethod
)
from conflux_web3.types import (
    AddressParam,
    TxReceipt,
    EventData,
    LogReceipt,
    EpochNumberParam,
)
from conflux_web3._utils.events import (
    cfx_get_event_data,
)
from conflux_web3._utils.decorators import (
    use_instead
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

class ConfluxContractEvent(BaseContractEvent):
    
    w3: "Web3"
    address: Base32Address
    
    @combomethod
    def process_receipt(
        self, txn_receipt: TxReceipt, errors: EventLogErrorFlags = WARN
    ) -> Sequence[EventData]:
        return self._parse_logs(txn_receipt, errors) # type: ignore
    
    @combomethod
    def processReceipt(
        self, txn_receipt: TxReceipt, errors: EventLogErrorFlags = WARN
    ) -> Sequence[EventData]:
        return self.process_receipt(txn_receipt, errors)
    
    @combomethod
    @to_tuple
    def _parse_logs(
        self, txn_receipt: TxReceipt, errors: EventLogErrorFlags
    ) -> Iterable[EventData]:
        try:
            errors.name
        except AttributeError:
            raise AttributeError(
                f"Error flag must be one of: {EventLogErrorFlags.flag_options()}"
            )
        for transaction_log_index in range(len(txn_receipt["logs"])):
        # for log in txn_receipt["logs"]:
            log = txn_receipt["logs"][transaction_log_index]
            try:
                log = cast(LogReceipt, dict(log))
                log["transactionHash"] = txn_receipt["transactionHash"]
                log["blockHash"] = txn_receipt["blockHash"]
                log["epochNumber"] = txn_receipt["epochNumber"]
                log["transactionIndex"] = txn_receipt["index"]
                log["transactionLogIndex"] = transaction_log_index
                abi = self.abi or self._get_event_abi()
                rich_log = cfx_get_event_data(self.w3.codec, abi, log, self.w3.cfx.chain_id)
            except (MismatchedABI, LogTopicError, InvalidEventABI, TypeError) as e:
                if errors == DISCARD:
                    continue
                elif errors == IGNORE:
                    # type ignores b/c rich_log set on 1092 conflicts with mutated types
                    new_log = MutableAttributeDict(log)  # type: ignore
                    new_log["errors"] = e
                    rich_log = AttributeDict(new_log)  # type: ignore
                elif errors == STRICT:
                    raise e
                else:
                    warnings.warn(
                        f"The log with transaction hash: {txn_receipt['transactionHash']!r} "
                        f"encountered the following "
                        f"error during processing: {type(e).__name__}({e}). It has "
                        "been discarded."
                    )
                    continue
            yield rich_log # type: ignore

    @combomethod
    def process_log(self, log: LogReceipt) -> EventData:
        abi = self.abi or self._get_event_abi()
        return cfx_get_event_data(self.w3.codec, abi, log, self.w3.cfx.chain_id)

    @combomethod
    def processLog(self, log: LogReceipt) -> EventData:
        return self.process_log(self.w3.codec, self.abi, log)

    @combomethod
    @use_instead
    def createFilter(*args, **kwargs):
        pass
    
    @combomethod
    @use_instead
    def build_filter(*args, **kwargs):
        pass

    @combomethod
    def get_filter_topics(
        self,
        argument_filters: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Any:
        """
        Web3.py's createFilter interface is used for eth_newFilter RPCEndpoint.
        We disable the createFilter method and use get_filter_topics instead
        """
        if argument_filters is not None and len(kwargs.keys()) != 0:
            raise ValueError("Redundant Param: argument_filters is already provided")

        if argument_filters is None:
            argument_filters = kwargs

        _filters = dict(**argument_filters)

        event_abi = self._get_event_abi()

        BaseContractEvent.check_for_forbidden_api_filter_arguments(event_abi, _filters)

        _, event_filter_params = construct_event_filter_params(
            self._get_event_abi(),
            self.w3.codec,
            argument_filters=_filters,
        )
        return event_filter_params["topics"] # type: ignore
    
    @combomethod
    def get_logs(
        self,
        argument_filters: Optional[Dict[str, Any]] = None,
        fromEpoch: Optional[EpochNumberParam] = None,
        toEpoch: Optional[EpochNumberParam] = None,
        blockHashes: Optional[Sequence[HexBytes]] = None,
        address: Optional[Union[Base32Address, Sequence[Base32Address]]]=None
    ) -> Sequence[EventData]:
        """
        _summary_

        Parameters
        ----------
        argument_filters : Optional[Dict[str, Any]], optional
            _description_, by default None
        fromEpoch : Optional[EpochNumberParam], optional
            _description_, by default None
        toEpoch : Optional[EpochNumberParam], optional
            _description_, by default None
        blockHashes : Optional[Sequence[HexBytes]], optional
            _description_, by default None
        address : Optional[Union[Base32Address, Sequence[Base32Address]]], optional
            _description_, by default None

        Returns
        -------
        Iterable[EventData]
            _description_
        """        
        topics = self.get_filter_topics(argument_filters)
        filter_params = {
            "blockHashes": blockHashes,
            "fromEpoch": fromEpoch,
            "toEpoch": toEpoch,
            "topics": topics,
            "address": address
        }
        logs = self.w3.cfx.get_logs(filter_params)
        return tuple(
            self.process_log(log) for log in logs
        )
        
    @combomethod
    def getLogs(self, *args, **kwargs):
        return self.get_logs(*args, **kwargs)

class ConfluxContractEvents(BaseContractEvents):
    def __init__(
        self, abi: ABI, w3: "Web3", address: Optional[AddressParam] = None
    ) -> None:
        super().__init__(abi, w3, ConfluxContractEvent, address) # type: ignore
        
    def __getitem__(self, event_name: str) -> Type["ConfluxContractEvent"]:
        return cast(Type[ConfluxContractEvent], super().__getitem__(event_name))
    
    def __getattr__(self, event_name: str) -> Type["ConfluxContractEvent"]:
        return cast(Type[ConfluxContractEvent], super().__getattr__(event_name))
