# import functools
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Sequence,
)
import json
from hexbytes import HexBytes

from eth_typing.encoding import HexStr
from eth_utils.hexadecimal import encode_hex
from eth_utils.conversions import to_hex

from web3.types import ABIFunction
from web3._utils import contracts
from web3._utils.abi import (
    check_if_arguments_can_be_encoded,
    get_abi_input_types,
    map_abi_data,
)
from web3._utils.normalizers import (
    abi_bytes_to_bytes,
    abi_string_to_text,
)

from conflux_web3._utils.normalizers import (
    abi_cns_resolver
)

if TYPE_CHECKING:
    from conflux_web3 import Web3

# this api is used to hook web3._utils.contracts.encode_abi
# hook is activated in _web3_hook
def cfx_encode_abi(
    web3: "Web3", abi: ABIFunction, arguments: Sequence[Any], data: Optional[HexStr] = None
) -> HexStr:
    """
    do what encode_abi does except for normalizers
    """
    argument_types = get_abi_input_types(abi)

    if not check_if_arguments_can_be_encoded(abi, web3.codec, arguments, {}):
        raise TypeError(
            "One or more arguments could not be encoded to the necessary "
            "ABI type.  Expected types are: {0}".format(
                ', '.join(argument_types),
            )
        )

    # abi_ens_resolver and abi_address_to_hex are eliminated
    normalizers = [
        abi_cns_resolver(web3), # type: ignore
        # abi_address_to_hex,
        abi_bytes_to_bytes,
        abi_string_to_text,
    ]
    normalized_arguments = map_abi_data(
        normalizers,
        argument_types,
        arguments,
    )
    encoded_arguments = web3.codec.encode(
        argument_types,
        normalized_arguments,
    )

    if data:
        return to_hex(HexBytes(data) + encoded_arguments)
    else:
        return encode_hex(encoded_arguments)

prepare_transaction = contracts.prepare_transaction
