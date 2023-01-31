base class used to define PODS with fixed attributes with fixed types and easily accessible as attributes.

advantages over `typing.TypedDict`:

- the specified types of each attribute are enforced at initialization
- you can use inheritance mechanisms to define common set of attributes for several PODS
- the attributes are accessible as such, not via keys in a dict that you may not remember.
  This also allows the IDE to provide autocompletion.
- supports default values (defined as class attributes)

Supported types:

- any type such that the provided value can be cast to it. This means most python base
  types, data structures and user defined classes that do require more that a single value
  in their initializer
- Enums (subclasses of `enum.Enum`)
- `typing.Optional` of any type of the first kind
- `typing.Union`

Error handling behaviors: (either warnings or errors can be launched depending on a global
configuration variable).

let’s suppose we have defined a PODS `A` with an attributed `a` of type `T` and that we
initialize the instance of `A` with a dict of keyword arguments called `kwargs`

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

verbosity levels:
- 0: we never raise anything
- 1: we raise warnings
- 2: we raise errors
