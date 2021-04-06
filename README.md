# python-conflux-sdk
This is the Python SDK to interact with Conflux network.

## How to install

```shell
$ pip3 install python-conflux-sdk
```

## How to use

### Interact with RPC

```python
from conflux import (
    Conflux,
    HTTPProvider,
)
provider = HTTPProvider('https://testnet-rpc.conflux-chain.org.cn/v2')
conflux = Conflux(provider)

# get RPC's clientVersion
print(conflux.clientVersion)

test_address = 'cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da'

balance = conflux.cfx.getBalance(test_address)

print(conflux.fromDrip(balance))
```


### Conflux base32 address utilities

```python
from conflux.address import Address
# create from base32 address
address_a = Address('cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da')
print(address_a.address)
print(address_a.hex_address)
print(address_a.network_id)
print(address_a.verbose_address)
# create from hex address and network_id
address_b = Address.create_from_hex_address('0x1ecde7223747601823f7535d7968ba98b4881e09', 1)
```


### Account 

```python
from conflux.account import Account

random_account = Account.create("custom random inputs", 1)
private_key_account = Account.from_key("your private key", 1)

print(random_account.hex_address)
print(random_account.cfx_address)
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

conflux.cfx.sendRawTransaction(signed_tx.rawTransaction.hex())
```


## Conflux network misc

### chainId (networkId)
1. main-net: 1029
2. test-net: 1

### RPC 
1. main-net: https://main.confluxrpc.org/v2
2. test-net: https://test.confluxrpc.org/v2