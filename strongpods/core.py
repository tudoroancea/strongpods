# Copyright (c) 2024. Tudor Oancea
import warnings
from enum import Enum
from inspect import getmembers, isroutine
from typing import Tuple, Type, Union, get_args, get_origin

import numpy as np

__all__ = [
    "set_verbosity_level",
    "VerbosityLevel",
    "PODS",
    "is_PODS",
]

#####################################################################################################################
# error handling
#####################################################################################################################


class VerbosityLevel(Enum):
    SILENT = 0
    WARNINGS = 1
    ERRORS = 2


__VERBOSITY_LEVEL = VerbosityLevel.ERRORS


def set_verbosity_level(level: VerbosityLevel):
    global __VERBOSITY_LEVEL
    __VERBOSITY_LEVEL = level


def _log_error(
    msg: str,
    warning_type: Type[Warning] = UserWarning,
    error_type: Type[Exception] = ValueError,
):
    if __VERBOSITY_LEVEL == VerbosityLevel.WARNINGS:
        warnings.warn(msg, warning_type)
    elif __VERBOSITY_LEVEL == VerbosityLevel.ERRORS:
        raise error_type(msg)


#####################################################################################################################
# type deduction helpers
#####################################################################################################################


def _is_optional(t: type) -> bool:
    return get_origin(t) is Union and type(None) in get_args(t)


def _is_enum(t: type) -> bool:
    try:
        return issubclass(t, Enum)
    except TypeError:
        return False


def _is_union(t: type) -> bool:
    return get_origin(t) is Union


#####################################################################################################################
# core
#####################################################################################################################

__PODS_PREFIX = "PODS_"


def __transform_dict(cls, kwargs: dict) -> Tuple[dict, dict]:
    res = {}
    attributes_with_default_values = {
        k: v
        for k, v in getmembers(cls, lambda a: not (isroutine(a)))
        if not k.startswith("__")
    }  # contains the **defined** attributes and values, i.e. those that are already set,
    # i.e. those with default values
    class_annotations = (
        cls.__annotations__
    )  # contains the required attributes and types
    for attribute_name, attribute_type in class_annotations.items():
        if attribute_name not in kwargs:
            if attribute_name not in attributes_with_default_values.keys():
                if _is_optional(attribute_type):
                    res[attribute_name] = None
                else:
                    _log_error(
                        f"value for field {attribute_name} was not provided and the field is not optional and has no default value",
                        error_type=ValueError,
                    )
            # we do not set the attribute, se we have to check that the attribute really exists before using it
        else:
            # in this case we ignore the default values
            param_value = kwargs.pop(attribute_name)
            if _is_union(attribute_type):
                possible_attribute_types = get_args(attribute_type)
                if (
                    len(possible_attribute_types) == 2
                    and type(None) in possible_attribute_types
                ):
                    # we treat it as an optional
                    if param_value is None:
                        res[attribute_name] = None
                    else:
                        other_type = (
                            possible_attribute_types[0]
                            if possible_attribute_types[1] is type(None)
                            else possible_attribute_types[1]
                        )
                        try:
                            res[attribute_name] = other_type(param_value)
                        except ValueError as e:
                            _log_error(
                                f"value for field {attribute_name} cannot be cast to {other_type}, error message: {e}",
                                error_type=TypeError,
                            )
                elif type(None) in possible_attribute_types:
                    _log_error(
                        "We don't support types of the form Union[None, ...] that are not optionals.",
                        error_type=NotImplementedError,
                    )
                else:
                    # we treat it as a union
                    # first we check if the value has any of the types of the Union. If it doesn't, we
                    # try to coerce it to one of the types, and stop as soon as we could do it.
                    # This means that for a field of type Union[str, float] and a value of 0,
                    # the attribute will be initialized with type str.
                    coerced_to_type = False
                    for T in possible_attribute_types:
                        if isinstance(param_value, T):
                            res[attribute_name] = param_value
                            coerced_to_type = True
                            break
                    if not coerced_to_type:
                        for T in possible_attribute_types:
                            # NOTE: we can't have T == type(None) here, because the case was treated in the first if (for optionals)
                            try:
                                res[attribute_name] = T(param_value)
                                break
                            except ValueError as e:
                                _log_error(
                                    f"value for field {attribute_name} cannot be cast to {T}, error message: {e}",
                                    error_type=TypeError,
                                )
            elif _is_enum(attribute_type):
                # TODO: add possibility to cast from int
                if isinstance(param_value, attribute_type):
                    res[attribute_name] = param_value
                elif isinstance(param_value, str):
                    try:
                        res[attribute_name] = attribute_type[param_value]
                    except KeyError as e:
                        _log_error(
                            f"value for field {attribute_name} cannot be cast to {attribute_type}, error message: {e}",
                            error_type=KeyError,
                        )
                else:
                    _log_error(
                        f"value for field {attribute_name} cannot be cast to {attribute_type} or {str}",
                        error_type=TypeError,
                    )
            else:
                try:
                    if attribute_type is np.ndarray:
                        res[attribute_name] = np.asarray(param_value)
                    else:
                        res[attribute_name] = attribute_type(param_value)
                except Exception as e:
                    _log_error(
                        f"value for field {attribute_name} cannot be cast to {attribute_type}, error message: {e}",
                        error_type=TypeError,
                    )

    return res, kwargs


def PODS(T: type):
    old_name = T.__name__
    T.__name__ = __PODS_PREFIX + old_name

    def __init__(self, **kwargs):
        current_params, remaining_params = __transform_dict(T, kwargs)
        for key, val in current_params.items():
            setattr(self, key, val)
        superclass = T.__bases__[0]
        if superclass is not object:
            superclass.__init__(self, **remaining_params)

    T.__init__ = __init__

    def __repr__(self):
        return (
            f"{old_name}("
            + ",".join([f"{k}={v}" for k, v in self.__dict__.items() if v is not None])
            + ")"
        )

    T.__repr__ = __repr__

    return T


def is_PODS(T: type) -> bool:
    return T.__name__.startswith(__PODS_PREFIX)
