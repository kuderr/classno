import enum


class MissingType:
    ...


MISSING = MissingType
_CLASSNO_KEYS_ATTRS = {
    "__hash_keys__",
    "__eq_keys__",
    "__order_keys__",
}
_CLASSNO_ATTRS = {
    "__features__",
    "__fields__",
} | _CLASSNO_KEYS_ATTRS


class Features(enum.Flag):
    EQ = enum.auto()
    ORDER = enum.auto()

    HASH = enum.auto()
    SLOTS = enum.auto()

    FROZEN = enum.auto()
    PRIVATE = enum.auto()

    NONE = 0
    DEFAULT = EQ | ORDER
    IMMUTABLE = DEFAULT | HASH | SLOTS | FROZEN
