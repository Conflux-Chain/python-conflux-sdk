# Introduction

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/conflux-chain/python-conflux-sdk/dev?urlpath=tree/docs/en/examples/01-quickstart.ipynb)
[![Documentation Status](https://readthedocs.org/projects/python-conflux-sdk/badge/?version=latest)](https://python-conflux-sdk.readthedocs.io/en/latest/?badge=latest)
[![gitlocalized ](https://gitlocalize.com/repo/8175/whole_project/badge.svg)](https://gitlocalize.com/repo/8175/whole_project?utm_source=badge)

[README](https://python-conflux-sdk.readthedocs.io/en/latest/README.html) | [中文文档](https://python-conflux-sdk.readthedocs.io/zh_CN/latest/README.html)

- [Introduction](#introduction)
  - [概览](#概览)
  - [Quickstart](#quickstart)
  - [文档](#文档)
    - [在线运行示例代码](#在线运行示例代码)
    - [本地化](#本地化)


## 概览

Python-conflux-sdk 帮助开发者使用 python 与 Conflux 区块链交互，本库基于 [web3.py](https://github.com/ethereum/web3.py) 构建且大部分 API 与 `web3.py` 兼容。

## Quickstart

安装需求: python >= 3.7

```bash
pip3 install conflux-web3
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

您也可以按照 `web3.py` 的 API 风格使用本 SDK： 

``` python
# 由 https://web3py.readthedocs.io/en/stable/middleware.html#signing 修改而来
from conflux_web3 import Web3
w3 = Web3("https://test.confluxrpc.com")
from conflux_web3.middleware import construct_sign_and_send_raw_middleware
from cfx_account import Account
acct = Account.create('KEYSMASH FJAFJKLDSKF7JKFDJ 1530')
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(acct))
w3.cfx.default_account = acct.address

transaction = {
    'to': w3.address.zero_address(),
    'value': 22,
}
w3.cfx.send_transaction(transaction)
```

## 文档

更详细的文档与用例可以参考 [文档](https://python-conflux-sdk.readthedocs.io/zh-CN/latest/README.html)。

### 在线运行示例代码

文档中提供的示例代码可以通过[mybinder](https://mybinder.org/)在线运行。 您可以依次点击代码示例页顶部的 `🚀` -> `Binder` 来启动环境。环境中已配置好运行代码的必备依赖，因此相关代码可以直接运行。

### 本地化

当前的文档支持两种语言:

* 英文版本
* 中文版本

欢迎您通过 [GitLocalize](https://gitlocalize.com/repo/8175) 为我们提供翻译。
