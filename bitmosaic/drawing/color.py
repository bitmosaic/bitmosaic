# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# color.py is part of Bitmosaic.
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
# along with BitmosaicI. If not, see <https://www.gnu.org/licenses/>.

import abc
import colorsys
import random
import re
from bitmosaic.exception import InvalidColorException


class Color(abc.ABC):
    """
    Interface for Color objects.
    """

    @property
    @abc.abstractmethod
    def r(self):
        pass

    @property
    @abc.abstractmethod
    def g(self):
        pass

    @property
    @abc.abstractmethod
    def b(self):
        pass

    @abc.abstractmethod
    def contrasted_color(self):
        pass

    @classmethod
    @abc.abstractmethod
    def random(cls):
        pass

    @abc.abstractmethod
    def tuple(self):
        pass


class HtmlColor(Color):

    """
    Defines html color objects.

    Attributes
    ----------

    code : str
        returns the string for the color in hex format, starting with '#'

    r : str
        returns the red value for the color, in hex format

    g : str
        returns the green value for the color, in hex format

    b : str
        returns the blue value for the color, in hex format

    Methods
    -------

    contrasted_color() -> Color
        returns a black or white color contrasting with current color

    rgba_color() -> Color
        returns the color as RGBAColor object

    tuple() -> tuple
        returns the rgb values as tuple (r, g, b), in decimal format

    Class Methods
    -------------

    is_valid(hex_code: str) -> bool
        checks if the hex_code is a valid html color

    random() -> Color
        returns a random HtmlColor

    """

    @property
    def code(self) -> str:
        return str(self)

    @property
    def r(self) -> str:
        return self._code[0:2]

    @property
    def g(self) -> str:
        return self._code[2:4]

    @property
    def b(self) -> str:
        return self._code[4:6]

    def __init__(self, hex_code: str):
        """
        :param str hex_code: the hex code for the color
        :raises InvalidColorException:
        """
        self._code = None
        if self.is_valid(hex_code):
            try:
                self._code = self._six_digits_code(hex_code)
            except InvalidColorException as e:
                raise e
        else:
            raise InvalidColorException(hex_code, "The hex code for color is not valid")

    def __eq__(self, other) -> bool:
        return self.code == other.code

    def __len__(self) -> int:
        return len(self._code)

    def __repr__(self) -> str:
        return "HtmlColor({0})".format("#" + self._code or "None")

    def __str__(self) -> str:
        return "#" + self._code or "None"

    def contrasted_color(self) -> Color:
        """
        Returns black or white color, the one with the most contrasts with the current color.

        :return: Color
        """
        color = "#000" if (int(self.r, 16) % 255 + int(self.g, 16) % 255 + int(self.b, 16)) / 3 > 128 else "#FFF"
        return HtmlColor(color)

    def rgba_color(self, alpha: int = 255) -> Color:
        """
        Returns the current color in rgba format.

        :param int alpha: the alpha value for the color
        :return: Color
        """
        return RGBAColor(int(self.r, 16), int(self.g, 16), int(self.b, 16), alpha)

    def tuple(self) -> tuple:
        """
        Returns a tuple with the r, g and b values of the current color; in decimal format.

        :return: tuple
        """
        rgb = self.rgba_color()
        return rgb.r, rgb.g, rgb.b

    @staticmethod
    def _six_digits_code(code: str) -> str:
        """
        Returns de color code without the "#". Completes to 6 characters when color format is 3 characters only.

        :param str code: the html color code
        :raises InvalidColorException:
        :return: str
        """
        temp_code = code.lstrip("#")
        if len(temp_code) == 3:
            r = temp_code[0] * 2
            g = temp_code[1] * 2
            b = temp_code[2] * 2
            return (r + g + b).upper()
        elif len(temp_code) == 6:
            return temp_code
        else:
            raise InvalidColorException(code, "The code for this color is not valid")

    @classmethod
    def is_valid(cls, hex_code) -> bool:
        """
        Checks if the hex_code is a valid html color code.

        :param str hex_code: the html color code to check
        :returns: bool
        """
        result = False
        if len(hex_code) == 4 or len(hex_code) == 7:
            regexp = "^#[0-9A-Fa-f]{{{0}}}$".format(len(hex_code) - 1)
            match = re.search(regexp, hex_code)
            result = True if match else False
        return result

    @classmethod
    def random(cls) -> Color:
        """
        Returns a random html color between #000000 and #FFFFFF.

        :return: Color
        """
        min_hex_code = 0
        max_hex_code = int("FFFFFF", 16)
        rand = hex(random.randint(min_hex_code, max_hex_code))
        hex_code = "".join(["#", "{0}".format(rand.upper()[2:]).zfill(6)])
        return cls(hex_code)


