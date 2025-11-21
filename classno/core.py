import copy
import functools
import typing as t

from classno import _fields
from classno import _hooks
from classno import constants as c


def _prepare_slots_for_class(attrs: dict, bases: tuple) -> dict:
    """
    Prepare slots configuration for a class during metaclass creation.

    This function handles the setup of __slots__ for classes that use the SLOTS
    feature. It collects field names from annotations and moves default values
    to a separate _field_defaults dictionary to avoid conflicts with __slots__.

    Args:
        attrs: Class attributes dictionary being processed by metaclass
        bases: Base classes tuple

    Returns:
        Modified attrs dictionary with slots and field defaults prepared

    Notes:
        - Slots are inherited: if any parent has SLOTS, child classes must handle it
        - Field defaults must be stored separately when using __slots__
        - Internal Classno attributes are excluded from slots
    """
    features = attrs.get("__features__", c.Features.DEFAULT)

    # Check if any base class has slots feature enabled
    parent_has_slots = any(
        hasattr(base, "__features__") and c.Features.SLOTS in base.__features__
        for base in bases
        if hasattr(base, "__features__")
    )

    # Enable slots if current class or any parent has slots
    if c.Features.SLOTS not in features and not parent_has_slots:
        return attrs

    # Get annotations from current class
    annotations = attrs.get("__annotations__", {})

    # Collect field names (excluding classno internal attributes)
    field_names = []
    # Store default values to move them out of attrs for slots compatibility
    field_defaults = {}

    for field_name in annotations:
        if field_name not in c._CLASSNO_ATTRS:
            field_names.append(field_name)
            # If there's a default value, store it and remove from attrs
            if field_name in attrs:
                field_defaults[field_name] = attrs[field_name]
                del attrs[field_name]

    # Only set __slots__ if we have fields and it's not already set
    if field_names and "__slots__" not in attrs:
        attrs["__slots__"] = tuple(field_names)
        # Store the field defaults for later use
        attrs["_field_defaults"] = field_defaults

    return attrs


class MetaClassno(type):
    def __new__(cls, name, bases, attrs):
        # Handle slots feature before class creation
        attrs = _prepare_slots_for_class(attrs, bases)

        klass = super().__new__(cls, name, bases, attrs)
        klass.__set_fields_hook__(klass)
        klass.__process_cls_features_hook__(klass)
        return klass

    # Called on SubClassno(...)
    def __call__(cls, *args, **kwargs):
        # def __init__ is called here
        obj = type.__call__(cls, *args, **kwargs)
        # Process object fields data and __init__ input
        cls.__init_hook__(obj, *args, **kwargs)

        cls.__process_obj_features_hook__(obj)
        obj.__post__init__(*args, **kwargs)
        return obj


class Classno(metaclass=MetaClassno):
    """
    Base class for creating data classes with powerful features.

    Classno provides a rich set of features for data modeling including:
    - Type validation
    - Immutability (frozen objects)
    - Private fields
    - Automatic type casting
    - Custom comparison behavior
    - Slots optimization

    Example:
        ```python
        from classno import Classno, Features

        class User(Classno):
            __features__ = Features.VALIDATION | Features.FROZEN

            name: str
            age: int
            email: str = "user@example.com"

        user = User(name="John", age=30)
        ```

    Class Attributes:
        __fields__: Dictionary of Field objects for this class
        __features__: Feature flags controlling behavior
        __eq_keys__: Tuple of field names used in equality comparison
        __hash_keys__: Tuple of field names used in hashing
        __order_keys__: Tuple of field names used in ordering
    """

    # Add empty __slots__ to prevent __dict__ in child classes that use slots
    __slots__ = ()

    __fields__: t.ClassVar[dict[str, _fields.Field]] = {}
    __features__: t.ClassVar[c.Features] = c.Features.DEFAULT

    __eq_keys__: t.ClassVar[tuple[str, ...]] = ()
    __hash_keys__: t.ClassVar[tuple[str, ...]] = ()
    __order_keys__: t.ClassVar[tuple[str, ...]] = ()

    __init_hook__ = _hooks.init_obj
    __set_fields_hook__ = _hooks.set_fields
    __process_cls_features_hook__ = _hooks.process_cls_features
    __process_obj_features_hook__ = _hooks.process_obj_features

    def __init__(self, *args, **kwargs) -> None: ...
    def __post__init__(self, *args, **kwargs) -> None: ...

    def as_dict(self):
        """
        Convert the object to a dictionary representation.

        Returns:
            dict: Dictionary mapping field names to their values
        """
        return {f.name: getattr(self, f.name) for f in self.__fields__.values()}

    def as_kwargs(self):
        """
        Convert the object to a kwargs-style string representation.

        Returns:
            str: String representation suitable for debugging, showing all fields
                 (except private fields if PRIVATE feature is enabled)
        """
        items = self.as_dict().items()
        # Filter out private fields if PRIVATE feature is enabled
        if c.Features.PRIVATE in self.__features__:
            items = [(k, v) for k, v in items if not k.startswith("_")]
        return ", ".join(f"{k!s}={v!r}" for k, v in items)

    def __copy__(self):
        return type(self)(**self.as_dict())

    def __deepcopy__(self, memo):
        return type(self)(
            **{k: copy.deepcopy(v, memo) for k, v in self.as_dict().items()}
        )

    def __reduce__(self) -> tuple[t.Any, ...]:
        return functools.partial(self.__class__, **self.as_dict()), tuple()
