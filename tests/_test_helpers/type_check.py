from typing import (
    Any,
    Dict, 
    get_args, 
    get_origin, 
    Union
)
import warnings
from conflux_web3.types import (
    EstimateResult,
    TxDict,
    TxData,
    TxReceipt
)
import conflux_web3.types

class TypeValidator:
    """
    use TypedDict.__annotations__ to check type

    >> from typing import Union, get_origin, get_args
    >> x = Union[int, str]
    >> get_origin(x), get_args(x)
    (typing.Union, (<class 'int'>, <class 'str'>))
    >> get_origin(x) is Union
    True
    >> get_args(int)
    ()
    >> isinstance(3, get_args(x))
    True
    >> isinstance('a', get_args(x))
    True
    >> isinstance([], get_args(x))
    False
    """
    @staticmethod
    def isinstance(val, field_type):
        if type(field_type).__name__ == "function":
            return isinstance(val, field_type.__supertype__)
        elif type(field_type) is type:
            return isinstance(val, field_type)
        else:
            # TODO: do fine grained check
            warnings.warn("complex type check")
            # raise Exception("unexpected exception")
            return True
            
    
    @staticmethod
    def validate(value_to_validate: Dict[str, Any], template: Dict[str, Any]):
        for field in template:
            assert field in value_to_validate
            field_type = template[field]
            if get_origin(field_type) is Union:
                assert any(TypeValidator.isinstance(value_to_validate[field], t)
                           for t in get_args(field_type))
                # for t in get_args(field_type):
                #     TypeValidator.isinstance(value_to_validate[field], t)
            else:
                assert TypeValidator.isinstance(value_to_validate[field], field_type)
    
    @staticmethod
    def validate_typed_dict(value_to_validate: Any, typed_dict_name: str):
        TypeValidator.validate(value_to_validate, getattr(conflux_web3.types, typed_dict_name).__annotations__)
        
    @staticmethod
    def validate_tx(value_to_validate):
        TypeValidator.validate(value_to_validate, TxDict.__annotations__)
        
    @staticmethod
    def validate_estimate(value_to_validate):
        TypeValidator.validate(value_to_validate, EstimateResult.__annotations__)
        
    @staticmethod
    def validate_receipt(value_to_validate):
        TypeValidator.validate(value_to_validate, TxReceipt.__annotations__)
    
    @staticmethod
    def validate_tx_data(value_to_validate):
        TypeValidator.validate(value_to_validate, TxData.__annotations__)
        