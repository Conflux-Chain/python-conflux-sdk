from typing import (
    Optional,
    cast,
    Any,
)
import itertools

from eth_utils.abi import (
    get_abi_input_names,
)
from eth_abi.codec import (
    ABICodec,
)

from eth_utils.conversions import (
    to_bytes,
)
from eth_utils.toolz import (
    curry, # type: ignore
)

from web3._utils.events import (
    get_event_abi_types_for_decoding,
)
from web3._utils.abi import (
    exclude_indexed_event_inputs,
    get_indexed_event_inputs,
    map_abi_data,
    normalize_event_input_types,
    named_tree
)
from web3.utils.abi import (
    get_event_log_topics,
)
from eth_typing import (
    ABIEvent,
)
from web3.datastructures import (
    AttributeDict
)
from web3.exceptions import (
    InvalidEventABI,
    LogTopicError,
)
from web3._utils.encoding import (
    hexstr_if_str,
)

from cfx_address.utils import (
    normalize_to
)
from conflux_web3.types import (
    EventData,
    LogReceipt,
)

def _log_entry_data_to_bytes(
    log_entry_data: Any,
):
    return hexstr_if_str(to_bytes, log_entry_data)  # type: ignore

def get_cfx_base32_normalizer(chain_id: int): # type: ignore
    return lambda type_str, hex_address: (type_str, normalize_to(hex_address, chain_id, True)) if type_str == "address" else (type_str, hex_address) # type: ignore


@curry # type: ignore
def cfx_get_event_data(
    abi_codec: ABICodec,
    event_abi: ABIEvent,
    log_entry: LogReceipt,
    chain_id: Optional[int]= None
) -> EventData:
    """
    Given an event ABI and a log entry for that event, return the decoded
    event data
    """
    log_topics = get_event_log_topics(event_abi, log_entry["topics"])
    log_topics_bytes = [_log_entry_data_to_bytes(topic) for topic in log_topics]
    log_topics_abi = get_indexed_event_inputs(event_abi)
    log_topic_normalized_inputs = normalize_event_input_types(log_topics_abi)
    log_topic_types = get_event_abi_types_for_decoding(log_topic_normalized_inputs)
    log_topic_names = get_abi_input_names(
        ABIEvent({"name": event_abi["name"], "type": "event", "inputs": log_topics_abi})
    )

    if len(log_topics_bytes) != len(log_topic_types):
        raise LogTopicError(
            f"Expected {len(log_topic_types)} log topics.  Got {len(log_topics_bytes)}"
        )

    log_data = _log_entry_data_to_bytes(log_entry["data"])
    log_data_abi = exclude_indexed_event_inputs(event_abi)
    log_data_normalized_inputs = normalize_event_input_types(log_data_abi)
    log_data_types = get_event_abi_types_for_decoding(log_data_normalized_inputs)
    log_data_names = get_abi_input_names(
        ABIEvent({"name": event_abi["name"], "type": "event", "inputs": log_data_abi})
    )

    # sanity check that there are not name intersections between the topic
    # names and the data argument names.
    duplicate_names = set(log_topic_names).intersection(log_data_names)
    if duplicate_names:
        raise InvalidEventABI(
            "The following argument names are duplicated "
            f"between event inputs: '{', '.join(duplicate_names)}'"
        )

    decoded_log_data = abi_codec.decode(log_data_types, log_data)
    normalized_log_data = map_abi_data(
        [get_cfx_base32_normalizer(chain_id)], log_data_types, decoded_log_data
    )
    named_log_data = named_tree(
        log_data_normalized_inputs,
        normalized_log_data,
    )

    decoded_topic_data = [
        abi_codec.decode([topic_type], topic_data)[0]
        for topic_type, topic_data in zip(log_topic_types, log_topics_bytes)
    ]
    normalized_topic_data = map_abi_data(
        [get_cfx_base32_normalizer(chain_id)], log_topic_types, decoded_topic_data
    )

    event_args = dict(
        itertools.chain(
            zip(log_topic_names, normalized_topic_data),
            named_log_data.items(),
        )
    )

    event_data = {
        "args": event_args,
        "event": event_abi.get("name", None),
        "logIndex": log_entry.get("logIndex", None),
        "transactionIndex": log_entry.get("transactionIndex", None),
        "transactionLogIndex": log_entry.get("transactionLogIndex", None),
        "transactionHash": log_entry.get("transactionHash", None),
        "address": log_entry["address"],
        "blockHash": log_entry.get("blockHash", None),
        "epochNumber": log_entry.get("epochNumber", None)
    }
    if isinstance(log_entry, AttributeDict):
        return cast(EventData, AttributeDict.recursive(event_data))

    return event_data
    

# events.get_event_data = conditional_func(
#     cfx_get_event_data,
#     from_cfx_condition
# )(events.get_event_data)


# modify_to_conditional_func(events.get_event_data, cfx_get_event_data, from_cfx_condition)