class RGBAColor(Color):
    """
    Defines rgba color objects.

    Attributes
    ----------

    r : int
        returns the red value for the color

    g : int
        returns the green value for the color

    b : int
        returns the blue value for the color

    a : int
        returns the alpha value for the color


    Methods
    -------

    contrasted_color() -> Color
        returns a black or white color contrasting with current color

    html_color() -> Color
        returns the color as HtmlColor object

    tuple() -> tuple
        returns the rgb values as tuple (r, g, b)

    Class Methods
    -------------

    random() -> Color
        returns a random RGBAColor

    """

    @property
    def r(self):
        return self._r

    @property
    def g(self):
        return self._g

    @property
    def b(self):
        return self._b

    @property
    def a(self):
        return self._a

    def __init__(self, r: int, g: int, b: int, a: int = 255):
        """
        :param int r: the red value
        :param int g: the green value
        :param int b: the blue value
        :param int a: the alpha value
        """
        self._r = r % 256
        self._g = g % 256
        self._b = b % 256
        self._a = a % 256

    def __eq__(self, other) -> bool:
        return str(self) == str(other)

    def __repr__(self) -> str:
        return "RGBAColor({0}, {1}, {2}, {3})".format(self._r, self._g, self._b, self._a)

    def __str__(self) -> str:
        return "r: {0}, g: {1}, b: {2}, a: {3}".format(self._r, self._g, self._b, self._a)

    def contrasted_color(self) -> Color:
        """
        Returns black or white color, the one with the most contrasts with the current color.

        :return: Color
        """
        value = 0 if (self._r + self._g + self._b) / 3 > 128 else 255
        return RGBAColor(value, value, value)

    def html_color(self) -> Color:
        """
        Returns the current color in html format.

        :return: Color
        """
        return HtmlColor("#{:02x}{:02x}{:02x}".format(self.r % 256, self.g % 256, self.b % 256).upper())

    def tuple(self):
        """
        Returns a tuple with the r, g and b values of the current color.

        :return: tuple
        """
        return self._r, self._g, self._b

    @classmethod
    def random(cls) -> Color:
        """
        Returns a random rgb color.

        :return: Color
        """
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        return cls(r, g, b)


class Palette:

    """
    Represents a color palette.

    Properties
    ----------
    colors : [Color]
        returns the color list of the palette

    Methods
    -------
    add_color(color: Color)
        adds a color to the palette

    add_colors(colors: [Color])
        adds a list of colors to the palette

    remove_color(color: Color)
        removes a color from the palette

    random()
        returns a random color from the palette

    """

    @property
    def colors(self) -> [Color]:
        return self._colors

    def __init__(self):
        self._colors = []

    def __len__(self):
        return len(self._colors)

    def __repr__(self):
        return "Palette({0})".format(self._colors)

    def __str__(self):
        return "{0}".format(self._colors)

    def add_color(self, color: Color):
        if type(color) is RGBAColor:
            color = color.html_color()
        elif type(color) is str:
            if HtmlColor.is_valid(color):
                color = HtmlColor(color)
        if color not in self._colors:
            self._colors.append(color)

    def add_colors(self, colors: [Color]):
        for color in colors:
            self.add_color(color)

    def remove_color(self, color: Color):
        if type(color) is RGBAColor:
            color = color.html_color()
        elif type(color) is str:
            if HtmlColor.is_valid(color):
                color = HtmlColor(color)
        if color in self._colors:
            self._colors.remove(color)

    def random(self) -> Color:
        """
        Returns a random color from the palette.

        :return: Color
        """
        return random.choice(self._colors)

    @classmethod
    def sample(cls) -> 'Palette':
        """
        Returns a sample palette.

        :returns: Palette
        """
        unicorn = ["#F3BC50", "#25C0C0", "#FA53A0", "#FC8BC0"]
        palette = cls()
        palette.add_colors(unicorn)
        return palette

    @classmethod
    def similar_colors(cls, color: Color, number: int = 5) -> [Color]:
        """
        Returns a list of similar colors to the given color.

        :param Color color: the main color
        :param int number: the length of the result list
        :return: [Color]
        """
        if type(color) is HtmlColor:
            color = color.rgba_color()
        colors = [color]
        for i in range(number - 1):
            h, s, v = colorsys.rgb_to_hsv(color.r, color.g, color.b)
            s = random.uniform(h - (1 / number * i + 1), h + (1 / number * (i + 1)))
            v = random.uniform(0.945, 1)
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            new_color = RGBAColor(round(r * 255), round(g * 255), round(b * 255))
            colors.append(new_color)
        return colors
