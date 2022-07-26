# from typing import Any, Optional, Tuple
# from eth_typing import ChecksumAddress, TypeStr


# @implicitly_identity
# def abi_address_to_hex(type_str: TypeStr, data: Any) -> Optional[Tuple[TypeStr, ChecksumAddress]]:
#     if type_str == 'address':
#         validate_address(data)
#         if is_binary_address(data):
#             return type_str, to_checksum_address(data)
#     return None