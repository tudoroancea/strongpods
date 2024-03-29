import re
import warnings
from enum import Enum
from typing import Optional, Union

import numpy as np
import pytest

from strongpods import PODS, VerbosityLevel, set_verbosity_level


class DummyEnum(Enum):
    E0 = 0
    E1 = 1
    E2 = 2


@PODS
class DummyParams:
    a: int
    b: str
    c: float
    d: bool
    e: np.ndarray
    f: DummyEnum
    g: Union[int, str]
    h: Optional[int]
    i: DummyEnum = DummyEnum.E0


@PODS
class SubDummyParams(DummyParams):
    j: int


default_params = {
    "a": 1,
    "b": "2",
    "c": 3.0,
    "d": True,
    "e": np.array([1, 2, 3]),
    "f": DummyEnum.E1,
    "g": 4,
    "h": 5,
    "i": DummyEnum.E2,
    "j": 6,
}


def test_no_cast_works():
    SubDummyParams(**default_params)


def test_missing_params_raises():
    params = default_params.copy()
    params.pop("a")
    params.pop("b")
    msgs = {
        "value for field a was not provided and the field is not optional and has no default value",
        "value for field b was not provided and the field is not optional and has no default value",
    }
    # first check warnings are raised
    set_verbosity_level(VerbosityLevel.WARNINGS)
    with pytest.warns(UserWarning) as record:
        DummyParams(**params)
    assert set(map(lambda x: x.message.args[0], record)) == msgs
    # then check errors are raised
    set_verbosity_level(VerbosityLevel.ERRORS)
    with pytest.raises(Exception) as e:
        DummyParams(**params)
    assert str(e.value) in msgs


def test_cast_works():
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            DummyParams(
                a="1", b=2, c="3", d="True", e=[1, 2, 3], f="E1", g=4, h=None, i="E2"
            )
    except Exception as e:
        pytest.fail(str(e))


def test_subparams_calls_superclass():
    set_verbosity_level(VerbosityLevel.WARNINGS)
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # this checks that nothing is raised
        x = SubDummyParams(**default_params)
        assert x.a == 1
    set_verbosity_level(VerbosityLevel.ERRORS)
    try:
        x = SubDummyParams(**default_params)
        assert x.a == 1
    except Exception as e:
        pytest.fail("No error should be raised here but one was: {}".format(e))


def test_impossible_cast_throws():
    set_verbosity_level(VerbosityLevel.WARNINGS)
    with pytest.warns(UserWarning) as record:
        bruh = DummyParams(
            a=[],
            b=[],
            c=[0.0],
            d=None,
            e="b",
            f=0,
            g=4.0,
            h=0.0,
            i="E3",
        )
    for r in record:
        assert (
            re.search(r"value for field \w cannot be cast to", r.message.args[0])
            is not None
        ), f'message "{r.message.args[0]}" does not match regex'
