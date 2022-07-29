from conflux_web3.types import Base32Address
from conflux_web3._utils.validation import validate_base32_address


def normalize_address(ens: None, address: Base32Address) -> Base32Address:
    if address:
        validate_base32_address(address)
    return address
