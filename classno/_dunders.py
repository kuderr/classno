import operator
import typing as t


def __repr__(self) -> str:
    return f"{self.__class__.__name__}({self.as_kwargs()})"


def __hash__(self) -> int:
    return hash(self._hash_value())


def _hash_value(self):
    def make_hashable(obj):
        """Convert unhashable objects to hashable equivalents."""
        if isinstance(obj, dict):
            # For dict-like objects, convert values recursively
            items = []
            for key, value in obj.items():
                items.append((key, make_hashable(value)))
            return tuple(sorted(items))
        elif isinstance(obj, (list, set)):
            # For lists and sets, convert elements recursively
            return tuple(make_hashable(item) for item in obj)
        elif hasattr(obj, "__iter__") and not isinstance(obj, (str, bytes)):
            try:
                # For other iterables, try to convert elements recursively
                return tuple(make_hashable(item) for item in obj)
            except TypeError:
                # If we can't iterate or convert to tuple, use string representation
                return str(obj)
        else:
            return obj

    return tuple(make_hashable(getattr(self, k)) for k in self.__hash_keys__)


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
    other_key = getattr(other, key)()

    return op(self_key, other_key)
