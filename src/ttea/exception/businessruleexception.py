"""
Exception classes for business rule violations.

This module defines custom exception types used to handle specific
business logic violations in the application, with support for error
codes and additional contextual details.

"""

from typing import Any


class BusinessRuleException(Exception):
    """
    Exception raised when a business rule is violated.

    This exception is designed to handle specific business logic
    violations with optional error codes and additional details for
    error tracking and debugging.

    Parameters
    ----------
    message : str
        The exception message describing the business rule
        violation.
    code : str | None, optional
        Error code that identifies the type of violation
        (keyword-only). Default is None.
    details : dict[str, Any] | None, optional
        Additional details about the exception (keyword-only).
        Default is None, stored as an empty dictionary.

    Attributes
    ----------
    message : str
        The exception message describing the business rule violation.
    code : str | None
        An optional error code to identify the type of violation.
    details : dict[str, Any]
        A dictionary containing additional details about the
        exception.

    Methods
    -------
    __str__()
        Return a string representation of the exception, formatted
        with code prefix if available.
    __repr__()
        Return a detailed string representation containing all
        exception attributes.

    Notes
    -----
    ``message`` is also passed to ``Exception.__init__``, so it is
    available in ``args[0]``.

    A falsy ``details`` (None or an empty mapping) is replaced by a
    new empty dictionary. A falsy ``code`` (None or ``""``) is
    omitted from ``str()``.

    Examples
    --------
    >>> exc = BusinessRuleException("Invalid age", code="E01")
    >>> str(exc)
    '[E01] Invalid age'
    >>> str(BusinessRuleException("Invalid age"))
    'Invalid age'
    >>> exc.details
    {}

    """

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        """
        Return a string representation of the exception.

        Returns
        -------
        str
            If a code is set, returns "[{code}] {message}".
            Otherwise, returns just the message.

        """
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        """
        Return a detailed string representation of the exception.

        Returns
        -------
        str
            A string containing class name and all exception
            attributes in format "ClassName(message=..., code=...,
            details=...)".

        """
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"code={self.code!r}, "
            f"details={self.details!r})"
        )
