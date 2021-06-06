# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# matrix.py is part of Bitmosaic.
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
import re
import secrets
from copy import deepcopy
from bitmosaic.core.filler import MatrixFiller
from bitmosaic.exception import ErrorCodes
from bitmosaic.exception import InvalidComponentException


class Point:

    """This class represents a point with 2 coordinates.


    Properties
    ----------
    x : int
        the x coordinate of this point (the column coordinate)
    y : int
        the y coordinate of this point (the row coordinate)


    Methods
    -------

    tuple()
        Returns the point coordinates as a tuple


    Classmethods
    ------------

    zero()
        Returns a point with x=0 and y=0

    random(values: range)
        Returns a random point in the range passed as parameter to the method

    """

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def __init__(self, x: int, y: int):
        """
        :param int x: the x coordinate
        :param int y: the y coordinate
        """
        self._x = x
        self._y = y

    def __add__(self, other):
        return Point(self._x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self._x - other.x, self.y - other.y)

    def __le__(self, other):
        return self._x <= other.x and self._y <= other.y

    def __lt__(self, other):
        return self._x < other.x and self._y < other.y

    def __ge__(self, other):
        return self._x >= other.x and self._y >= other.y

    def __gt__(self, other):
        return self._x > other.x and self.y > other.y

    def __eq__(self, other):
        return self._x == other.x and self._y == other.y

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "Point(x:{0}, y:{1})".format(self._x, self._y)

    def __str__(self):
        return "({0}, {1})".format(self._x, self._y)

    def tuple(self):
        return self.x, self.y

    @classmethod
    def zero(cls) -> 'Point':
        """Returns a point with the x and y coordinates set to 0
        :return: Point
        """
        return cls(0, 0)

    @classmethod
    def random(cls, values: range) -> 'Point':
        """Returns a random point in the range passed as parameter to the method
        :param range values: the range for the MatrixPoint x and y values
        :return: Point
        """
        return cls(random.randint(values.start, values.stop-1), random.randint(values.start, values.stop-1))


class V2Component:
    """
    This class defines the component type for V2Point class.

    Properties
    ----------
    label : int
        the label to refer this component
    value : int
        the value for this component


    Methods
    -------

    in_set(the_set: set) -> bool
        Returns True if the V2Point is in the_set


    Classmethods
    ------------

    __init_fake_components()
        Returns a point with x=0 and y=0

    random(labels: [str], values: range) -> V2Component
        Returns a random V2Component taking a random label from the labels list and a random value from the range

    random_fake_component() -> V2Component
        Returns a random V2Component from the __fake_components list

    components_from_string(text: str) -> {V2Component}
        Return a set of V2Component from a given string
    """

    __fake_components = []

    @property
    def label(self) -> str:
        return self._label

    @property
    def value(self) -> int:
        return self._value

    def __init__(self, label: str, value: int, regex="[a-zA-Z]{1}"):
        """
        :param str label: the label for this component
        :param int value: the value
        :param str regex: optinal regular expression that label has to match to be valid
        :raises ValueError: if label doesn't match the regular expression
        """
        match = re.match(regex, label)
        if match is None:
            raise ValueError("Invalid label")
        self._label = match.group().lower() if value >= 0 else match.group().upper()
        self._value = int(value)

    def __repr__(self):
        return "V2Component {0}:{1} ".format(self._label, self._value)

    def __str__(self):
        return "{0}:{1}".format(self._label, self.value)

    def __eq__(self, other):
        return self.label.lower() == other.label.lower()

    def __lt__(self, other):
        return self.label.lower() < other.label.lower()

    def __hash__(self):
        return hash(str(self.label.lower()))

    def in_set(self, the_set: set) -> 'V2Component':
        """
        Checks if V2Point is in the_set passed as parameter
        :param set the_set: the set of V2Component to search for self
        :return bool:
        """
        return next((item for item in the_set if item == self), None)

    @classmethod
    def __init_fake_components(cls):
        """Private method that initializes the list of fake components
        :return: None
        """
        for c in range(ord("a"), ord("z") + 1):
            cls.__fake_components.append(V2Component(chr(c), random.randint(-10, 10)))

    @classmethod
    def random(cls, labels: [str], values: range) -> 'V2Component':
        """Returns a random V2Component taking a random label from the labels list and a random value from the range
        :param [str] labels: a list of valid labels strings
        :param range values: a range which the values to select a random value
        :return: V2Component
        """
        return cls(random.choice(labels), random.randint(values.start, values.stop-1))

    @classmethod
    def random_fake_component(cls) -> 'V2Component':
        """Returns a random fake component from the __fake_components private list
        :return: V2Component
        """
        if len(cls.__fake_components) == 0:
            cls.__init_fake_components()
        return random.choice(cls.__fake_components)

    @classmethod
    def components_from_string(cls, text: str) -> set:
        """
        Returns a set of V2Component from a given string.
        :param str text: the components as text. The format must be label:value <space> label:value (a:1 b:2 c:3)
        :raises InvalidComponentException: if the text format is not valid or if some label is not valid
        :return: {V2Component}
        """
        components = set()
        added_labels = []
        for raw_component in text.split(' '):
            data = raw_component.split(':')
            if len(data) != 2:
                raise InvalidComponentException(data, "Invalid component from string: {0}".format(raw_component))
            if data[0] not in added_labels:
                try:
                    v2_component = V2Component(data[0], abs(int(data[1])))
                    components.add(v2_component)
                except ValueError:
                    raise InvalidComponentException(ErrorCodes.invalid_component, "Invalid component from string: {0}"
                                                    .format(raw_component))
        return components


