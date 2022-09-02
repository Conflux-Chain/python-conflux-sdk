from conflux_web3 import Web3

def test_next_nonce(w3: Web3, address):
    nonce = w3.txpool.next_nonce(address)
    assert isinstance(nonce, int)
