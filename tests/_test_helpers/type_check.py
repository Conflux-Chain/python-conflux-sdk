from typing import (
    Any,
    ForwardRef,
    Type,
    Union,
)
import typing
import sys
from typing_extensions import (
    Literal,
    TypedDict, 
    get_args,
    get_origin, 
    is_typeddict,
)
import collections.abc

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
    def isinstance(val, field_type) -> bool:
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
        if get_origin(field_type) is Literal:
            return val in get_args(field_type)
        if TypeValidator._is_list_like_type(field_type):
            return all(
                TypeValidator.isinstance(v, get_args(field_type)[0])
                for v in val
            )
        if sys.version_info >= (3, 10):
            # NewType becomes a class after python3.10
            if type(field_type) == typing.NewType:
                return isinstance(val, field_type.__supertype__)
        elif type(field_type).__name__ == "function":
            return isinstance(val, field_type.__supertype__)
        if type(field_type) is type:
            # for sake of debug
            if isinstance(val, field_type):
                return True
            return False
        if type(field_type) is ForwardRef:
            return type(val).__name__ == field_type.__forward_arg__
        if type(field_type) is typing._GenericAlias: # type: ignore
            return TypeValidator.isinstance(val, get_origin(field_type))
        else:
            if isinstance(val, field_type):
                return True
            return False
            # warnings.warn("complex type check")
            # return True

    @staticmethod
    def validate_typed_dict(value_to_validate: Any, typed_dict_class: Union[str, Type[TypedDict]]):
        if isinstance(typed_dict_class, str):
            typed_dict_class = getattr(conflux_web3.types, typed_dict_class)
        assert TypeValidator.isinstance(value_to_validate, typed_dict_class)
        return True
