from conflux_web3.main import Web3

def get_local_web3():
    return Web3(Web3.HTTPProvider("http://127.0.0.1:12537"))

def get_testnet_web3():
    return Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))

def get_mainnet_web3():
    return Web3(Web3.HTTPProvider("https://main.confluxrpc.com"))
