from typing import (
    Any,
    Dict,
    Type,
    TypedDict, 
    get_args, 
    get_origin, 
    Union
)
import warnings
from cfx_address import Base32Address

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
            if field_type == Base32Address:
                return Base32Address.is_valid_base32(val)
            return isinstance(val, field_type)
        else:
            # TODO: do fine grained check
            warnings.warn("complex type check")
            # raise Exception("unexpected exception")
            return True
    
    @staticmethod
    def _validate_type(val, typ):
        if get_origin(typ) is Union:
            assert any(TypeValidator.isinstance(val, t)
                        for t in get_args(typ))
        else:
            assert TypeValidator.isinstance(val, typ)
    
    @staticmethod
    def validate(value_to_validate: Dict[str, Any], template: Dict[str, Any]):
        for field in template:
            assert field in value_to_validate
            field_type = template[field]
            TypeValidator._validate_type(value_to_validate[field], field_type)
    
    @staticmethod
    def validate_typed_dict(value_to_validate: Any, typed_dict_class: Union[str, Type[TypedDict]]):
        if isinstance(typed_dict_class, str):
            typed_dict_class = getattr(conflux_web3.types, typed_dict_class)
        TypeValidator.validate(value_to_validate, typed_dict_class.__annotations__)
        return True
