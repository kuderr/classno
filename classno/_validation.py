import collections
import contextlib
import types
import typing as t

from classno import _errors
from classno import exceptions as excs


def validate_fields(obj):
    fields = obj.__fields__
    errors = []

    for field in fields.values():
        attr = getattr(obj, field.name)
        try:
            validate_value_hint(attr, field.hint)
        except TypeError:
            errors.append(
                _errors.ErrorFormatter.validation_error(field.name, field.hint, attr)
            )

    if errors:
        raise excs.ValidationError(errors)


def validate_dict(value, hint):
    args = t.get_args(hint)
    if len(args) == 2:
        keys_type, val_type = args
    elif len(args) == 1:
        # Counter[str] only has key type, values are always int
        keys_type = args[0]
        val_type = int
    else:
        # No type args, accept any
        return

    for key in value:
        if not isinstance(key, keys_type):
            raise TypeError

    for val in value.values():
        validate_value_hint(val, val_type)


def validate_collection(value, hint):
    tp, *_ = t.get_args(hint)
    for el in value:
        validate_value_hint(el, tp)


def validate_tuple(value, hint):
    tps = t.get_args(hint)
    if len(tps) == 2 and tps[-1] is Ellipsis:
        tp = tps[0]
        for el in value:
            validate_value_hint(el, tp)
        return

    if len(tps) != len(value):
        raise TypeError

    for tp, val in zip(tps, value):
        validate_value_hint(val, tp)


def validate_frozenset(value, hint):
    """Validate frozenset types."""
    tp, *_ = t.get_args(hint)
    for el in value:
        validate_value_hint(el, tp)


def validate_deque(value, hint):
    """Validate collections.deque types."""
    tp, *_ = t.get_args(hint)
    for el in value:
        validate_value_hint(el, tp)


VALIDATION_ORIGIN_HANDLER = {
    dict: validate_dict,
    list: validate_collection,
    set: validate_collection,
    tuple: validate_tuple,
    frozenset: validate_frozenset,
    collections.deque: validate_deque,
    # Dict-like collections can reuse the dict validator
    collections.defaultdict: validate_dict,
    collections.OrderedDict: validate_dict,
    collections.Counter: validate_dict,
}


def validate_forward_ref(value, hint):
    """Validate a ForwardRef type.

    ForwardRefs are used for circular/self-referential type hints.

    Args:
        value: Value to validate
        hint: ForwardRef type hint

    Raises:
        TypeError: If value doesn't match the forward reference
    """
    # For ForwardRef, we need to check if the value is an instance of a class
    # with the same name as the forward reference
    expected_name = hint.__forward_arg__
    if hasattr(value, "__class__"):
        actual_name = value.__class__.__name__
        if actual_name == expected_name:
            return  # Valid ForwardRef match
    raise TypeError


def validate_union(value, hint):
    """Validate a Union type.

    Handles Optional[T] and Union[T1, T2, ...] types.

    Args:
        value: Value to validate
        hint: Union type hint

    Raises:
        TypeError: If value doesn't match any type in the Union
    """
    for sub_hint in t.get_args(hint):
        with contextlib.suppress(TypeError):
            validate_value_hint(value, sub_hint)
            return
    raise TypeError


def validate_simple_type(value, hint):
    """Validate a simple (non-generic) type.

    Handles primitives like int, str, bool, and custom classes.

    Args:
        value: Value to validate
        hint: Target type hint

    Raises:
        TypeError: If value doesn't match the target type
    """
    if not isinstance(value, hint):
        raise TypeError


def validate_with_origin(value, hint, origin):
    """Validate a generic type with origin.

    Handles types like List[int], Dict[str, int], Set[str], etc.

    Args:
        value: Value to validate
        hint: Generic type hint
        origin: Origin type (e.g., list, dict, set)

    Raises:
        TypeError: If value doesn't match the target type
    """
    # First check if value is the correct origin type
    if not isinstance(value, origin):
        raise TypeError

    # Then validate the inner elements
    handler = VALIDATION_ORIGIN_HANDLER.get(origin)
    if handler:
        handler(value, hint)
    else:
        # Fallback for unknown collection types
        # If it's iterable but not str/bytes, try to validate as collection
        if hasattr(origin, "__iter__") and not issubclass(origin, (str, bytes)):
            validate_collection(value, hint)
        else:
            raise TypeError(_errors.ErrorFormatter.validation_no_handler(origin))


def validate_value_hint(value, hint):
    """Main dispatcher for validating values against type hints.

    Args:
        value: Value to validate
        hint: Target type hint

    Raises:
        TypeError: If value doesn't match the target type
    """
    # Handle ForwardRef (circular/self-referential types)
    if isinstance(hint, t.ForwardRef):
        return validate_forward_ref(value, hint)

    origin = t.get_origin(hint)

    # Handle Union types (including Optional)
    if isinstance(hint, types.UnionType) or origin is t.Union:
        return validate_union(value, hint)

    # Handle simple types (no generic origin)
    if not origin:
        return validate_simple_type(value, hint)

    # Handle generic types with origin (List[int], Dict[str, int], etc.)
    return validate_with_origin(value, hint, origin)
