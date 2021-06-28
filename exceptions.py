"""
DevLogs Exceptions.

The Exceptions to be used by DevLogs
"""
from globaldata import __author__, __version__, __license__


__author__ = __author__
__version__ = __version__
__license__ = __license__


class AuthorizationException(Exception):
    """Exception raised when user failed to be authorized."""

    pass


class InvalidCredentials(AuthorizationException):
    """Exception raised when invalid credentials were given."""

    pass


class AccountLocked(AuthorizationException):
    """Exception raised when current account is locked."""

    pass


class DataFileException(Exception):
    """Exception raised when there is a problem with the app data file used."""

    pass


class FormatException(Exception):
    """Exception raised when the data doesn't follow format."""

    pass


class InvalidAccountFormat(FormatException):
    """Exception raised when the account bytes doesn't follow format."""

    pass


class AccountExists(Exception):
    """Exception raised when account already exists."""

    pass


class AccountNotFound(Exception):
    """Exception raised when account doesn't exist."""

    pass


class InvalidUsername(Exception):
    """Exception raised when username is invalid."""

    pass


class TooManyAttempts(Exception):
    """Exception raised when too many attempts to start a session are made."""

    pass


class SessionOngoing(Exception):
    """Exception raised when a session is still ongoing."""

    pass


class NoSession(Exception):
    """Exception raised when no session is ongoing yet."""

    pass
