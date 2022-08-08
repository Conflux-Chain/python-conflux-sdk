## Code styles

### type hints

- for inputs, be flexible
- for outputs, be strict

```python
# recommended
def receives_address(address: Union[Base32Address, str]) -> Base32Address:
    return address

def receives_hash(hash: Union[_Hash32, str]) -> HexBytes:
    return hash
```

such style suit for `conflux_web3.types, tests._test_helpers.type_check`


