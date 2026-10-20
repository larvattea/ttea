"""Utility classes for the T-TEA platform.

Includes path management, CSV handling, dialogs, exception hooks,
date formats, images, OpenCV text and the help system support.

Attributes
----------
__version__ : str
    Current package version.
__date__ : str
    Release date of the package version.
__author__ : str
    Package author or team.
__license__ : str
    Package license.

See Also
--------
CriticalHooks
    Global exception hooks with a translated error dialog.
CSVHandler
    Handling CSV files with a custom dialect.
CvText
    Unicode text and window titles for OpenCV windows.
HelpKeyFilter
    Application-wide F1 key handling for the help.
Image
    Loading images from Qt resources as pygame surfaces.
MessageService
    Centralized Qt message dialogs.
PathConfig
    Manage file paths and directory structures.
QtDateFormat
    Conversion of Python date formats to Qt formats.

Notes
-----
This package is maintained by the Larva UDESC team and is under active
development.

Contributions and bug reports are welcome at:
https://github.com/larvattea/ttea
"""

__all__ = [
    "CriticalHooks",
    "CSVHandler",
    "CvText",
    "HelpKeyFilter",
    "Image",
    "MessageService",
    "QtDateFormat",
    "PathConfig",
]

__version__ = "1.0.0"
__date__ = "2025-12-25"
__author__ = "Larva UDESC"
__license__ = "MIT License"

from .criticalhooks import CriticalHooks
from .cvshandler import CSVHandler
from .cvtext import CvText
from .helpkeyfilter import HelpKeyFilter
from .image import Image
from .messageservice import MessageService
from .pathconfig import PathConfig
from .qtdateformat import QtDateFormat
