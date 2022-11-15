# Introduction

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Conflux-Chain/python-conflux-sdk/dev?labpath=docs%2Fen%2Fexamples%2F01-quickstart.ipynb)
[![Documentation Status](https://readthedocs.org/projects/python-conflux-sdk/badge/?version=latest)](https://python-conflux-sdk.readthedocs.io/en/latest/?badge=latest)
[![gitlocalized ](https://gitlocalize.com/repo/8175/whole_project/badge.svg)](https://gitlocalize.com/repo/8175/whole_project?utm_source=badge)

[README](/README.md) | [中文文档](/docs/zh-CN/README.md)

Python SDK to interact with Conflux blockchain.

- [Introduction](#introduction)
  - [Overview](#overview)
  - [Quickstart](#quickstart)
  - [Documentations](#documentations)
    - [Run Code Examples Online!](#run-code-examples-online)
    - [Localization](#localization)


## Overview

Python-conflux-sdk helps to interact with Conflux network using python. It is built over [web3.py](https://github.com/ethereum/web3.py) and most of its APIs are consistent with [web3.py](https://github.com/ethereum/web3.py).

## Quickstart

Requirements: python version >= 3.7

```bash
$ pip3 install conflux-web3
```

```python
from conflux_web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))

acct = w3.account.from_key("0xxxxxxxxxxxxxx")
w3.cfx.default_account = acct
w3.cfx.contract(name="Faucet").claimCfx().transact().executed()

w3.cfx.send_transaction({
    'to': w3.address.zero_address(),
    'value': 10**18,
}).executed()
```

Or you can also use API as you do in `web3.py`: 

## Documentations

More detailed code examples are provided in the [documentation](https://python-conflux-sdk.readthedocs.io/en/latest/README.html).

### Run Code Examples Online!

All code examples can be run online in [mybinder](https://mybinder.org/). You can click `🚀` -> `Binder` on the top bar to activate the running environment. All dependencies wil be installed and the example can be run immediately.

### Localization

Currently this documentation supports:

* English version
* Chinese version