class V2Point:

    """This class defines the V2Point. A V2Point is a special type of point where each component is a V2Component.


    Properties
    ----------
    x : V2Component
        the x coordinate for the V2Point
    y : V2Component
        the y coordinate for the V2Point


    Methods
    -------

    labels() -> str
        Returns a the labels of the V2Point component as string

    to_point() -> Point
        Returns the V2Point as regular Point


    Classmethods
    ------------

    random_fake() -> V2Point
        Returns a fake V2Point with random fake V2Components

    """

    @property
    def x(self) -> V2Component:
        return self._x

    @property
    def y(self) -> V2Component:
        return self._y

    def __init__(self, x: V2Component, y: V2Component):
        """
        :param V2Component x: first V2Component
        :param V2Component y: second V2Component
        """
        self._x = x
        self._y = y

    def __repr__(self):
        return "V2Point({0}:{1})".format(self._x, self._y)

    def __str__(self):
        return "({0},{1})".format(self._x, self._y)

    def labels(self) -> str:
        """Returns a the labels of the V2Point component as string
        :return: str
        """
        return "{0}{1}".format(self._x.label, self._y.label)

    def to_point(self) -> Point:
        """Returns the V2Point as regular Point
        :return: Point
        """
        return Point(self.x.value, self.y.value)

    @classmethod
    def random_fake(cls) -> 'V2Point':
        """Returns a fake V2Point with random fake V2Components
        :return: V2Point
        """
        return cls(V2Component.random_fake_component(), V2Component.random_fake_component())


class Matrix:

    """This class defines a Matrix, the object where the data will be stored.
    A V2Point is a special type of point where each component is a V2Component.


    Properties
    ----------
    cols : int
        the number of cols in the matrix
    rows : int
        the number of rows in the matrix


    Methods
    -------

    _create_matrix() -> str
        Returns a the labels of the V2Point component as string

    get_element(point: Point) -> object
        Returns the V2Point as regular Point

    set_element(element: object, point: Point)
        Sets the element in the point in matrix

    remove_element(element: object)
        Removes the element from the matrix, if found

    normalize_point(point: Point) -> Point
        Returns a point with each component in the range of matrix indexes. Example,
        for a 4x4 matrix -> Point(5, 5) === Point(1, 1)

    random_point(empty_point: bool)
        Returns a random point from the matrix.
        If empty_point is True, returns a Point in matrix which content is not set.


    Class Methods
    ------------

    random_fake() -> V2Point
        Returns a fake V2Point with random fake V2Components

    """

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def rows(self) -> int:
        return self._rows

    def __init__(self, cols: int, rows: int, filler: MatrixFiller):
        """
        :param cols: the number of cols for the matrix
        :param rows: the number of rows for the matrix
        """
        self.__empty = []
        self._cols = cols
        self._rows = rows
        self._matrix = []
        self._filler = filler
        self._create_matrix()

    def __copy__(self):
        cls = self.__class__
        result = cls.__new__(cls)
        result.__dict__.update(self.__dict__)
        return result

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def __len__(self):
        return self._rows * self._cols

    def __eq__(self, other):
        if self._rows != other.rows or self._cols != other.cols:
            return False

        for y in range(self._rows):
            for x in range(self._cols):
                if self.get_element(Point(x, y)) != other.get_element(Point(x, y)):
                    return False
        return True

    def __str__(self):
        result = ""
        for y in range(0, self._rows):
            for x in range(0, self._cols):
                result += "{0}".format(self._matrix[y][x])
        return result

    def __repr__(self):
        result = ""
        for y in range(0, self._rows):
            for x in range(0, self._cols):
                result += "{0} | ".format(self._matrix[y][x])
            result += "\n"
        return "Matrix {0}".format(result)

    def _create_matrix(self):
        """Creates a new matrix with the number of rows and cols, filled with None"""
        for r in range(self._rows):
            row = []
            for c in range(self._cols):
                item = self._filler.get_item(Point(c, r).tuple())
                row.append(item)
                if item is None:
                    self.__empty.append(Point(c, r))
            self._matrix.append(row)

    def get_item(self, point: Point) -> object:
        """Gets the content of the point in the matrix
        :param Point point: the point to get the element
        :return: object
        """
        point = self.normalize_point(point)
        item = self._matrix[point.y][point.x]
        return item

    def set_item(self, item: object, point: Point, replace=False):
        """Sets the item at the point in matrix
        :param object item: the element we want to set in matrix
        :param Point point: the point where the element should be located
        :param bool replace: to force replace the content in point
        """
        point = self.normalize_point(point)

        if not replace and point not in self.__empty:
            return
        if point in self.__empty:
            self.__empty.remove(point)
        self._matrix[point.y][point.x] = item

    def remove_item(self, point: Point):
        """Removes the element at point from the matrix
        :param Point point: the point where the element should be removed
        """
        point = self.normalize_point(point)
        if point in self.__empty:
            return
        self._matrix[point.y][point.x] = None
        self.__empty.append(point)

    def normalize_point(self, point: Point) -> Point:
        """Returns a point with each component in the range of matrix indexes.
        :param Point point: the point to normalize
        :return: Point
        """
        new_x = point.x % self._cols
        new_y = point.y % self._rows
        return Point(new_x, new_y)

    def same_point(self, point1: Point, point2: Point) -> bool:
        """Compares two given points
        :param Point point1: the first point
        :param Point point2: the second point
        :return: bool
        """
        return self.normalize_point(point1) == self.normalize_point(point2)

    def random_point(self, empty_point=True) -> Point:
        """Return a random point from the matrix.
        :param bool empty_point: forces to return a point which content in matrix is None
        :return: Point
        """
        if not empty_point:
            return Point(secrets.randbelow(self._cols), secrets.randbelow(self._rows))
        else:
            if len(self.__empty) == 0:
                return None
            return random.choice(self.__empty)
