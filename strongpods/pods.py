# Copyright (c) 2024. Tudor Oancea
import warnings
from inspect import getmembers, isroutine
from typing import Tuple, get_args
from enum import Enum

import numpy as np

from .helpers import isoptional, isenum, isunion

__all__ = [
    "set_verbosity_level",
    "VerbosityLevel",
    "PODS_decorator",
    "is_PODS",
    "PODS",
]


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
    warning_type: type[Warning] = UserWarning,
    error_type: type[Exception] = ValueError,
):
    if __VERBOSITY_LEVEL == VerbosityLevel.WARNINGS:
        warnings.warn(msg, warning_type)
    elif __VERBOSITY_LEVEL == VerbosityLevel.ERRORS:
        raise error_type(msg)


__PODS_PREFIX = "PODS_"


def PODS_decorator(T: type):
    old_name = T.__name__
    T.__name__ = __PODS_PREFIX + old_name

    def _transform_dict(cls, di: dict) -> Tuple[dict, dict]:
        """
        Transform a dict of params only containing values with primitives types (int, float,
         bool or str) into a dict with the right types to construct an instance of a
         subclass of Params. In particular, it instantiates the Enum values from strings.

        :param cls: subclass of Params specifying the types of the params
        :param di: dict of params to be transformed
        """
        res = {}
        class_attributes = {
            k: v
            for k, v in getmembers(cls, lambda a: not (isroutine(a)))
            if not k.startswith("__")
        }  # contains the **defined** attributes and values, i.e. those that are already set,
        # i.e. those with default values
        class_annotations = (
            cls.__annotations__
        )  # contains the required attributes and types
        for param_name, param_type in class_annotations.items():
            if param_name not in di:
                if param_name not in class_attributes.keys() and not isoptional(
                    param_type
                ):
                    _log_error(
                        f"value for field {param_name} was not provided and the field is not optional and has no default value"
                    )
                # we do not set the attribute, se we have to check that the attribute really exists before using it
            else:
                # in this case we ignore the default values
                param_value = di.pop(param_name)
                if isunion(param_type):
                    all_types = get_args(param_type)
                    worked = False
                    for T in all_types:
                        if isinstance(param_value, T):
                            res[param_name] = param_value
                            worked = True
                            break
                    if not worked:
                        for T in all_types:
                            if T is not type(None):
                                try:
                                    res[param_name] = T(param_value)
                                    break
                                except ValueError as e:
                                    _log_error(
                                        f"value for field {param_name} cannot be cast to {T}, error message: {e}",
                                        error_type=TypeError,
                                    )
                            else:
                                # if it was None, it would have already been assigned
                                pass
                    continue
                if isenum(param_type):
                    if isinstance(param_value, param_type):
                        res[param_name] = param_value
                    elif isinstance(param_value, str):
                        try:
                            res[param_name] = param_type[param_value]
                        except KeyError as e:
                            _log_error(
                                f"value for field {param_name} cannot be cast to {param_type}, error message: {e}",
                            )

                    else:
                        _log_error(
                            f"value for field {param_name} cannot be cast to {param_type} or {str}",
                            error_type=TypeError,
                        )
                    continue
                else:
                    try:
                        if param_type is np.ndarray:
                            res[param_name] = np.asarray(param_value)
                        else:
                            res[param_name] = param_type(param_value)
                    except Exception as e:
                        _log_error(
                            f"value for field {param_name} cannot be cast to {param_type}, error message: {e}",
                            error_type=TypeError,
                        )
                    continue

        return res, di

    def __init__(self, **kwargs):
        current_params, remaining_params = _transform_dict(T, kwargs)
        for key, val in current_params.items():
            setattr(self, key, val)
        superclass = T.__bases__[0]
        if superclass is not object:
            superclass.__init__(self, **remaining_params)

    T.__init__ = __init__

    def __repr__(self):
        return (
            f"{old_name}("
            + ",".join([f"{k}: {v}" for k, v in self.__dict__.items() if v is not None])
            + ")"
        )

    T.__repr__ = __repr__

    return T


def is_PODS(T: type) -> bool:
    return T.__name__.startswith(__PODS_PREFIX)


class PODS:
    """
    Base class for all the parameters types needed (e.g. CarParams). You can see it as an evolution on typings.TypedDict
    that actually stores the values as class attributes instead of dict values, which lets you use PyCharm's autocomplete
    and type checking.
    Must always be instantiated with a dict of params given as keyword arguments to ensure that the required types
    are respected.

    When subclassing Params, you have to define your params but also implement the __init__ method as follows:
    >>> class MyPODS(PODS):
    >>>     a: int
    >>>     b: float
    >>>     c: str
    >>>     d: bool
    >>>     def __init__(self, **kwargs):
    >>>         current_params, remaining_params = PODS._transform_dict(kwargs)
    >>>         for key, val in current_params.items():
    >>>             setattr(self, key, val)
    >>>         super().__init__(**remaining_params)
    """

    @classmethod
    def _transform_dict(cls, di: dict) -> Tuple[dict, dict]:
        """
        Transform a dict of params only containing values with primitives types (int, float,
         bool or str) into a dict with the right types to construct an instance of a
         subclass of Params. In particular, it instantiates the Enum values from strings.

        :param cls: subclass of Params specifying the types of the params
        :param di: dict of params to be transformed
        """
        res = {}
        class_attributes = {
            k: v
            for k, v in getmembers(cls, lambda a: not (isroutine(a)))
            if not k.startswith("__")
        }  # contains the **defined** attributes and values, i.e. those that are already set,
        # i.e. those with default values
        class_annotations = (
            cls.__annotations__
        )  # contains the required attributes and types
        for param_name, param_type in class_annotations.items():
            if param_name not in di:
                if param_name not in class_attributes.keys() and not isoptional(
                    param_type
                ):
                    _log_error(
                        f"value for field {param_name} was not provided and the field is not optional and has no default value"
                    )
                # we do not set the attribute, se we have to check that the attribute really exists before using it
            else:
                # in this case we ignore the default values
                param_value = di.pop(param_name)
                if isunion(param_type):
                    all_types = get_args(param_type)
                    worked = False
                    for T in all_types:
                        if isinstance(param_value, T):
                            res[param_name] = param_value
                            worked = True
                            break
                    if not worked:
                        for T in all_types:
                            if T is not type(None):
                                try:
                                    res[param_name] = T(param_value)
                                    break
                                except ValueError as e:
                                    _log_error(
                                        f"value for field {param_name} cannot be cast to {T}, error message: {e}",
                                        error_type=TypeError,
                                    )
                            else:
                                # if it was None, it would have already been assigned
                                pass
                    continue
                if isenum(param_type):
                    if isinstance(param_value, param_type):
                        res[param_name] = param_value
                    elif isinstance(param_value, str):
                        try:
                            res[param_name] = param_type[param_value]
                        except KeyError as e:
                            _log_error(
                                f"value for field {param_name} cannot be cast to {param_type}, error message: {e}",
                            )

                    else:
                        _log_error(
                            f"value for field {param_name} cannot be cast to {param_type} or {str}",
                            error_type=TypeError,
                        )
                    continue
                else:
                    try:
                        if param_type is np.ndarray:
                            res[param_name] = np.asarray(param_value)
                        else:
                            res[param_name] = param_type(param_value)
                    except Exception as e:
                        _log_error(
                            f"value for field {param_name} cannot be cast to {param_type}, error message: {e}",
                            error_type=TypeError,
                        )
                    continue

        return res, di

    def __init__(self, **kwargs):
        """
        Initialize the instance with the given params.
        """
        pass
