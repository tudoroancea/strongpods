# strongpods

[![Python test and build](https://github.com/tudoroancea/strongpods/actions/workflows/python.yml/badge.svg)](https://github.com/tudoroancea/strongpods/actions/workflows/python.yml)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>

`strongpods` is a tiny and simple library for _Strongly typed Plain Old Data Structures_.

Using it you can create a simple PODS using a decorator and C-style attribute declaration using type annotations:

```python
from strongpods import PODS

@PODS
class MyPODS:
    an_int: int
    a_list: list
```

You can then initialize it using keyword arguments and an error will be emitted (see section [strongpods errors](#strongpods-errors)) if the provided values don't have the specified typed and cannot be cast to these types.

```python
pods_instance = MyPODS(an_int=127, a_str="brains") # works
pods_instance_2 = MyPODS(an_int="an irrational number", a_str="brains") # raises a TypeError because an_int cannot be converted to an int
pods_instance_3 = MyPODS(an_int="an irrational number", a_str="brains") # raises a TypeError because an_int cannot be converted to an int
```

## Installation

```bash
pip3 install git+https://github.com/tudoroancea/strongpods.git@v2.0.0#egg=strongpods
```

## Main features

`strongpods` relies on the type annotations of the attributes to enforce the types at runtime.
If a given value can be cast to it (using the type casting rules described [below](#type-casting-rules)), it will, otherwise an error will be emitted (see section [strongpods errors](#strongpods-errors) for more details).
The following types are supported:

- primitive types
- numpy arrays
- enumerations
- unions
- optionals (which are special types of unions)

One can also define default values for attributes.

The PODS defined with `strongpods` can also be subclassed and the attributes of the parent class will be inherited by the child class, while still maintaining the type enforcement.


```python
from strongpods import PODS
@PODS
class ParentPODS:
    an_int: int
    a_list: list
class ChildPODS(ParentPODS):
    a_str: str
```

## Type casting rules

Suppose we have defined a PODS as
```python
@PODS
class MyPODS:
  attr: Typ
```
and try to construct an instance of `MyPODS` using `MyPODS(attr=val)` using a value `val` **which is not of type `Typ`**.
- If `Typ` is an enumeration, we can convert `val` if it is a string representing a member of the enumeraion. For example, if we defined
  ```python
  class Typ(Enum):
    Typ0 = 0
    Typ1 = 1
    Typ2 = 2
  ```
  then we can provide the following are valid
  ```python
  MyPODS(attr="Typ0")
  MyPODS(attr="Typ1")
  MyPODS(attr="Typ2")
  ```
- If `Typ` is an union, we first check if the provided value has the exact type of any of the types of the union, and if does not, we cast it to the first type it can be cast to.
  For the following PODS
  ```
  @PODS
  class MyPODS:
    a: Union[int, str]
  ```
  the intialization `MyPODS(a="hello")` initializes `a` with type `str` (the actual type of `"hello"`) and `MyPODS(a=0.0)` initializes it with type `int` (and value `0`).

## `strongpods` errors

The way the errors are handled depends on the value of the global parameter
`strongpods.VERBOSITY_LEVEL`:

- 0: all errors are ignored
- 1: warnings are raised via `warnings.warn`
- 2: errors are raised

You can manually change this value at any time in your code with
`strongpods.set_verbosity_level()`.

Here are the cases where an error can be raised: let’s suppose we have defined a PODS `A`
with an attributed `a` of type `T` and that we initialize the instance of `A` with a dict
of keyword arguments called `kwargs`

- if a value for `a` is not present in `kwargs` **and** `a` not have a default value
  **and** `T` is not an Optional, a warning/error is raised
- if we cannot create an instance of `T` with the value `kwargs["a"]` , a warning/error is
  raised. The following specific cases are considered:
  - if `T` is an Enum and `kwargs["a"]` is not an instance of this enum and cannot be
    cast to `str`
  - if `T` is `Optional[U]` and `kwargs["a"]` cannot be cast to `U`
  - if `T` is `Union[U,...]` and `kwargs["a"]` cannot be cast to `U` or any other type in
    the union
  - in all other cases, if the cast `T(kwargs["a"])` fails
- if no default value was set for `a` and no value cannot be created from `kwargs["a"]`,
  we do not set the attribute `a` in the instance of `A`.
