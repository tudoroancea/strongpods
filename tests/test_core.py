from enum import Enum
from typing import Optional, Union

import numpy as np
import pytest

from strongpods import (
    PODS,
    VerbosityLevel,
    is_PODS,
    set_verbosity_level,
)
from strongpods.core import (
    _is_enum,
    _is_optional,
    _is_union,
    _log_error,
)

set_verbosity_level(VerbosityLevel.ERRORS)


class TestUnspecifiedKWArgs:
    def test_not_optional_no_default_value(self):
        @PODS
        class T:
            a: int

        with pytest.raises(ValueError):
            T()

    def test_not_optional_with_default_value(self):
        @PODS
        class T:
            a: int = 2

        try:
            t = T()
            assert t.a == 2
        except ValueError as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_optional_no_default_value(self):
        @PODS
        class T:
            a: Optional[int]

        try:
            t = T()
            assert t.a is None
        except ValueError as e:
            pytest.fail(f"Unexpected error: {e}")

    def test_optional_with_default_value(self):
        @PODS
        class T:
            a: Optional[int] = 2

        try:
            t = T()
            assert t.a == 2
        except ValueError as e:
            pytest.fail(f"Unexpected error: {e}")


class TestOptionalType:
    def test_optional_type_none_value(self):
        @PODS
        class T:
            a: Optional[int]

        t = T(a=None)
        assert t.a is None

    def test_optional_type_convertable_value(self):
        @PODS
        class T:
            a: Optional[int]

        t = T(a="2")
        assert isinstance(t.a, int)
        assert t.a == 2

    def test_optional_type_unconvertable_value(self):
        @PODS
        class T:
            a: Optional[int]

        with pytest.raises(TypeError):
            T(a="a")


class TestUnionType:
    def test_union_with_none_type_and_more_than_one_type(self):
        @PODS
        class T:
            a: Union[None, int, str]

        with pytest.raises(NotImplementedError):
            T(a=None)

    # TODO: rename this test.
    def test_union_1(self):
        @PODS
        class T:
            a: Union[int, float, str]

        t1 = T(a=2)
        assert isinstance(t1.a, int)
        assert t1.a == 2
        t2 = T(a=2.0)
        assert isinstance(t2.a, float)
        assert np.isclose(t2.a, 2.0, rtol=1e-09, atol=1e-09)
        t3 = T(a="2")
        assert isinstance(t3.a, str)
        assert t3.a == "2"

    # TODO: rename this test.
    def test_union_2(self):
        @PODS
        class T:
            a: Union[int, str]

        t1 = T(a=2.0)
        assert isinstance(t1.a, int)
        assert t1.a == 2

    # TODO: rename this test.
    def test_union_3(self):
        @PODS
        class T:
            a: Union[int, float]

        with pytest.raises(TypeError):
            T(a="hello")


class TestEnumType:
    class E(Enum):
        E0 = 0
        E1 = 1

    def test_enum_1(self):
        @PODS
        class T:
            a: TestEnumType.E

        t = T(a=TestEnumType.E.E0)
        assert isinstance(t.a, TestEnumType.E)
        assert t.a == TestEnumType.E.E0

    def test_enum_from_string(self):
        @PODS
        class T:
            a: TestEnumType.E

        t0 = T(a="E0")
        assert isinstance(t0.a, TestEnumType.E)
        assert t0.a == TestEnumType.E.E0
        t1 = T(a="E1")
        assert isinstance(t1.a, TestEnumType.E)
        assert t1.a == TestEnumType.E.E1
        with pytest.raises(KeyError):
            T(a="E2")

    def test_enum_3(self):
        @PODS
        class T:
            a: TestEnumType.E

        with pytest.raises(TypeError):
            T(a=2)


class TestPrimitiveType:
    def test_int(self):
        @PODS
        class T:
            a: int

        t = T(a="2")
        assert isinstance(t.a, int)
        assert t.a == 2

    def test_float(self):
        @PODS
        class T:
            a: float

        t = T(a="2.0")
        assert isinstance(t.a, float)
        assert np.isclose(t.a, 2.0, rtol=1e-09, atol=1e-09)

    def test_bool(self):
        @PODS
        class T:
            a: bool

        t = T(a="True")
        assert isinstance(t.a, bool)
        assert t.a

    def test_str(self):
        @PODS
        class T:
            a: str

        t = T(a=2)
        assert isinstance(t.a, str)
        assert t.a == "2"

    def test_tuple(self):
        @PODS
        class T:
            a: tuple

        t = T(a=[1, 2, 3])
        assert isinstance(t.a, tuple)
        assert t.a == (1, 2, 3)

    def test_list(self):
        @PODS
        class T:
            a: list

        t = T(a=(1, 2, 3))
        assert isinstance(t.a, list)
        assert t.a == [1, 2, 3]


class TestNumpyType:
    def test_numpy(self):
        @PODS
        class T:
            a: np.ndarray

        t = T(a=[1, 2, 3])
        assert isinstance(t.a, np.ndarray)
        assert np.array_equal(t.a, np.array([1, 2, 3]))
        t = T(a=(1, 2, 3))
        assert isinstance(t.a, np.ndarray)
        assert np.array_equal(t.a, np.array([1, 2, 3]))
        t = T(a=np.arange(1, 4))
        assert isinstance(t.a, np.ndarray)
        assert np.array_equal(t.a, np.array([1, 2, 3]))


class TestSubclassing:
    def test_subclassing(self):
        @PODS
        class T:
            a: int

        @PODS
        class T2(T):
            b: str

        t = T2(a=2, b="hello")
        assert t.a == 2
        assert t.b == "hello"


class TestStringRepresentation:
    def test_string_representation(self):
        @PODS
        class T:
            a: int

        t = T(a=2)
        assert str(t) == "T(a=2)"


def test_is_pods():
    @PODS
    class T:
        a: int

    class T2:
        a: int

    assert is_PODS(T)
    assert not is_PODS(T2)


class TestVerbosityLevel:
    def test_warn(self):
        set_verbosity_level(VerbosityLevel.WARNINGS)
        with pytest.warns(UserWarning):
            _log_error("warning", warning_type=UserWarning)
        with pytest.warns(RuntimeWarning):
            _log_error("warning", warning_type=RuntimeWarning)

        @PODS
        class T:
            a: int

        with pytest.warns(UserWarning):
            T(a="a")

    def test_error(self):
        set_verbosity_level(VerbosityLevel.ERRORS)
        with pytest.raises(ValueError):
            _log_error("error", error_type=ValueError)
        with pytest.raises(TypeError):
            _log_error("error", error_type=TypeError)

        @PODS
        class T:
            a: int

        with pytest.raises(TypeError):
            T(a="a")


class TestTypeDeductionHelpers:
    def test_is_optional(self):
        assert _is_optional(Optional[int])
        assert _is_optional(Union[int, None])
        assert _is_optional(int | None)
        assert not _is_optional(int)
        assert not _is_optional(127)

    def test_is_enum(self):
        class E(Enum):
            E0 = 0
            E1 = 1

        assert _is_enum(E)
        assert not _is_enum(int)
        assert not _is_enum(127)

    def test_is_union(self):
        assert _is_union(Union[int, str])
        assert not _is_union(int)
        assert _is_union(Optional[int])
        assert not _is_union(127)
