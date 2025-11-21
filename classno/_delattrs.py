import typing as t

from classno import _errors


def frozen_delattr(self, name: str) -> t.Never:
    raise AttributeError(
        _errors.ErrorFormatter.frozen_delete_error(self.__class__.__name__)
    )
