from typing import (
    Union,
    overload,
)

import rlp
from hexbytes import HexBytes
from eth_utils import (
    keccak,
    to_bytes,
    to_checksum_address,
)

from cfx_address import Base32Address
from cfx_address.utils import (
    normalize_to
)
from cfx_utils.types import (
    ChecksumAddress,
)

def get_create_address(sender: Union[str, Base32Address], nonce: int, bytecode_hash: Union[bytes, str]) -> Union[ChecksumAddress, Base32Address]:
    """
    Determine the resulting `CREATE` opcode contract address for a sender and a nonce.
    Typically, the sender is a wallet address and the nonce is the next nonce of the sender.
    NOTE: in Conflux, the contract address is computed differently from that in Ethereum 
    where the bytecode hash is not accounted for in the address computation.
    
    :param sender: The address of the sender. Can be a hex string or a base32 address.
    :param nonce: The nonce of the sender.
    :param bytecode_hash: The keccak256 hash of the contract bytecode, whereas the "data" field of the transaction. Can be bytes or hex string.
    :return: The computed address as a hex string or base32 address, depending on the type of sender
    """
    address_hex = normalize_to(sender, None)
    contract_address = "0x8" + keccak(
        b"\x00"
        + to_bytes(hexstr=address_hex)
        + nonce.to_bytes(32, "little")
        + HexBytes(bytecode_hash)
    ).hex()[-39:]
    if Base32Address.is_valid_base32(sender):
        return Base32Address(contract_address, network_id=Base32Address(sender).network_id)
    return to_checksum_address(contract_address)


def get_create2_address(
    create2_factory_address: Union[str, Base32Address], salt: bytes, bytecode_hash: Union[bytes, str]
) -> Union[ChecksumAddress, Base32Address]:
    """
    Compute the address of a contract created using CREATE2.
    
    :param create2_factory_address: The address of the CREATE2 factory contract. On Conflux, it is deployed via `CIP-31 <https://github.com/Conflux-Chain/CIPs/blob/master/CIPs/cip-31.md>`_
    :param salt: A 32-byte value used as salt. Should be bytes.
    :param bytecode_hash: The keccak256 hash of the contract bytecode. Can be bytes or hex string.
    :return: The computed address as a hex string or base32 address, depending on the type of create2_factory_address
    """
    address_hex = normalize_to(create2_factory_address, None)
    contract_address = "0x8" + keccak(
        b"\xff"
        + to_bytes(hexstr=address_hex)
        + salt
        + HexBytes(bytecode_hash)
    ).hex()[-39:]
    if Base32Address.is_valid_base32(create2_factory_address):
        return Base32Address(contract_address, network_id=Base32Address(create2_factory_address).network_id)
    return to_checksum_address(contract_address)
