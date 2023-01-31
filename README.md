# strongpods
[![Python test and build](https://github.com/tudoroancea/strongpods/actions/workflows/python.yml/badge.svg)](https://github.com/tudoroancea/strongpods/actions/workflows/python.yml)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"/></a>

The name stands for _Strongly Typed PODS_ (Plain Old Data Structures).
This library offers a simple and robust alternative to `typing.TypedDict` to define PODS.
You can define them easily by subclassing `strongpods.PODS` and specifying the attributes:
```python
from strongpods import PODS

class MyPODS(PODS):
    a: int
    b: str
    c: float = 0.0

my_pods = MyPODS(a=1, b="2")
print(my_pods.a, my_pods.b, my_pods.c)
```

`strongpods.PODS` has the following advantages over `typing.TypedDict`:
- the specified types of each attribute are enforced at initialization
- you can use inheritance mechanisms to define common set of attributes for several PODS
- the attributes are accessible as such, not via keys in a dict that you may not remember.
  This also allows IDEs to provide autocompletion.
- supports default values (defined as class attributes)

It supports a variety of types that are correctly handled as assured by CI tests:
- any type such that the provided value can be cast to it. This means most python base
  types, data structures and user defined classes that do require more that a single value
  in their initializer
- Enums (subclasses of `enum.Enum`)
- `typing.Optional` of any type of the first kind
- `typing.Union`

## Installation
```bash
pip3 install git+https://github.com/tudoroancea/strongpods.git@main#egg=strongpods
```

## Usage
### Error handling behaviors
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
