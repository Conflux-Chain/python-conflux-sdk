# Change Logs

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
