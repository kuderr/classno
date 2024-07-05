import operator
import typing as t

from classno import _fields
from classno import _utils
from classno import constants as c


def init_obj(self: "Classno", *args, **kwargs):
    missing_fields = []

    _setattr = super(self.__class__, self).__setattr__

    for field in self.__fields__.values():
        if field.name in kwargs:
            _setattr(field.name, kwargs[field.name])
        elif field.default is not c.MISSING:
            _setattr(field.name, field.default)
        elif field.default_factory is not c.MISSING:
            _setattr(field.name, field.default_factory())
        else:
            missing_fields.append(field.name)

    if missing_fields:
        raise TypeError(
            f"{self.__class__.__name__}.__init__() missing {len(missing_fields)} "
            f"required arguments: {', '.join(f'{arg}' for arg in missing_fields)}"
        )


class MetaClassno(type):
    def __new__(cls, name, bases, attrs):
        klass = super().__new__(cls, name, bases, attrs)
        _utils.set_fields(klass)
        _utils.set_keys(klass)
        _utils.process_cls_features(klass)
        return klass

    def __call__(cls, *args, **kwargs):
        # Called on SubClassno(...)
        obj = type.__call__(cls, *args, **kwargs)
        init_obj(obj, *args, **kwargs)
        _utils.process_obj_features(obj)
        return obj


class Classno(metaclass=MetaClassno):
    __fields__: t.ClassVar[dict[str, _fields.Field]] = {}
    __features__: t.ClassVar[c.Features] = c.Features.DEFAULT

    __hash_keys__: t.ClassVar[set[str]] = set()
    __eq_keys__: t.ClassVar[set[str]] = set()
    __order_keys__: t.ClassVar[set[str]] = set()

    def as_dict(self):
        return {f.name: getattr(self, f.name) for f in self.__fields__.values()}

    def as_kwargs(self):
        return ", ".join(f"{k!s}={v!r}" for k, v in self.as_dict().items())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.as_kwargs()})"

    def __hash__(self) -> int:
        return hash(self._hash_value())

    def _hash_value(self):
        return tuple(getattr(self, k) for k in self.__hash_keys__)

    def __eq__(self, other: object) -> bool:
        return self._cmp_factory(other, operator.eq, self._eq_value.__name__)

    def _eq_value(self):
        return tuple(getattr(self, k) for k in self.__eq_keys__)

    def __lt__(self, other: object) -> bool:
        return self._cmp_factory(other, operator.lt, self._order_value.__name__)

    def __le__(self, other: object) -> bool:
        return self._cmp_factory(other, operator.le, self._order_value.__name__)

    def __gt__(self, other: object) -> bool:
        return self._cmp_factory(other, operator.gt, self._order_value.__name__)

    def __ge__(self, other: object) -> bool:
        return self._cmp_factory(other, operator.ge, self._order_value.__name__)

    def _order_value(self):
        return tuple(getattr(self, k) for k in self.__order_keys__)

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
