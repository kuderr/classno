class BaseErrorsCollection(Exception):
    def __init__(self, errors):
        self.errors = errors
        error_lines = [f"\n  - {error};" for error in errors]
        super().__init__("".join(error_lines))


class ValidationError(BaseErrorsCollection): ...


class CastingError(BaseErrorsCollection): ...
