from typing import (
    Any
)
from web3._utils import validation 
from web3._utils.validation import validate_address as validate_web3_address
from cfx_address.utils import validate_base32
from cfx_utils.exceptions import InvalidAddress

class InvalidBase32Address(ValueError):
    """
    The supplied address is not a valid Base32 address, as defined in CIP-37
    """

# def validate_universal_address(value: Any):
#     try:
#         validate_web3_address(value)
#         return 
#     except:
#         try:
#             validate_base32(value)
#         except:
#             raise InvalidAddress

# validation.validate_address = validate_universal_address
