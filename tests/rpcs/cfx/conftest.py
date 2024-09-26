import pytest
from conflux_web3 import Web3
from conflux_web3.types import Base32Address, HexBytes
from conflux_web3.contract.metadata import get_contract_metadata

@pytest.fixture(scope="module")
def tx_hash(moduled_w3: Web3, secret_key: str) -> HexBytes:
    w3 = moduled_w3
    status = w3.cfx.get_status()
    account = w3.account.from_key(secret_key)
    addr = account.address
    
    tx = {
        'from': addr,
        'nonce': w3.cfx.get_next_nonce(addr),
        'gas': 21000,
        'to': "cfxtest:aamd4myx7f3en2yu95xye7zb78gws09gj2ykmv9p58",
        'value': 100,
        'gasPrice': 10**9,
        'chainId': w3.cfx.chain_id,
        'storageLimit': 0,
        'epochHeight': status['epochNumber']
    }
    signed = account.sign_transaction(tx)
    rawTx = signed.rawTransaction
    h = w3.cfx.send_raw_transaction(rawTx)
    h.executed()
    return h

@pytest.fixture(scope="module")
def contract_address(moduled_w3: Web3):
    erc20_metadata = get_contract_metadata("ERC20")
    erc20 = moduled_w3.cfx.contract(bytecode=erc20_metadata["bytecode"], abi=erc20_metadata["abi"])
    hash = erc20.constructor(name="Coin", symbol="C", initialSupply=10**18).transact()
    contract_address = hash.executed()["contractCreated"]
    return contract_address

@pytest.fixture(scope="module")
def tx_with_log(moduled_w3: Web3, contract_address: Base32Address) -> HexBytes:
    w3 = moduled_w3
    erc20_metadata = get_contract_metadata("ERC20")
    erc20 = w3.cfx.contract(address=contract_address, abi=erc20_metadata["abi"])

    hash = erc20.functions.transfer(w3.account.create().address, 100).transact()
    hash.executed()
    return hash