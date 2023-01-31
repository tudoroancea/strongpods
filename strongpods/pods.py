# Copyright (c) 2023. Tudor Oancea EPFL Racing Team Driverless
import warnings
from inspect import getmembers, isroutine
from typing import Tuple, get_args, Union

from .helpers import isoptional, isenum, isunion

__all__ = ["PODS", "set_verbosity_level", "VERBOSITY_LEVEL"]


VERBOSITY_LEVEL = 1


def set_verbosity_level(level: int):
    global VERBOSITY_LEVEL
    assert level in [0, 1, 2], "Verbosity level must be 0, 1 or 2"
    VERBOSITY_LEVEL = level


def msg(
    msg: str,
    warning_type=UserWarning,
    error_type=ValueError,
):
    if VERBOSITY_LEVEL == 1:
        warnings.warn(msg, warning_type)
    elif VERBOSITY_LEVEL == 2:
        raise error_type(msg)


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
                    msg(
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
                                    msg(
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
                            msg(
                                f"value for field {param_name} cannot be cast to {param_type}, error message: {e}",
                            )

                    else:
                        msg(
                            f"value for field {param_name} cannot be cast to {param_type} or {str}",
                            error_type=TypeError,
                        )
                    continue
                else:
                    try:
                        res[param_name] = param_type(param_value)
                    except Exception as e:
                        msg(
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
