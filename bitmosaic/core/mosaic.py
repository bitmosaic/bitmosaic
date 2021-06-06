# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# mosaic.py is part of Bitmosaic.
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


import random
import secrets
from bitmosaic.core.data_domain import Domain
from bitmosaic.core.filler import ColorFiller
from bitmosaic.core.filler import PaletteFiller
from bitmosaic.core.filler import RecoveryFiller
from bitmosaic.core.filler import MatrixFiller
from bitmosaic.core.filler import NoneFiller
from bitmosaic.core.matrix import Matrix
from bitmosaic.core.matrix import Point
from bitmosaic.core.matrix import V2Point
from bitmosaic.core.matrix import V2Component
from bitmosaic.core.secret import Secret
from bitmosaic.core.secret import Vault
from bitmosaic.core.secret import Recovery
from bitmosaic.drawing.color import Color
from bitmosaic.exception import ErrorCodes
from bitmosaic.exception import IncompleteSecretException
from bitmosaic.exception import InvalidComponentException
from bitmosaic.exception import MosaicItemCollisionException
from bitmosaic.exception import ValueException


class Tessera:
    """Creates a tessera. A tessera is each piece in a mosaic.
    A tessera stores:
        - The position in the mosaic
        - The data
        - A V2Point to get the position for the next tessera

    Properties
    ----------

    position : Point
        The position in the mosaic

    data : str
        The data for this tessera

    v2_point: V2Point
        Add this point to the tessera's position to get the point of the next tessera

    Methods
    -------

    next() -> Point
        Returns the position for the next tessera in the mosaic

    Class Method
    ------------

    from_recovery(data: str) -> Tessera
        Returns a Tessera object created from a string

    """

    @property
    def position(self) -> Point:
        return self._position

    @property
    def data(self) -> str:
        return self._data

    @property
    def v2_point(self) -> V2Point:
        return self._v2_point

    @data.setter
    def data(self, value: str):
        self._data = value

    @position.setter
    def position(self, value: Point):
        self._position = value

    @v2_point.setter
    def v2_point(self, value: V2Point):
        self._v2_point = value

    def __init__(self, position: Point, data: str, v2_point: V2Point):
        """
        :param Point position: the position in the mosaic
        :param str data: the data
        :param V2Point v2_point: the point to get the next tessera
        """
        self._data = data
        self._position = position
        self._v2_point = v2_point

    def __repr__(self):
        return "Tessera({0}, {1}, {2})".format(self.position, self.data, self.v2_point)

    def __str__(self):
        return "{0}{1}|".format(self.data, self.v2_point.labels())

    def next(self) -> Point:
        """Calculates the position in the mosaic for next tessera
        :return: Point
        """
        return self.position + self.v2_point.to_point()

    @classmethod
    def init_for_recovery(cls, point: Point, data: str, components: set) -> 'Tessera':
        """
        Creates a tessera from data in recovery file
        :param tuple point: the point as tuple
        :param str data: the tessera's data
        :param set components: the available V2Component set
        :return: Tessera
        """
        max_value = random.randint(1, 100)
        secret = data[0:len(data) - 2]
        vector = data[-2:len(data)]
        first_component_label = vector[0]
        first_component_value = 1 if first_component_label.islower() else -1
        second_component_label = vector[1]
        second_component_value = 1 if second_component_label.islower() else -1

        try:
            first_component = V2Component(first_component_label, first_component_value)
            first_component_found = first_component.in_set(components)

            if first_component_found is None:
                label = first_component.label
                value = secrets.randbelow(max_value) * (1 if label.islower() else -1)
            else:
                label = first_component.label
                value = first_component_found.value * (1 if label.islower() else -1)

            first_component = V2Component(label, value)

            second_component = V2Component(second_component_label, second_component_value)
            second_component_found = second_component.in_set(components)

            if second_component_found is None:
                label = second_component.label
                value = secrets.randbelow(max_value + 1) * (1 if label.islower() else -1)
            else:
                label = second_component.label
                value = second_component_found.value * (1 if label.islower() else -1)

            second_component = V2Component(label, value)
        except Exception:
            raise InvalidComponentException(ErrorCodes.invalid_component, "There are invalid components")

        return cls(point, secret, V2Point(first_component, second_component))


