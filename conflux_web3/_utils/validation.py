from typing import (
    Any
)

from cfx_address.utils import validate_base32

class InvalidBase32Address(ValueError):
    """
    The supplied address is not a valid Base32 address, as defined in CIP-37
    """

validate_base32_address = validate_base32
