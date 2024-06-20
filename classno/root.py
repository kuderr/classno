import enum
import operator
import types
import typing as t
import dataclasses


class MissingType: ...


MISSING = MissingType
_CLASSNO_ATTRS = {"__features__", "__fields__"}


def field(*, default=MISSING, default_factory=MISSING, metadata=None):
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError("cannot specify both default and default_factory")

    return Field(default, default_factory, metadata)


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


def build_fields(cls):
    hints = t.get_type_hints(cls)

    fields = {}
    for name, hint in hints.items():
        if name in _CLASSNO_ATTRS:
            continue

        attr = getattr(cls, name, MISSING)
        f = attr if isinstance(attr, Field) else field(default=attr)

        f.name = name
        f.hint = hint

        fields[name] = f

    return fields


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


class Classno:
    __fields__: t.ClassVar[dict[str, Field]] = {}
    __features__: t.ClassVar[Features] = Features.DEFAULT

    def __init_subclass__(cls):
        cls.__fields__ = build_fields(cls)
        preprocess_features(cls)

    def __init__(self, **kwargs):
        missing_fields = []

        for field in self.__fields__.values():
            if field.name in kwargs:
                setattr(self, field.name, kwargs[field.name])
            elif field.default is not MISSING:
                setattr(self, field.name, field.default)
            elif field.default_factory is not MISSING:
                setattr(self, field.name, field.default_factory())
            else:
                missing_fields.append(field.name)

        if missing_fields:
            raise TypeError(
                f"{self.__class__.__name__}.__init__() missing {len(missing_fields)} "
                f"required arguments: {', '.join(f'{arg}' for arg in missing_fields)}"
            )

        postprocess_features(self.__class__)

    def as_dict(self):
        return {f.name: getattr(self, f.name) for f in self.__fields__.values()}

    def as_kwargs(self):
        return ", ".join(f"{k!s}={v!r}" for k, v in self.as_dict().items())

    def __repr__(self) -> str:
        # return ", ".join(f"{k!s}={v!r}" for k, v in self._repr_dict.items())
        return f"{self.__class__.__name__}({self.as_kwargs()})"

    def _hash_key(self):
        return tuple(getattr(self, f.name) for f in self.__fields__.values())

    # if only immutable
    def __hash__(self) -> int:
        return hash(self._hash_key())

    def _eq_key(self):
        return tuple(getattr(self, f.name) for f in self.__fields__.values())

    def __eq__(self, other: object) -> bool:
        return self._cmp_factory(other, operator.eq, self._eq_key.__name__)

    def _order_key(self):
        return tuple(getattr(self, f.name) for f in self.__fields__.values())

    def __lt__(self, other: object) -> bool:
        return self._cmp_factory(other, operator.lt, self._order_key.__name__)

    def __le__(self, other: object) -> bool:
        return self._cmp_factory(other, operator.le, self._order_key.__name__)

    def __gt__(self, other: object) -> bool:
        return self._cmp_factory(other, operator.gt, self._order_key.__name__)

    def __ge__(self, other: object) -> bool:
        return self._cmp_factory(other, operator.ge, self._order_key.__name__)

    def _cmp_factory(
        self,
        other: object,
        op: t.Callable[[t.Any, t.Any], bool],
        key: str,
    ) -> bool:
        if other.__class__ is not self.__class__:
            return NotImplemented

        self_key = getattr(self, key)()
        other_key = getattr(self, key)()

        return op(self_key, other_key)


def preprocess_features(cls: t.Type[Classno]) -> None:
    fields = cls.__fields__
    features = cls.__features__

    # process if all these methods already set in cls
    if Features.EQ not in features:
        cls.__eq__ = None
    if Features.ORDER not in features:
        cls.__lt__ = cls.__le__ = cls.__gt__ = cls.__ge__ = None
    if Features.HASH not in features:
        cls.__hash__ = None
    if Features.SLOTS in features:
        cls.__slots__ = tuple(f.name for f in fields.values())


def _raise_frozen_attr_exc(*args, **kwargs):
    raise Exception("lala")


def postprocess_features(cls: t.Type[Classno]) -> None:
    features = cls.__features__

    if Features.FROZEN in features:
        cls.__setattr__ = cls.__delattr__ = _raise_frozen_attr_exc
    if Features.PRIVATE in features:
        # TODO
        ...
