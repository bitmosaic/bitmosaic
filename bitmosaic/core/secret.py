# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# secret.py is part of Bitmosaic.
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
# along with Bitmosaic. If not, see <https://www.gnu.org/licenses/>.

import ast
import os
import random
import bitmosaic.util as util
from bitmosaic.core.filler import MatrixFiller
from bitmosaic.core.matrix import Point
from bitmosaic.core.matrix import V2Component
from bitmosaic.exception import FileException
from bitmosaic.exception import InvalidFormatException
from bitmosaic.exception import ValueException


class Secret:
    """
    This class represents a secret in bitmosaic.

    The secret is made of:
        - An unique name.
        - The data to hide.
        - A point where the first data item will be placed.
        - A set of V2Component that will be used to create the points to get the next data items.

    Properties
    ----------
    name : str
        The name that identifies this secret
    data : [str]
        The sensible information
    origin : Point
        The point to place the first data item
    v2_components : set
        The V2Component that will be used to create the points to get the next data items

    Methods
    -------
    is_complete() -> bool
        Returns if all necessary info is filled
    """

    @property
    def name(self) -> str:
        return self._name

    @property
    def data(self) -> [str]:
        return self._data

    @property
    def origin(self) -> Point:
        return self._origin

    @property
    def components(self) -> set:
        return self._components

    def __init__(self, name: str, data: [str], origin: Point, v2_components: set):
        """
        :param str name: the secret's name
        :param [str] data: the sensible information
        :param Point origin: the point for the first data item
        :param set v2_components: a set of objects used to create the next points to get the following data items
        """
        self._name = name
        self._data = data
        self._origin = origin
        self._components = v2_components

    def __eq__(self, other):
        return type(other) == Secret and (self.name == other.name or self.origin == other.origin)

    def __hash__(self):
        return hash(self.name)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return "Secret({0}, {1}, {2}, {3})".format(self._name, self._data, repr(self._origin),
                                                   repr(self._components))

    def __str__(self):
        components = " ".join([str(x) for x in sorted(self.components)])
        return "{0}|{1}|{2}".format(self._origin, components, len(self._data))

    def is_complete(self) -> bool:
        """
        Checks if all necessary info is filled

        :return: bool
        """
        return (self._data is not None and isinstance(self._data, list) and len(self._data) > 0 and
                self._origin is not None and isinstance(self._origin, Point) and
                self._components is not None and len(self._components) > 0 and isinstance(self._components, set))


