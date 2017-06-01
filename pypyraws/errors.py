"""Custom exceptions for pypyraws.

All pypyraws specific exceptions derive from pypyr root Error.
"""

from pypyr.errors import PlugInError


class Error(PlugInError):
    """Base class for all pypyraws exceptions."""


class WaitTimeOut(Error):
    """Aws resource that did not finish processing within wait limit."""
