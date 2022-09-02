from typing import (
    Any,
    Type,
    TypedDict, 
    get_args, 
    get_origin, 
    Union
)
from typing_extensions import (
    is_typeddict,
)
import collections.abc
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
    def _is_list_like_type(typ):
        return any(
            [
                get_origin(typ) == collections.abc.Sequence,
                get_origin(typ) == list
            ]
        )
    
    @staticmethod
    def isinstance(val, field_type):
        if is_typeddict(field_type):
            annotations = field_type.__annotations__
            for key, sub_field_type in annotations.items():
                if key not in val:
                    return False
                if not TypeValidator.isinstance(val[key], sub_field_type):
                    return False
            return True
        if get_origin(field_type) is Union:
            return any(TypeValidator.isinstance(val, t)
                        for t in get_args(field_type))
        elif TypeValidator._is_list_like_type(field_type):
            return all(
                TypeValidator.isinstance(v, get_args(field_type)[0])
                for v in val
            )
        elif type(field_type).__name__ == "function":
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
    def validate_typed_dict(value_to_validate: Any, typed_dict_class: Union[str, Type[TypedDict]]):
        if isinstance(typed_dict_class, str):
            typed_dict_class = getattr(conflux_web3.types, typed_dict_class)
        assert TypeValidator.isinstance(value_to_validate, typed_dict_class)
        return True