class Mosaic:
    """
    This class creates a mosaic. A mosaic is made of tesserae.

    The mosaic has two main attributes:
        - The mosaic data matrix
        - The mosaic color matrix

    The values for each matrix come from an 'filler' object. The filler for the color matrix has the values for the
    number of cols and rows for the mosaic.

    Optionally, a data filler can be provided to initialize the matrix with some custom data instead of None.

    Properties:
    -----------

    cols : int
        number of cols of the mosaic

    rows : int
        number of rows of the mosaic

    matrix : Matrix
        the matrix where the mosaic data is stored


    Methods
    -------

    build()
        creates an empty matrix with the number of cols and rows specified

    build_with_data(data, components)
        creates a matrix from the file contents

    add_secret(secret: Secret)
        adds a secret to the secrets list

    remove_secret(secret: Secret)
        removes a secret from the secrets list

    hide_secrets(the_secrets: [Secret])
        hides the secrets into the matrix

    recover_secret(recovery: Recovery) -> Secret
        recovers the secret whit the recovery information

    get_tessera(point: Point) -> Tessera
        returns the tessera at point

    set_tessera(tessera: Tessera, point: Point)
        sets the tessera at point

    """

    @property
    def cols(self) -> int:
        return self._color_filler.cols

    @property
    def rows(self) -> int:
        return self._color_filler.rows

    @property
    def matrix(self) -> Matrix:
        return self.__data_matrix

    @property
    def recoveries(self) -> list:
        return self.__recoveries

    def __init__(self, domain: Domain, color_filler: ColorFiller, data_filler: MatrixFiller = NoneFiller()):
        self._domain = domain
        self._color_filler = color_filler
        self.__color_matrix = Matrix(self.cols, self.rows, color_filler)
        self.__data_matrix = Matrix(self.cols, self.rows, data_filler)
        self.__recoveries = []

    def __len__(self):
        return self.cols * self.rows

    def __repr__(self):
        return "Mosaic({0}x{1})".format(self.cols, self.rows)

    def __str__(self):
        return str(self.__data_matrix)

    def get_color(self, point: Point) -> Color:
        """
        Returns the color at point from color matrix.

        :param Point point: the point in mosaic.
        :return: Tessera
        """
        return self.__color_matrix.get_item(point)

    def get_tessera(self, point: Point) -> Tessera:
        """
        Returns the tessera at point.

        :param Point point: the point in mosaic.
        :return: Tessera
        """
        return self.__data_matrix.get_item(point)

    def set_tessera(self, tessera: Tessera, point: Point):
        """
        Sets the tessera at point.

        :param Tessera tessera: the tessera to store.
        :param Point point: the point where the tessera has to be placed
        """
        tessera.position = self.__data_matrix.normalize_point(point)
        self.__data_matrix.set_item(tessera, point)

    @classmethod
    def from_recovery(cls, bitmosaic_data: str, recovery: Recovery):
        color_filler = PaletteFiller(recovery.cols, recovery.rows)
        data_filler = RecoveryFiller(recovery.cols, recovery.rows, recovery, bitmosaic_data)
        return Mosaic(domain=None, color_filler=color_filler, data_filler=data_filler)

    def hide_secrets(self, vault: Vault):
        """
        Hide the_secrets in the matrix.

        :param Vault vault: the collection of secrets to hide.
        :raises IncompleteSecretException:
        """
        if vault is None or len(vault) == 0:
            raise IncompleteSecretException(vault, "Vault can't be empty")

        for index in range(len(vault)):
            secret = vault.get_secret(index)
            if not secret.is_complete():
                raise IncompleteSecretException(secret, "The secret needs to be complete to be hidden")

            self.__recoveries.append(Recovery(secret.name, secret.origin, secret.components,
                                              self.cols, self.rows, len(secret)))

            rand_min = secrets.randbelow(100)
            rand_max = random.randint(rand_min, 100)
            hidden = []

            for index, value in enumerate(secret.data):
                if not self._domain.contains(value):
                    raise ValueException(value, "'{0}' was not found in domain".format(value))
                if index == 0:
                    point = secret.origin
                else:
                    point = hidden[-1].position + hidden[-1].v2_point.to_point()
                if self.get_tessera(point) is not None:
                    raise MosaicItemCollisionException(point, "Collision at {0}".format(point))
                v2_point = self.__v2_point(point, secret, rand_min, rand_max)
                tessera = Tessera(point, value, v2_point)
                hidden.append(tessera)
                self.set_tessera(tessera, tessera.position)
        del hidden
        self.__complete_with_fake_data()

    def recover_secret(self, recovery: Recovery) -> Recovery:
        """
        Recovers the secret hidden in the mosaic.

        :param Recovery recovery: the recovery info used to recover the secret.
        :return: Recovery
        """
        if not Point.zero() <= recovery.origin < Point(self.cols, self.rows):
            raise ValueException(recovery.origin, "The point is not valid for this mosaic")

        index = 0
        while index < len(recovery):
            if index == 0:
                tessera = self.get_tessera(recovery.origin)
            else:
                tessera = self.get_tessera(tessera.next())
            recovery.data[index] = tessera.data
            index += 1
        return recovery

    def __complete_with_fake_data(self):
        """
        Completes the empty matrix positions with fake tesserae.
        """
        index = 0
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                point = Point(col, row)
                if self.get_tessera(point) is None:
                    if index < len(self._domain):
                        data = self._domain.data[index]
                    else:
                        data = self._domain.random(count=1)[0]
                    tessera = Tessera(point, data, V2Point.random_fake())
                    self.set_tessera(tessera, point)
                index += 1

    def __v2_point(self, point: Point, secret: Secret, min_value: int, max_value: int) -> V2Point:
        """
        Returns a valid V2Point, used to hide the secret in the mosaic.

        :param Point point: the point for the current tessera
        :param Secret secret: the secret used to get the valid V2Components
        :param int min_value: minimum value for the random value for next point coordinates
        :param int max_value: maximum value for the random value for next point coordinates
        :return: V2Point
        """
        while True:
            v1 = random.choice(tuple(secret.components))
            next_x_sign = 1
            if min_value < secrets.randbelow(100) < max_value:
                next_x_sign = -1
            next_x = V2Component(v1.label, v1.value * next_x_sign)

            v2 = random.choice(tuple(secret.components))
            next_y_sign = 1
            if min_value < secrets.randbelow(100) < max_value:
                next_y_sign = -1
            next_y = V2Component(v2.label, v2.value * next_y_sign)

            v2_point = V2Point(next_x, next_y)
            empty_destination_point = v2_point.to_point() + point

            if self.get_tessera(empty_destination_point) is None and \
                    not self.__data_matrix.same_point(empty_destination_point, point):
                break
        return v2_point
