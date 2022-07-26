from typing import (
    Any
)

from cfx_address import Address

class InvalidBase32Address(ValueError):
    """
    The supplied address is not a valid Base32 address, as defined in CIP-37
    """


def validate_base32_address(value: Any) -> None:
    """
    Helper function for validating an address
    """
    if not Address.is_valid_base32(value):
        raise InvalidBase32Address(
            "Address needs to be encode in Base32 format, such as cfx:aaejuaaaaaaaaaaaaaaaaaaaaaaaaaaaajrwuc9jnb"
        )
    return 