class Recovery(Secret):
    """
    A class used to recover a hidden secret.

    Extends the Secret class by adding more specific properties.

    The secret is unknown at the moment of creation.

    Properties
    ----------
    name : str
        The name that identifies this secret
    data : [str]
        The sensible information
    origin : Point
        The point to place the first data item
    v2_components : set
        The V2Component that will be used to create the points to get the next data items
    cols : int
        The number of cols
    rows : int
        The number of rows
    length : int
        The length of the secret

    Methods
    -------
    card() -> str
        Returns a string for printing in a card format

    is_complete() -> bool
        Overrides super class method.
        Returns if all necessary info is filled

    Class Methods
    -------------
    create_from_file(file_path: str) -> Recovery
        Creates a recovery object with contents of file_path file

    """

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def secret(self) -> str:
        secret = None
        if None not in self._data and len(self._data) > 0:
            secret = " ".join(self._data)[:-1]
        return secret

    def __init__(self, name: str, origin: Point, v2_components: set, cols: int, rows: int, length: int):
        """
        Extends super class init method.

        :param str name: the secret's name
        :param [str] data: the sensible information
        :param Point origin: the point for the first data item
        :param set v2_components: a set of objects used to create the next points to get the following data items
        :param int cols: the number of cols
        :param int rows: the number of rows
        :param int length: the number of items in the secret
        """
        super().__init__(name=name, data=[], origin=origin, v2_components=v2_components)
        self._data = [None for _ in range(length)]
        self._cols = cols
        self._rows = rows

    def __repr__(self):
        return "Recovery({0}x{1}, {2}, {3}, {4}, {5})".format(self._cols, self._rows, self._name, self._data,
                                                              repr(self._origin), repr(self._components),
                                                              self.__len__())

    def __str__(self):
        return "{0}x{1}|{2}".format(self._cols, self._rows, super().__str__())

    def card(self) -> str:
        """
        Creates a string to be printed in a card format

        :returns: str
        """
        components = list(sorted(self.components))
        components_str = ""
        for index, component in enumerate(components):
            if index % 4 == 0:
                components_str += "\n\n"
            components_str += str(component) + " "
        return "{0}x{1}\n\n{2}\n{3}\n\n\n{4}".format(self.cols, self.rows, self.origin, components_str, self.__len__())

    def is_complete(self) -> bool:
        """
        Checks if all the necessary info is filled

        :return: bool
        """
        return (self._name is not None and self._name != "" and
                self.cols >= 0 and
                self.rows >= 0 and
                self.origin is not None and isinstance(self.origin, Point) and
                self.components is not None and isinstance(self.components, set) and
                self.__len__() > 0)

    @classmethod
    def create_from_file(cls, file_name: str) -> 'Recovery':
        """
        Creates a Recovery object from the contents of the file.

        :param str file_name: the name of the file to get the content.
        :return: Recovery
        """
        try:
            file = util.get_output_directory(file_name)
            file_content = util.read_txt_file(str(file))
        except FileException as e:
            raise e
        file_path = os.path.normpath("{0}/{1}".format(util.get_output_directory(), file_name))
        if not os.path.exists(file_path):
            raise FileException(file_name, "The file {0} does not exist".format(file_name))

        splitted_recovery = []
        try:
            splitted_recovery = file_content.split("|")
            if len(splitted_recovery) != 4:
                raise InvalidFormatException(len(splitted_recovery), "Incorrect format for recovery")
            cols, rows = splitted_recovery[0].split('x')
            text_origin = ast.literal_eval(splitted_recovery[1])
            origin = Point(int(text_origin[0]), int(text_origin[1]))
            components = V2Component.components_from_string(splitted_recovery[2])
            length = int(splitted_recovery[3])
        except FileException as e:
            raise e
        except InvalidFormatException as e:
            raise e
        except ValueError:
            raise ValueException(splitted_recovery[3],
                                 "The value for length is not valid: {0}".format(splitted_recovery[3]))

        return cls(name=file_name, origin=origin, v2_components=components, cols=int(cols), rows=int(rows),
                   length=int(length))


class Vault:
    """
    Defines a method to store the secrets.

    Methods
    -------

    add_secret(secret: Secret)
        adds a secret to the vault if is complete and was not previously added.

    remove_secret(secret: Secret)
        removes a secret from the vault.

    remove_secret_by_name(name: str)
        removes a secret identified by its name

    get_secret(index: int) -> Secret
        get the secret at specified position.
    """

    def __init__(self):
        self._content = []

    def __repr__(self):
        return "Vault: {0} secret(s)".format(len(self._content))

    def __len__(self):
        return len(self._content)

    def add_secret(self, secret: Secret) -> bool:
        """
        Adds a secret to the vault if the secret is complete and was not previously added.

        :param Secret secret: the secret to add.
        :return: bool
        """
        if secret not in self._content and secret.is_complete():
            self._content.append(secret)
            return True
        return False

    def remove_secret(self, secret: Secret) -> bool:
        """
        Removes a secret from the vault.

        :param Secret secret: the secret to remove.
        :return: bool
        """
        if secret in self._content and secret.is_complete():
            self._content.remove(secret)
            return True
        return False

    def remove_secret_by_name(self, name: str):
        """
        Removes a secret from the vault searched by name.

        :param str name: the secret's name to remove.
        """
        for secret in self._content:
            if secret.name == name.replace("_", " "):
                self.remove_secret(secret)

    def get_secret(self, index: int) -> Secret:
        """
        :param int index: the index to get the secret.

        :return: Secret
        """
        if index in range(len(self._content)):
            return self._content[index]
