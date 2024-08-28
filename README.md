# strongpods

`strongpods` is a tiny and simple library for _Strongly typed Plain Old Data Structures (PODS)_.

Using it you can create a simple PODS using a decorator and C-style attribute declaration using type annotations:

```python
from strongpods import PODS

@PODS
class MyPODS:
    an_int: int
    a_list: list
```

You can then initialize it using keyword arguments and an error will be emitted if the provided values don't have the specified typed and cannot be cast to these types.
See the [Error reporting](#error-reporting) section for more details.

```python
pods_instance = MyPODS(an_int=127, a_list=["brains"]) # works
pods_instance_2 = MyPODS(an_int="an irrational number", a_list=["brains"]) # raises a TypeError because "an irrational number" cannot be converted to an int
pods_instance_3 = MyPODS(an_int=127, a_list="brains") # raises a TypeError because "brains" cannot be converted to a list
```

## Installation

Using pip:

```bash
pip3 install strongpods
```

or using [uv](https://docs.astral.sh/uv/) (recommended):

```bash
uv pip install strongpods
```

## Main features

`strongpods` relies on type annotations of the attributes to enforce the types at runtime.
If a given value can be cast to it (using the type casting rules described [below](#type-casting-rules)), it will, otherwise an error will be emitted (see section [strongpods errors](#strongpods-errors) for more details).
The following types are supported:

- primitive types
- numpy arrays
- enumerations
- unions
- optionals (which are special types of unions)

One can also define default values for attributes.

The PODS defined with `strongpods` can also be subclassed and the attributes of the parent class will be inherited by the child class, while still maintaining the type enforcement at runtime.

```python
from strongpods import PODS

@PODS
class ParentPODS:
    an_int: int
    a_list: list

@PODS
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

and try to construct an instance of `MyPODS` using `MyPODS(attr=val)`.
If `val` is of type `Typ`, the attribute `attr` will be initialized with the value `val`.
Otherwise, `strongpods` will try to cast `val` to `Typ` using the following rules:

- If `Typ` is a simple type (e.g. `int`, `str`, `float`, `bool`, `list`, `tuple` or `np.ndarray`), the type cast will be performed using `Typ(val)`.
- If `Typ` is an enumeration, we can convert `val` if it is a string representing a member of the enumeraion. For example, if we defined
  ```python
  class Typ(Enum):
    Typ0 = 0
    Typ1 = 1
    Typ2 = 2
  ```
  then the following are valid
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

## Error reporting

The way the errors are handled depends on the value of the global parameter
`strongpods.VERBOSITY_LEVEL` of type `strongpods.VerbosityLevel`:

- `SILENT`: all errors are ignored
- `WARNINGS`: warnings are raised via `warnings.warn`
- `ERRORS`: exceptions are raised

You can manually change this value at any time in your code with
`strongpods.set_verbosity_level()`.

## Alternatives

I created this package around 2022, when I started working at the [EPFL Racing Team](https://epflracingteam.ch/en/) on big Python projects (an autonomous racing software stack).
I wanted to create simple data structures to encapsulate input/output data in a safe and simple way. I didn't like the idea of using plain dicts and relying on my
memory to remember the exact name of the keys, so I started looking into dedicated solutions, part of the Python standard library. Neither
[`dataclasses`](https://docs.python.org/3/library/dataclasses.html#module-dataclasses), [`TypedDicts`](https://docs.python.org/3/library/typing.html#typing.TypedDict)
nor [`NamedTuples`](https://docs.python.org/3/library/typing.html#typing.NamedTuple) seemed to fit my needs, mainly because of their lack of strong typing that I missed
from C and C++.
At the time, the simplest solution for me was to write my own small library. I since discovered other mainstream alternatives, such as
[pydantic](https://docs.pydantic.dev/latest/). Comparatively, this project offers substantially fewer options and a more limited and opinionated set of supported types.
One important example is the direct support for numpy arrays, which was of great use in my projects.
It is not designed to rival with pydantic, but rather to be a simple and lightweight alternative that suits my needs.
