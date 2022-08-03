from conflux_web3 import Web3

def test_basetx(w3: Web3, secret_key: str):
    account = w3.account.from_key(secret_key, w3.cfx.chain_id)
    # assert w3.isConnected()
    status = w3.cfx.get_status()
    
    # addr = w3.address.encode_hex_address(account.address, w3.cfx.chain_id)
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
    assert w3.cfx.send_raw_transaction(rawTx)
    