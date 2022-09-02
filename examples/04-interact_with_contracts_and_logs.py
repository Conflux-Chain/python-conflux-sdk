import json, os
from conflux_web3 import Web3

web3 = Web3(Web3.HTTPProvider("https://test.confluxrpc.com"))
web3.wallet.add_account(
    account := web3.account.from_key(os.environ.get("TESTNET_SECRET"))
)
web3.cfx.default_account = account.address

# you can compile erc20 yourself 
# or use our pre-compiled file https://raw.githubusercontent.com/Conflux-Chain/python-conflux-sdk/v2/tests/_test_helpers/ERC20.json
erc20_metadata = json.load(open("path/to/erc20metadata.json"))
erc20 = web3.cfx.contract(bytecode=erc20_metadata["bytecode"], abi=erc20_metadata["abi"])

# you might need to change the argument name depending on the solidity source code
# below works if wallet middleware and default account is set 
# see examples/10-send_raw_transactions.py if you want to manually sign and send transactions
hash = erc20.constructor(name="ERC20", symbol="C", initialSupply=10**18).transact()
# or use 
# contract_address = hash.executed()["contractCreated"]
contract_address = web3.cfx.wait_for_transaction_receipt(hash)["contractCreated"] 
assert contract_address is not None
print(f"contract deployed: {contract_address}")
print()

contract = web3.cfx.contract(contract_address, abi=erc20_metadata["abi"])
random_account = web3.account.create()
# contract.functions.transfer(random_account.address, 100) prebuilt the transaction
# the transaction is not send until .transact() is called
prebuilt_tx = contract.functions.transfer(random_account.address, 100)
hash = prebuilt_tx.transact()
transfer_receipt = web3.cfx.wait_for_transaction_receipt(hash)

# 2 ways to call, either is ok
balance = contract.functions.balanceOf(random_account.address).call()
balance1 = contract.caller().balanceOf(random_account.address)
assert balance1 == balance == 100
print("transfer success")
print()

# parameter definitions: https://developer.confluxnetwork.org/conflux-doc/docs/json_rpc#cfx_getlogs
fromEpoch = transfer_receipt["epochNumber"]
logs = web3.cfx.get_logs(fromEpoch=fromEpoch, address=contract_address)
print("raw logs: ")
print(logs)
print()
    
# use contract event to process logs
processed_logs = contract.events.Transfer.process_receipt(transfer_receipt)
processed_log = processed_logs[0]
assert processed_log["args"]["from"] == web3.cfx.default_account
assert processed_log["args"]["to"] == random_account.address
assert processed_log["args"]["value"] == 100
# for log in transaction["logs"], field "logIndex" and "transactionIndex" are not included
print("processed log: (no logIndex)")
print(processed_log)
print()

# generate topics to use getLogs
filter_topics = contract.events.Transfer.get_filter_topics(
    value=100,
    to=random_account.address
)
new_logs = web3.cfx.get_logs(fromEpoch=fromEpoch, topics=filter_topics)
print("logs filter by topics:")
print(new_logs)
print()

# event get_logs will return processed logs
new_processed_logs = contract.events.Transfer.get_logs(
    argument_filters={
        "value": 100,
        "to": random_account.address
    },
    fromEpoch=fromEpoch
)
print("processed logs from contract event get_logs")
print(new_processed_logs)
print()