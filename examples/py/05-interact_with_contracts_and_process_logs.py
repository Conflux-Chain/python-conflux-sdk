# ## `conflux-web3` Code Example 05: Interact with Contracts and Process Logs
# 
# Run this example online --> [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/Conflux-Chain/python-conflux-sdk/dev?labpath=examples%2Fipynb%2F04-query_data_via_RPC.ipynb)

# ### Preparation

import pprint
from conflux_web3 import Web3

w3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
account = w3.account.create()
w3.cfx.default_account = account

faucet = w3.cfx.contract(name="Faucet")
faucet.functions.claimCfx().transact().executed()
print()

# ## Interact with Contracts
# 
# In the [Preparation](#preparation) part, we have already shown how to interact with a contract. A contract instance can be initialized from `w3.cfx.contract`. With the `name` paramter, some frequently used contract instance can be created. 

# ### Compile and Deploy a Contract
# 
# A contract is a program running on the blockchain. And we need to firstly **deploy** a contract to the blockchain if we want to interact with a program written by ourselves.
# 
# Here is a simple smart contract:
# 
# ``` solidity
# // SPDX-License-Identifier: MIT
# // modified from https://solidity-by-example.org/first-app/
# pragma solidity ^0.8.13;
# 
# contract Counter {
#     uint public count;
# 
#     event Change(address indexed sender, uint new_value);
# 
#     constructor(uint init_value) {
#         count = init_value;
#     }
# 
#     // Function to get the current count
#     function get() public view returns (uint) {
#         return count;
#     }
# 
#     // Function to increment count by 1
#     function inc() public {
#         count += 1;
#         emit Change(msg.sender, count);
#     }
# }
# ```
# 
# After this contract is compiled and deployed, you can:
# 
# * read the value of `count` from interface `get`
# * add the variable `count` by invoking `inc`
# 
# Besides, the contract will emit an event `Change` after `inc` is executed, we can know what has happened on chain by analyzing the logs.
# 
# You might need to run `pip install py-solc-x` if you are running the the codes in your local environment.

# py-solc-x is already installed in the test environment
from solcx import install_solc, compile_source
source_code = r"""
// SPDX-License-Identifier: MIT
// modified from https://solidity-by-example.org/first-app/
pragma solidity ^0.8.13;

contract Counter {
    uint public count;

    event Change(address indexed sender, uint new_value);

    constructor(uint init_value) {
        count = init_value;
    }

    // Function to get the current count
    function get() public view returns (uint) {
        return count;
    }

    // Function to increment count by 1
    function inc() public {
        count += 1;
        emit Change(msg.sender, count);
    }
}
"""
metadata = compile_source(
    source_code,
    output_values=['abi', 'bin'],
    solc_version=install_solc(version="0.8.13")
).popitem()[1]
# "abi" defines the interface, "bin" is the contract bytecode
assert "abi" in metadata and "bin" in metadata

# init contract from metadata, bytecode is needed to deploy a contract
factory = w3.cfx.contract(abi=metadata["abi"], bytecode=metadata["bin"])

# deploy the contract
tx_receipt = factory.constructor(init_value=0).transact().executed()
contract_address = tx_receipt["contractCreated"]
assert contract_address is not None
print(f"contract deployed: {contract_address}")

# init a contract with address param, now we can interact with it
deployed_contract = w3.cfx.contract(address=contract_address, abi=metadata["abi"])

# ### Interact with the Deployed Contract

tx_hash = deployed_contract.functions.inc().transact()
inc_receipt = w3.cfx.wait_for_transaction_receipt(tx_hash)

# "call" a contract means virtually execute the transaction without actually sending a transaction
# 2 ways to call, either is ok
current_counter = deployed_contract.functions.get().call()
current_counter_ = deployed_contract.caller().get()
assert current_counter == current_counter_ == 1
print("counter added to 1")

# ## Process Logs
# 
# We can check transaction logs to know what has happened after transaction execution. However, raw logs are encoded in hex and is hard to read.

# get_logs parameter definitions: https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc#cfx_getlogs
fromEpoch = inc_receipt["epochNumber"]
# use get_logs to get raw logs
logs = w3.cfx.get_logs(fromEpoch=fromEpoch, address=contract_address)
print("raw log: ")
pprint.pprint(dict(logs[0]))


# In the following parts, we present several approaches to process and filter logs.
# 
# We can use `contract.event` to process logs. The `args` field of processed log presents

processed_logs = deployed_contract.events.Change.process_receipt(inc_receipt)
processed_log = processed_logs[0]
assert processed_log["args"]["sender"] == w3.cfx.default_account
assert processed_log["args"]["new_value"] == 1

# for log processed from transaction receipt, field "logIndex" is None
pprint.pprint(dict(processed_log))

# Besides, we can use `contract.events` to encode contract topics and filter logs

# generate topics to use getLogs
filter_topics = deployed_contract.events.Change.get_filter_topics(
    sender=w3.cfx.default_account
)
new_logs = w3.cfx.get_logs(fromEpoch=fromEpoch, topics=filter_topics)
print("log filtered by topics:")
pprint.pprint(dict(new_logs[0]))

# Or we can use `get_logs` interface from `contract.events`

# event get_logs will return processed logs
new_processed_logs = deployed_contract.events.Change.get_logs(
    argument_filters={
        "sender": w3.cfx.default_account
    },
    fromEpoch=fromEpoch
)
print("processed log from contract event get_logs")
pprint.pprint(dict(new_processed_logs[0]))

# `conflux_web3`'s apis are consistent with `web3.py`'s apis. You can also try the examples from `web3.py`'s documentation.
# * https://web3py.readthedocs.io/en/stable/contracts.html
# * https://web3py.readthedocs.io/en/stable/examples.html#working-with-contracts
# * https://web3py.readthedocs.io/en/stable/examples.html#working-with-an-erc20-token-contract

