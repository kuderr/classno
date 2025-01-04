import typing as t

from classno import _fields
from classno import _hooks
from classno import constants as c


class MetaClassno(type):
    def __new__(cls, name, bases, attrs):
        klass = super().__new__(cls, name, bases, attrs)
        klass.__set_fields_hook__(klass)
        klass.__process_cls_features_hook__(klass)
        return klass

    def __call__(cls, *args, **kwargs):
        # Called on SubClassno(...)
        obj = type.__call__(cls, *args, **kwargs)
        cls.__init_hook__(obj, *args, **kwargs)
        cls.__process_obj_features_hook__(obj)
        return obj


class Classno(metaclass=MetaClassno):
    __fields__: t.ClassVar[dict[str, _fields.Field]] = {}
    __features__: t.ClassVar[c.Features] = c.Features.DEFAULT

    __eq_keys__: t.ClassVar[set[str]] = set()
    __hash_keys__: t.ClassVar[set[str]] = set()
    __order_keys__: t.ClassVar[set[str]] = set()

    __init_hook__ = _hooks.init_obj
    __set_fields_hook__ = _hooks.set_fields
    __process_cls_features_hook__ = _hooks.process_cls_features
    __process_obj_features_hook__ = _hooks.process_obj_features

    def __init__(self, *args, **kwargs) -> None: ...

    def __call__(self, *args, **kwargs) -> None:
        raise TypeError(f"'{self.__class__.__name__}' object is not callable")

    def as_dict(self):
        return {f.name: getattr(self, f.name) for f in self.__fields__.values()}

    def as_kwargs(self):
        return ", ".join(f"{k!s}={v!r}" for k, v in self.as_dict().items())
