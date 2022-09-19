# conflux-web3 
Python SDK for interacting with Conflux network.

- [conflux-web3](#conflux-web3)
  - [Quick start](#quick-start)
  - [Overview](#overview)
    - [Code Examples](#code-examples)
      - [initialization with providers](#initialization-with-providers)
      - [Contract Interaction](#contract-interaction)
      - [RPC support](#rpc-support)
      - [Base32 Address Operation](#base32-address-operation)

## Quick start

Requirements: python version >= 3.8

```shell
$ pip3 install --pre conflux-web3
```

```python
from conflux_web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
# fill your secret key
# and you can claim testnet token from https://faucet.confluxnetwork.org/
acct = w3.account.from_key("0xxxxxxxxxxxxxx") 
w3.wallet.add_account(acct)
w3.cfx.default_account = acct.address

w3.cfx.send_transaction({
    'to': w3.cfx.account.create().address,
    'value': 22,
}).executed()
```

## Overview

conflux-web3 helps to interact with Conflux network using python, and most of its APIs are consistent with [web3.py](https://github.com/ethereum/web3.py). 

> conflux-web3 is a wrapping layer over [web3.py](https://github.com/ethereum/web3.py).

### Code Examples

Here are some simple code examples. More detailed code examples are in the folder `examples`

#### initialization with providers

```python
# same as web3.py
from conflux_web3 import Web3
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:12537"))

# or
# conflux_web3's additional functions
# using local default HTTP provider or Conflux's public RPC FOR DEVELOPMENT
from conflux_web3.dev import (
    get_local_web3, # "http://127.0.0.1:12537"
    get_testnet_web3, # "https://test.confluxrpc.com"
    get_mainnet_web3, # "https://main.confluxrpc.com"
)
w3 = get_testnet_web3()
```

#### Contract Interaction

``` py
import os, json
from conflux_web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
acct = w3.cfx.account.from_key(os.environ.get('PRIVATE_KEY'))
w3.wallet.add_account(acct)
w3.cfx.default_account = acct.address

# if you want to get contract object from metadata file, uses 
# >>> erc20_metadata = json.load(open("path/to/ERC20metadata.json"))
# >>> erc20 = web3.cfx.contract(bytecode=erc20_metadata["bytecode"], abi=erc20_metadata["abi"])
erc20 = web3.cfx.contract(name="ERC20")
hash = erc20.constructor(name="Coin", symbol="C", initialSupply=10**18).transact()
contract_address = w3.cfx.wait_for_transaction_receipt(hash)["contractCreated"]
assert contract_address is not None
contract = w3.cfx.contract(contract_address, name="ERC20")

# transfer
random_account = w3.account.create()
hash = contract.functions.transfer(random_account.address, 100).transact()
transfer_receipt = w3.cfx.wait_for_transaction_receipt(hash)
balance = contract.functions.balanceOf(random_account.address).call()
```

#### RPC support

Visit [JSON-RPC methods](https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc/#json-rpc-methods) to check the full RPC list. Currently, most frequently used RPCs are supported.

``` python
w3.cfx.get_balance("cfx:aarc9abycue0hhzgyrr53m6cxedgccrmmyybjgh4xg", "latest_state")
# the returned value from RPC will be formatted
# 158972490234375000
```

#### Base32 Address Operation

You can use `from cfx_address import Base32Address` or simply use `w3.address` or `w3.cfx.address` to use the `Base32Address` class. This class provides several methods for you to convert or validate base32 addresses. See [cfx_address documentation](https://conflux-fans.github.io/cfx-address/cfx_address.html#module-cfx_address.address) for the full documentation.

```py
from cfx_address import Base32Address

address = Base32Address("0x1ecde7223747601823f7535d7968ba98b4881e09", network_id=1)
address
# 'cfxtest:aatp533cg7d0agbd87kz48nj1mpnkca8be1rz695j4'
[
    address.address_type,
    address.network_id,
    address.hex_address,
    address.verbose_address,
    address.abbr,
    address.mapped_evm_space_address,
    address.eth_checksum_address,
]
# ['user', 1, '0x1ecde7223747601823f7535d7968ba98b4881e09', 'CFXTEST:TYPE.USER:AATP533CG7D0AGBD87KZ48NJ1MPNKCA8BE1RZ695J4', 'cfxtest:aat...95j4', '0x349f086998cF4a0C5a00b853a0E93239D81A97f6', '0x1ECdE7223747601823f7535d7968Ba98b4881E09']
```
