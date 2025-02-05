from typing import Any
from eth_abi.registry import (
    ABIRegistry,
    BaseEquals
)
from eth_abi.decoding import (
    AddressDecoder
)
from eth_abi.exceptions import (
    EncodingError
)
from web3._utils.abi import (
    build_non_strict_registry, 
    AddressEncoder,
)
from cfx_address.utils import (
    normalize_to
)
from cfx_utils.exceptions import (
    InvalidAddress,
)
from conflux_web3._utils.cns import (
    is_cns_name
)

class Base32AddressEncoder(AddressEncoder):
    
    encode_fn = lambda self, address: AddressEncoder.encode_fn(normalize_to(address, None))
    
    @classmethod
    def validate_value(cls, value: Any) -> None:
        if is_cns_name(value):
            return
        try:
            normalize_to(value, None)
        except InvalidAddress:
            raise EncodingError(f"Not a valid Base32 address nor hex address: {value}")


class CfxAddressDecoder(AddressDecoder):
    decode_fn = lambda x: x

def build_cfx_default_registry() -> ABIRegistry:
    registry = build_non_strict_registry()
    
    registry.unregister('address')
    registry.register(
        BaseEquals('address'),
        Base32AddressEncoder, CfxAddressDecoder,
        label='address',
    )
    
    return registry
