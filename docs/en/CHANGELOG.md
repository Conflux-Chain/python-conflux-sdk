# Change Logs

## 1.0.0

* Release

## 1.0.0-dev8

* fix: error caused by `find_functions_by_identifier`
* add more strict format checking for `is_cns_name`

## 1.0.0-dev7

* type hints: migrate to `Pylance`; add `py.typed`
* fix: cns recursive import problem
* feature: default network id by using `web3.address`
* feature: support python3.7
* doc: add inline documents for frequently used RPCs
* change: recover `estimate_gas_and_collateral`, `gas_price` returned token units

## 1.0.0-dev6

* bug fix: include the contract metadata in the release

## 1.0.0-dev4

* Response containing "address" from rpc is wrapped by `Base32Address`
  * including contract return values
* Introduces token unit `CFX`, `GDrip` and `Drip`
  * responses are formatted using Drip/GDrip/CFX
  * Drip/GDrip/CFX can be used as gas price or value
* CNS support
  * available by using `w3.cns` or `w3.ens`
  * supports name service resolve as web3.py (as receiver/sender/parameter)
  * (unstable) supports `w3.cns.setup_address` and `w3.cns.setup_owner`

## 1.0.0-dev3

* bump web3.py version
  * web3.py: 6.0.0b4->6.0.0b5
  * eth-account(required by cfx-account): ~=7.0.0

## 1.0.0-dev2

* Optimizes web3.py hacking mechanisms
  * hacking codes are moved to `conflux_web3._hook.py`
* Basic support for ethpm (furthur supports are not in plan)
* The default account will be added to wallet if `w3.cfx.default_account` setter receives a `LocalAccount` object
  * `w3.cfx.default_account` is still a `Base32Address`
* `.finalized()` apis are tests.
* Fix contract constructor's `build_transaction()` bugs
* Add `name` parameter to `w3.cfx.contract()`
  * supports internal contracts including `AdminControl`, `SponsorWhitelistControl`, `Staking`, `PoSRegister`, `CrossSpaceCall`, `ParamsControl`
  * supports specific contracts added in genesis block, including `Create2Factory`, `ERC1820`
  * supports `Faucet` in testnet
  * supports `cUSDT` and `FC` in mainnet and testnet
