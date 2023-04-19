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
from cfx_address import (
    Base32Address,
    validate_base32
)
from cfx_utils.exceptions import (
    InvalidBase32Address
)
from conflux_web3._utils.cns import (
    is_cns_name
)

class Base32AddressEncoder(AddressEncoder):
    
    encode_fn = lambda self, address: AddressEncoder.encode_fn(Base32Address(address).hex_address)
    
    @classmethod
    def validate_value(cls, value: Any) -> None:
        if is_cns_name(value):
            return
        try:
            validate_base32(value)
        except InvalidBase32Address:
            raise EncodingError(InvalidBase32Address)

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
