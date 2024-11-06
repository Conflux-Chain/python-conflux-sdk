from typing import TYPE_CHECKING
import pytest


from conflux_web3 import Web3
from conflux_web3.contract.metadata import get_contract_metadata
from cfx_utils.exceptions import Base32AddressNotMatch


if TYPE_CHECKING:
    from conflux_web3 import Web3


def test_contract_initialization(w3: Web3):
    metadata = get_contract_metadata("AdminControl")
    chain_id = w3.cfx.chain_id
    metadata["address"] = w3.cfx.address(metadata["address"], chain_id + 1)

    with pytest.raises(Base32AddressNotMatch):
        w3.cfx.contract(**metadata)


def test_contract_with_no_deployment_info(w3: Web3):
    c = w3.cfx.contract(name="AdminControl", with_deployment_info=False)
    assert not c.address


# This is an error from upstream web3.py and will be fixed in https://github.com/ethereum/web3.py/issues/3482
# def test_get_function_by_signature(w3: Web3, account: LocalAccount):
#     from tests._test_helpers.ENV_SETTING import HELPER_DIR
#     with open(os.path.join(HELPER_DIR, "amb_metadata.json")) as f:
#         metadata = json.load(f)
#     contract = w3.cfx.contract(abi=metadata['abi'], bytecode=metadata["bin"])
#     # with pytest.raises(ValidationError):
#     #     contract.functions.identity(account.address, True)

#     w3.cfx.default_account = account
#     contract_addr = contract.constructor().transact().executed()["contractCreated"]
#     assert contract_addr
#     contract = contract(contract_addr)
#     func = contract.get_function_by_signature('identity(address,bool)')
#     assert func(account.address, True).call() == account.address # returned address should be in Base32 format
#     assert contract.get_function_by_signature('identity(string,bool)')(account.address, True).call() == account.address
#     assert contract.get_function_by_signature('identity(string,bool)')("conflux", True).call() == "conflux"
