# Introduction

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/conflux-chain/python-conflux-sdk/dev?urlpath=tree/docs/en/examples/01-quickstart.ipynb)
[![Documentation Status](https://readthedocs.org/projects/python-conflux-sdk/badge/?version=latest)](https://python-conflux-sdk.readthedocs.io/en/latest/?badge=latest)
[![codecov](https://codecov.io/github/Conflux-Chain/python-conflux-sdk/branch/dev/graph/badge.svg?token=GZ62V9QW0A)](https://codecov.io/github/Conflux-Chain/python-conflux-sdk)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/conflux-web3)

[README](https://python-conflux-sdk.readthedocs.io/en/latest/README.html) | [中文文档](https://python-conflux-sdk.readthedocs.io/zh_CN/latest/README.html)

- [Introduction](#introduction)
  - [Overview](#overview)
  - [Quickstart](#quickstart)
  - [Documentations](#documentations)
    - [Run Code Examples Online!](#run-code-examples-online)


## Overview

Python-conflux-sdk (or conflux-web3) helps to interact with Conflux network using python. It is built over [web3.py](https://github.com/ethereum/web3.py) and most of its APIs are consistent with [web3.py](https://github.com/ethereum/web3.py).

> Note: python-conflux-sdk v1.3.0 is the version compatible with web3.py v6.x. If you are using web3.py v7.x, please use the v1.4.0 or later.

## Quickstart

Requirements: python version >= 3.8

```bash
$ pip3 install conflux-web3
```

```python
from conflux_web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))

acct = w3.account.from_key("0xxxxxxxxxxxxxx")
w3.cfx.default_account = acct

# Uncomment the following line if there is not CFX in your account
# w3.cfx.contract(name="Faucet").claimCfx().transact().executed()

w3.cfx.send_transaction({
    'to': w3.address.zero_address(),
    'value': 10**18,
}).executed()
```

Or you can also use API as you do in `web3.py` before v6.20:

``` python
# modified from https://web3py.readthedocs.io/en/v6.20.2/transactions.html#chapter-1-w3-eth-send-transaction-signer-middleware
from conflux_web3 import Web3
w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
from conflux_web3.middleware import SignAndSendRawMiddlewareBuilder
from cfx_account import Account
acct = Account.create('KEYSMASH FJAFJKLDSKF7JKFDJ 1530', network_id=w3.cfx.chain_id)
w3.middleware_onion.inject(SignAndSendRawMiddlewareBuilder.build(acct), layer=0)
w3.cfx.default_account = acct.address

transaction = {
    'to': w3.address.zero_address(),
    'value': 22,
}
w3.cfx.send_transaction(transaction)
```

## Documentations

More detailed code examples are provided in the [documentation](https://python-conflux-sdk.readthedocs.io/en/latest/README.html).

### Run Code Examples Online!

All code examples can be run online in [mybinder](https://mybinder.org/). You can click `🚀` -> `Binder` on the top bar to activate the running environment. All dependencies wil be installed and the example can be run immediately.
