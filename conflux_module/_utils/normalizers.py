from conflux_module.types import Base32Address
from conflux_module._utils.validation import validate_base32_address


def normalize_address(ens: None, address: Base32Address) -> Base32Address:
    if address:
        validate_base32_address(address)
    return address
