# python-conflux-sdk
A Python SDK for interacting with Conflux network.

## How to install

```shell
$ pip3 install conflux
```

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

print(c.fromDrip(balance))
```


### Conflux base32 address utilities

```python
from conflux import Address
# create from base32 address
addr_a = Address('cfxtest:aak7fsws4u4yf38fk870218p1h3gxut3ku00u1k1da')
print(addr_a.address)
print(addr_a.hex_address)
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

random_account = Account.create("custom random inputs", 1)
private_key_account = Account.from_key("your private key", 1)

print(random_account.address)
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


## Conflux network misc

### chainId (networkId)
1. main-net: 1029
2. test-net: 1

### RPC 
1. main-net: https://main.confluxrpc.com
2. test-net: https://test.confluxrpc.com