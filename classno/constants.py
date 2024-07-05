import enum


class MissingType: ...


MISSING = MissingType
_CLASSNO_KEYS_ATTRS = {
    "__hash_keys__",
    "__eq_keys__",
    "__order_keys__",
}
_CLASSNO_ATTRS = {
    "__features__",
    "__fields__",
    "__init_hook__",
    "__set_keys_hook__",
    "__set_fields_hook__",
    "__process_cls_features_hook__",
    "__process_obj_features_hook__",
} | _CLASSNO_KEYS_ATTRS


class Features(enum.Flag):
    EQ = enum.auto()
    ORDER = enum.auto()

    HASH = enum.auto()
    SLOTS = enum.auto()

    FROZEN = enum.auto()
    PRIVATE = enum.auto()

    VALIDATION = enum.auto()

    NONE = 0
    DEFAULT = EQ | ORDER
    IMMUTABLE = DEFAULT | HASH | SLOTS | FROZEN
