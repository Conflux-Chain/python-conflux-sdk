from typing import Any
from eth_abi.registry import (
    ABIRegistry,
    BaseEquals
)
from eth_abi.decoding import (
    AddressDecoder
)
from web3._utils.abi import (
    build_default_registry, 
    AddressEncoder,
)
from cfx_address import (
    Base32Address,
    validate_base32
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
        validate_base32(value)

class CfxAddressDecoder(AddressDecoder):
    decode_fn = lambda x: x

def build_cfx_default_registry() -> ABIRegistry:
    registry = build_default_registry()
    
    registry.unregister('address')
    registry.register(
        BaseEquals('address'),
        Base32AddressEncoder, CfxAddressDecoder,
        label='address',
    )
    
    return registry
