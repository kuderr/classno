import enum


class MissingType: ...


MISSING = MissingType

_CLASSNO_EQ_KEYS_ATTR = "__eq_keys__"
_CLASSNO_HASH_KEYS_ATTR = "__hash_keys__"
_CLASSNO_ORDER_KEYS_ATTR = "__order_keys__"
_CLASSNO_ATTRS = {
    "__features__",
    "__fields__",
    "__init_hook__",
    "__set_keys_hook__",
    "__set_fields_hook__",
    "__process_cls_features_hook__",
    "__process_obj_features_hook__",
    _CLASSNO_EQ_KEYS_ATTR,
    _CLASSNO_HASH_KEYS_ATTR,
    _CLASSNO_ORDER_KEYS_ATTR,
}


class Features(enum.Flag):
    EQ = enum.auto()
    REPR = enum.auto()
    ORDER = enum.auto()

    HASH = enum.auto()
    SLOTS = enum.auto()

    FROZEN = enum.auto()
    PRIVATE = enum.auto()

    VALIDATION = enum.auto()

    LOSSY_AUTOCAST = enum.auto()

    NONE = 0
    DEFAULT = EQ | REPR | ORDER
    IMMUTABLE = DEFAULT | HASH | SLOTS | FROZEN
