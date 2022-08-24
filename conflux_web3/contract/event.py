import warnings
from typing import (
    TYPE_CHECKING,
    Iterable,
    Optional,
)

from eth_utils.functional import (
    to_tuple
)
from web3.contract import (
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
from web3.exceptions import (
    InvalidEventABI,
    LogTopicError,
    MismatchedABI,
)

from conflux_web3.types import (
    AddressParam,
    TxReceipt,
    EventData,
)
from conflux_web3._utils.events import (
    cfx_get_event_data
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

class ConfluxContractEvent(BaseContractEvent):
    
    w3: "Web3"
    
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

        for log in txn_receipt["logs"]:
            try:
                rich_log = cfx_get_event_data(self.w3.codec, self.abi, log, self.w3.cfx.chain_id)
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
                        f"The log with transaction hash: {log['transactionHash']!r} "
                        f"and logIndex: {log['logIndex']} encountered the following "
                        f"error during processing: {type(e).__name__}({e}). It has "
                        "been discarded."
                    )
                    continue
            yield rich_log # type: ignore
    

class ConfluxContractEvents(BaseContractEvents):
    def __init__(
        self, abi: ABI, w3: "Web3", address: Optional[AddressParam] = None
    ) -> None:
        super().__init__(abi, w3, ConfluxContractEvent, address) # type: ignore
