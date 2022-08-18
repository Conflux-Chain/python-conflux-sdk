from typing import Any
from eth_abi.registry import (
    ABIRegistry,
    BaseEquals
)
from eth_abi.decoding import (
    AddressDecoder
)
from web3._utils.abi import build_default_registry, AddressEncoder
from conflux_web3._utils.validation import validate_base32_address
from cfx_address import Base32Address

class Base32AddressEncoder(AddressEncoder):
    
    encode_fn = lambda self, address: AddressEncoder.encode_fn(Base32Address(address).hex_address)
    
    @classmethod
    def validate_value(cls, value: Any) -> None:
        validate_base32_address(value)

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
