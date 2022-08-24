from typing import (
    Optional,
    cast
)
import itertools

from eth_abi.codec import (
    ABICodec,
)
from eth_utils.abi import (
    event_abi_to_log_topic,
)
from eth_utils.conversions import (
    to_bytes,
)
from eth_utils.toolz import (
    curry, # type: ignore
)
from web3._utils.normalizers import (
    BASE_RETURN_NORMALIZERS,
)
from web3._utils import events
from web3._utils.events import (
    get_event_abi_types_for_decoding
)
from web3._utils.abi import (
    exclude_indexed_event_inputs,
    get_abi_input_names,
    get_indexed_event_inputs,
    get_normalized_abi_arg_type,
    map_abi_data,
    normalize_event_input_types,
)
from web3.types import (
    ABIEvent,
)
from web3.datastructures import (
    AttributeDict
)
from web3.exceptions import (
    InvalidEventABI,
    LogTopicError,
    MismatchedABI,
)
from web3._utils.encoding import (
    encode_single_packed,
    hexstr_if_str,
)

from cfx_address.utils import normalize_to

from conflux_web3.types import (
    EventData
)
from conflux_web3.types import (
    LogReceipt
)


@curry
def cfx_get_event_data(
    abi_codec: ABICodec, event_abi: ABIEvent, log_entry: LogReceipt, chain_id: Optional[int]= None
) -> EventData:
    """
    Given an event ABI and a log entry for that event, return the decoded
    event data.
    Modified from web3._utils.events.get_event_data
    """
    if event_abi.get("anonymous", None):
        log_topics = log_entry["topics"]
    elif not log_entry["topics"]:
        raise MismatchedABI("Expected non-anonymous event to have 1 or more topics")
    # type ignored b/c event_abi_to_log_topic(event_abi: Dict[str, Any])
    elif event_abi_to_log_topic(event_abi) != log_entry["topics"][0]:  # type: ignore
        raise MismatchedABI("The event signature did not match the provided ABI")
    else:
        log_topics = log_entry["topics"][1:]

    log_topics_abi = get_indexed_event_inputs(event_abi)
    log_topic_normalized_inputs = normalize_event_input_types(log_topics_abi)
    log_topic_types = get_event_abi_types_for_decoding(log_topic_normalized_inputs)
    log_topic_names = get_abi_input_names(ABIEvent({"inputs": log_topics_abi}))

    if len(log_topics) != len(log_topic_types):
        raise LogTopicError(
            f"Expected {len(log_topic_types)} log topics.  Got {len(log_topics)}"
        )

    log_data = hexstr_if_str(to_bytes, log_entry["data"])
    log_data_abi = exclude_indexed_event_inputs(event_abi)
    log_data_normalized_inputs = normalize_event_input_types(log_data_abi)
    log_data_types = get_event_abi_types_for_decoding(log_data_normalized_inputs)
    log_data_names = get_abi_input_names(ABIEvent({"inputs": log_data_abi}))

    # sanity check that there are not name intersections between the topic
    # names and the data argument names.
    duplicate_names = set(log_topic_names).intersection(log_data_names)
    if duplicate_names:
        raise InvalidEventABI(
            "The following argument names are duplicated "
            f"between event inputs: '{', '.join(duplicate_names)}'"
        )

    decoded_log_data = abi_codec.decode_abi(log_data_types, log_data)
    
    return_normalizer = [
        lambda type_str, hex_address: (type_str, normalize_to(hex_address, chain_id, True)) if type_str == "address" \
                                                                                        else (type_str, hex_address)
    ]
    
    normalized_log_data = map_abi_data(
        return_normalizer, log_data_types, decoded_log_data
    )

    decoded_topic_data = [
        abi_codec.decode_single(topic_type, topic_data)
        for topic_type, topic_data in zip(log_topic_types, log_topics)
    ]
    normalized_topic_data = map_abi_data(
        return_normalizer, log_topic_types, decoded_topic_data
    )

    event_args = dict(
        itertools.chain(
            zip(log_topic_names, normalized_topic_data),
            zip(log_data_names, normalized_log_data),
        )
    )

    event_data = {
        "args": event_args,
        "event": event_abi.get("name", None),
        "logIndex": log_entry.get("logIndex", None),
        "transactionIndex": log_entry.get("transactionIndex", None),
        "transactionHash": log_entry.get("transactionHash", None),
        "address": log_entry["address"],
        "blockHash": log_entry.get("blockHash", None),
        "epochNumber": log_entry.get("epochNumber", None),
    }

    return cast(EventData, AttributeDict.recursive(event_data))

    

# events.get_event_data = conditional_func(
#     cfx_get_event_data,
#     from_cfx_condition
# )(events.get_event_data)


# modify_to_conditional_func(events.get_event_data, cfx_get_event_data, from_cfx_condition)


