class OctoAuthException(Exception):
    ...


class DatabaseException(OctoAuthException):
    ...


class ObjectNotFoundException(DatabaseException):
    ...


class AuthenticationError(OctoAuthException):
    ...


class UIException(Exception):
    def __init__(self, message: str, details: str = None):
        super().__init__(message)
        self.message = message
        self.details = details


class AuthenticationRequired(UIException):
    ...


class AuthenticationForbidden(UIException):
    ...
