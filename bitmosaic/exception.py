# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# exceptions.py is part of Bitmosaic.
#
# Bitmosaic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Bitmosaic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Bitmosaic.  If not, see <https://www.gnu.org/licenses/>.

from enum import Enum
from enum import auto


class ErrorCodes(Enum):
    no_error = 0
    file_error = auto()
    invalid_component = auto()
    invalid_format = auto()
    invalid_value = auto()
    value_error = auto()
    incomplete_secret = auto()
    recovery_info_incomplete = auto()
    mosaic_item_collision = auto()
    invalid_color = auto()
    no_image_selected = auto()
    no_data_domain = auto()
    no_secret = auto()


class BitmosaicException(Exception):
    """ Base class for bitmosaic's custom exceptions
        Attributes:
            - message -- explanation of the error
            - error_code -- the error code to identify the exception
    """

    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class InvalidComponentException(Exception):
    """ Exception raised for errors in components
        Attributes:
            - value -- the value which caused the error
            - message -- explanation of the error
    """

    def __init__(self, value, message):
        self.value = value
        self.error_code = ErrorCodes.invalid_value
        self.message = message
        super().__init__(self.message, self.error_code)


class FileException(Exception):
    """ Exception raised for errors whith files
        Attributes:
            - value -- the value which caused the error
            - message -- explanation of the error
    """

    def __init__(self, value, message):
        self.value = value
        self.error_code = ErrorCodes.file_error
        self.message = message
        super().__init__(self.message, self.error_code)


class ValueException(Exception):
    """ Exception raised for value errors
        Attributes:
            - value -- the value which caused the error
            - message -- explanation of the error
    """

    def __init__(self, value, message):
        self.value = value
        self.error_code = ErrorCodes.value_error
        self.message = message
        super().__init__(self.message, self.error_code)


# Mosaic


class InvalidFormatException(Exception):
    """ Exception raised when the format is not correct
        Attributes:
            - value -- the value which caused the error
            - message -- explanation of the error
    """

    def __init__(self, value, message):
        self.value = value
        self.error_code = ErrorCodes.value_error
        self.message = message
        super().__init__(self.message, self.error_code)


class IncompleteSecretException(Exception):
    """ Exception raised for errors when the secret is not complete
        Attributes:
            - value -- the value which caused the error
            - message -- explanation of the error
    """

    def __init__(self, value, message):
        self.value = value
        self.error_code = ErrorCodes.incomplete_secret
        self.message = message
        super().__init__(self.message, self.error_code)


class MosaicItemCollisionException(Exception):
    """ Exception raised for errors when an item collides with another in mosaic
        Attributes:
            - value -- the value which caused the error
            - message -- explanation of the error
    """

    def __init__(self, value, message):
        self.value = value
        self.error_code = ErrorCodes.mosaic_item_collision
        self.message = message
        super().__init__(self.message, self.error_code)


class InvalidColorException(Exception):
    """ Exception raised for errors in colors
        Attributes:
            - value -- the value which caused the error
            - message -- explanation of the error
    """

    def __init__(self, value, message):
        self.value = value
        self.error_code = ErrorCodes.invalid_color
        self.message = message
        super().__init__(self.message, self.error_code)


class NoImageSelectedException(Exception):
    """ Exception raised when no image is selected to create the bitmosaic
        Attributes:
            - message -- explanation of the error
    """

    def __init__(self, message):
        self.value = None
        self.error_code = ErrorCodes.no_image_selected
        self.message = message
        super().__init__(self.message, self.error_code)

