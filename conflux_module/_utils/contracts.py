from copy import deepcopy
# from modulefinder import Module
# import functools
from turtle import clone
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Sequence,
    Type,
    # Tuple,
    # Type,
    # Union,
    # cast,
    
)

from eth_typing import (
    # ChecksumAddress,
    HexStr,
)
from eth_utils import (
    encode_hex,
)
# from eth_utils.toolz import (
#     pipe,
#     valmap,
# )
from hexbytes import (
    HexBytes,
)

from web3._utils.abi import (
    abi_to_signature,
    check_if_arguments_can_be_encoded,
    filter_by_argument_count,
    filter_by_argument_name,
    filter_by_encodability,
    filter_by_name,
    filter_by_type,
    get_abi_input_types,
    get_aligned_abi_inputs,
    get_fallback_func_abi,
    get_receive_func_abi,
    map_abi_data,
    merge_args_and_kwargs,
)
from web3._utils.encoding import (
    to_hex,
)
from web3._utils.function_identifiers import (
    FallbackFn,
    ReceiveFn,
)
from web3._utils.normalizers import (
    abi_address_to_hex,
    abi_bytes_to_bytes,
    abi_ens_resolver,
    abi_string_to_text,
)
from web3._utils import contracts
# from web3._utils.contracts import (
#     encode_abi,
#     prepare_transaction
# )
from web3.exceptions import (
    ValidationError,
)
from web3.types import (
    ABI,
    ABIEvent,
    ABIFunction,
    TxParams,
)

from conflux_module._utils.decorators import (
    temp_alter_module_variable,
    cfx_web3_condition,
    conditional_func
)


def cfx_encode_abi(
    web3: "Web3", abi: ABIFunction, arguments: Sequence[Any], data: Optional[HexStr] = None
) -> HexStr:
    argument_types = get_abi_input_types(abi)

    if not check_if_arguments_can_be_encoded(abi, web3.codec, arguments, {}):
        raise TypeError(
            "One or more arguments could not be encoded to the necessary "
            "ABI type.  Expected types are: {0}".format(
                ', '.join(argument_types),
            )
        )

    normalizers = [
        # abi_ens_resolver(web3),
        # abi_address_to_hex,
        abi_bytes_to_bytes,
        abi_string_to_text,
    ]
    normalized_arguments = map_abi_data(
        normalizers,
        argument_types,
        arguments,
    )
    encoded_arguments = web3.codec.encode_abi(
        argument_types,
        normalized_arguments,
    )

    if data:
        return to_hex(HexBytes(data) + encoded_arguments)
    else:
        return encode_hex(encoded_arguments)
    
# contracts.encode_abi = cfx_encode_abi
contracts.encode_abi = conditional_func(
    cfx_encode_abi,
    cfx_web3_condition
)(contracts.encode_abi)

prepare_transaction = contracts.prepare_transaction

