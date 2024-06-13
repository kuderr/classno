import typing as t

import types
import operator
import functools
import enum


class MissingType: ...


MISSING = MissingType
_CLASSNO_ATTRS = {"__features__", "_Classno__fields"}


class Field:
    def __init__(self, default, default_factory, metadata):
        self.name = None
        self.hint = None
        self.default = default
        self.default_factory = default_factory
        self.metadata = types.MappingProxyType(metadata or {})

    def __repr__(self) -> str:
        return (
            "Field("
            f"name={self.name!r}, "
            f"hint={self.hint!r}, "
            f"default={self.default!r}, "
            f"default_factory={self.default_factory!r}, "
            f"metadata={self.metadata!r}"
            ")"
        )


def field(*, default=MISSING, default_factory=MISSING, metadata=None):
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError("cannot specify both default and default_factory")

    return Field(default, default_factory, metadata)


def build_fields(cls):
    hints = t.get_type_hints(cls)

    fields = {}
    for name, hint in hints.items():
        if name in _CLASSNO_ATTRS:
            continue

        attr = getattr(cls, name, MISSING)
        if isinstance(attr, Field):
            f = attr
        else:
            if isinstance(attr, types.MemberDescriptorType):
                attr = MISSING
            f = field(default=attr)

        f.name = name
        f.hint = hint

        fields[name] = f

    return fields


class Features(enum.Flag):
    INIT = enum.auto()
    REPR = enum.auto()
    EQ = enum.auto()
    ORDER = enum.auto()
    FROZEN = enum.auto()
    KW_ONLY = enum.auto()
    HASH = enum.auto()
    SLOTS = enum.auto()

    NONE = 0
    DEFAULT = INIT | REPR | EQ | ORDER | FROZEN | KW_ONLY | HASH | SLOTS


class Classno:
    __fields: t.ClassVar[dict[str, Field]] = {}
    __features__: t.ClassVar[Features] = Features.DEFAULT

    def __init_subclass__(cls):
        cls.__fields = build_fields(cls)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        missing_required_pos_args = []
        for field in self.__fields.values():
            if hasattr(self, field.name) and not isinstance(
                getattr(self, field.name), Field
            ):
                continue

            if field.default is not MISSING:
                setattr(self, field.name, field.default)
            elif field.default_factory is not MISSING:
                setattr(self, field.name, field.default_factory())
            else:
                missing_required_pos_args.append(field.name)

        if missing_required_pos_args:
            raise TypeError(
                f"{self.__class__.__name__}.__init__() missing {len(missing_required_pos_args)} "
                f"required positional arguments: {', '.join(f'{arg}' for arg in missing_required_pos_args)}"
            )

    # @functools.cached_property
    @property
    def __key(self):
        return tuple(getattr(self, f.name) for f in self.__fields.values())

    # @functools.cached_property
    @property
    def as_dict(self):
        return {f.name: getattr(self, f.name) for f in self.__fields.values()}

    # @functools.cached_property
    @property
    def as_kwargs(self):
        return ", ".join(f"{k!s}={v!r}" for k, v in self.as_dict.items())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.as_kwargs})"

    # if only immutable
    def __hash__(self) -> int:
        return hash(self.__key)

    def __eq__(self, other: object) -> bool:
        return self.__cmp_factory(other, operator.eq)

    def __lt__(self, other: object) -> bool:
        return self.__cmp_factory(other, operator.lt)

    def __le__(self, other: object) -> bool:
        return self.__cmp_factory(other, operator.le)

    def __gt__(self, other: object) -> bool:
        return self.__cmp_factory(other, operator.gt)

    def __ge__(self, other: object) -> bool:
        return self.__cmp_factory(other, operator.ge)

    def __cmp_factory(self, other: object, op: str) -> bool:
        if not (other.__class__ is self.__class__):
            return NotImplemented

        return op(self.__key, other.__key)
