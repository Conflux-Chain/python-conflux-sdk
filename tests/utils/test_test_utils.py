from typing import (
    List,
    TypedDict,
    Union,
    Sequence,
)
from tests._test_helpers.type_check import (
    TypeValidator
)

def test_base_check():
    val = 1
    typ = int
    assert TypeValidator.isinstance(val, typ)
    
def test_union_check():
    vs= [1, "2"]
    typ = Union[int, str]
    
    for v in vs:
        assert TypeValidator.isinstance(v, typ)    

def test_list_check():
    vs = [
        [1,2,3],
        ("2","3","4")
    ]
    wrong_vs = [
        [1, "2", []]
    ]
    ts = [
        List[Union[int, str]],
        Sequence[Union[int, str]]
    ]
    for v in vs:
        for t in ts:
            assert TypeValidator.isinstance(v, t)
    
    for v in wrong_vs:
        for t in ts:
            assert not TypeValidator.isinstance(v, t)

class D(TypedDict):
    a: int
    b: str

def test_typed_dict():
    d1 = {
        "a": 1,
        "b": "2"
    }
    assert TypeValidator.isinstance(d1, D)
    d2 = {
        "a": 1,
        "b": 2
    }
    assert not TypeValidator.isinstance(d2, D)
