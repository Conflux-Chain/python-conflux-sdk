# python-conflux-sdk
A Python SDK for interacting with Conflux network.

Note: this SDK still is in developing, and the API may change in the future.

## How to install

```shell
$ pip3 install conflux
```

## Features

1. Base32 address utilities
2. Account for signing Conflux transaction
3. Conflux RPC interaction

## How to use

### Interact with RPC

```python
from conflux import (
    Conflux,
    HTTPProvider,
)
provider = HTTPProvider('https://test.confluxrpc.com')
c = Conflux(provider)

# get RPC's clientVersion
print(c.clientVersion)

test_address = 'cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da'
balance = c.cfx.getBalance(test_address)
print(balance)
```


### Conflux base32 address utilities

```python
from conflux import Address
# create from base32 address
addr_a = Address('cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da')
print(addr_a.address)
print(addr_a.hex_address)
print(addr_a.eth_checksum_address)
print(addr_a.network_id)
print(addr_a.verbose_address)
# create from hex address and network_id
address_b = Address.create_from_hex_address('0x1ecde7223747601823f7535d7968ba98b4881e09', 1)
```


### Account 

```python
from conflux import (
    Account,
    Conflux,
    HTTPProvider,
)
provider = HTTPProvider('https://test.confluxrpc.com')
c = Conflux(provider)

random_account = Account.create("custom random inputs")
private_key_account = Account.from_key("your private key")

print(random_account.address)  # this is an hex address, you can use Address convert it to an base32 address
print(random_account.key)

transaction = {
    'from': 'cfxtest:aak2rra2njvd77ezwjvx04kkds9fzagfe6d5r8e957',
    'to': 'cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da',
    'nonce': 1,
    'value': 1,
    # data: '0x',
    'gas': 100,
    'gasPrice': 1,
    'storageLimit': 100,
    'epochHeight': 100,
    'chainId': 1
}

signed_tx = Account.sign_transaction(transaction, random_account.key)
print(signed_tx.hash.hex())
print(signed_tx.rawTransaction.hex())

c.cfx.sendRawTransaction(signed_tx.rawTransaction.hex())
```

### Contract interaction
The SDK currently only have primitive support for contract interaction 

If you need invoke contract's method and change it's state
```python
# initiate an contract instance with abi, bytecode, or address
contract = c.contract(contract_address, contract_abi)
data = contract.encodeABI(fn_name="transfer", args=["0x13d2bA4eD43542e7c54fbB6c5fCCb9f269C1f94C", 100])
tx_info = {
    'from': 'cfxtest:aak2rra2njvd77ezwjvx04kkds9fzagfe6d5r8e957',
    'to': 'cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da',
    'data': data,
}
# populate tx with other parameters for example: chainId, epochHeight, storageLimit
# then sign it with account
signed_tx = Account.sign_transaction(tx_info, random_account.key)
c.cfx.sendRawTransaction(signed_tx.rawTransaction.hex())
```

If you only want to query contract's state
```python
result = c.call_contract_method(contract_address, contract_abi, 'balanceOf', "0x13d2bA4eD43542e7c54fbB6c5fCCb9f269C1f94C")
```

We will add more support for contract interaction in the future.

## Work with web3.py
A lot of web3py utilities can directly work on Conflux, for example:

1. [eth-utils](https://eth-utils.readthedocs.io/en/stable/) for type conversion, hex encodings and so on 
2. [eth-abi](https://eth-abi.readthedocs.io/en/latest/) for abi encoding & decoding
3. [eth-hash](https://eth-hash.readthedocs.io/en/latest/) for keccak256

## Conflux network misc

### chainId (networkId)
1. main-net: 1029
2. test-net: 1

### RPC 
1. main-net: https://main.confluxrpc.com
2. test-net: https://test.confluxrpc.com

## Docs

1. [Official development site](https://developer.conflux-chain.org/)
2. [RPC methods documentation](https://developer.conflux-chain.org/docs/conflux-doc/docs/json_rpc)
3. [Available public RPCs](https://github.com/conflux-fans/conflux-rpc-endpoints)
4. [Conflux faqs](https://github.com/conflux-fans/conflux-faqs)
