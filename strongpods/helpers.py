# Copyright (c) Tudor Oancea, 2023

from enum import Enum
from typing import get_origin, Union, get_args


def isoptional(t) -> bool:
    try:
        return get_origin(t) is Union and type(None) in get_args(t)
    except TypeError:
        return False


def isenum(t) -> bool:
    try:
        return issubclass(t, Enum)
    except TypeError:
        return False


def isunion(t) -> bool:
    try:
        return get_origin(t) is Union
    except TypeError:
        return False
