# import functools
from typing import (
    TYPE_CHECKING,
    Any,
    Optional,
    Sequence,
)
from hexbytes import HexBytes

from eth_typing.encoding import (
    HexStr,
)
from eth_utils.hexadecimal import (
    encode_hex,
)
from eth_utils.conversions import (
    to_hex,
)

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
from web3.types import (
    ABIFunction,
)

from conflux_module._utils.decorators import (
    cfx_web3_condition,
    conditional_func
)

if TYPE_CHECKING:
    from web3 import Web3

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
    
# hack the encode_abi function of _util.contracts module
contracts.encode_abi = conditional_func(
    cfx_encode_abi,
    cfx_web3_condition
)(contracts.encode_abi)

prepare_transaction = contracts.prepare_transaction

