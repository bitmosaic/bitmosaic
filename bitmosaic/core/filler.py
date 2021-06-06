# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# filler.py is part of Bitmosaic.
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

import abc
import os
import random
import bitmosaic.util as util
from PIL import Image
from bitmosaic.drawing.color import Color
from bitmosaic.drawing.color import Palette
from bitmosaic.drawing.color import RGBAColor
from bitmosaic.exception import FileException
from bitmosaic.exception import InvalidFormatException
from bitmosaic.exception import NoImageSelectedException

# from bitmosaic.core.secret import Recovery
# from bitmosaic.core.mosaic import Tessera


class MatrixFiller(abc.ABC):
    """
    Filler interface.

    Methods
    -------
    get_item() -> object
        returns an object to use as fill for matrix initialization
    """

    @abc.abstractmethod
    def get_item(self, point: tuple = None) -> object:
        pass


class NoneFiller(MatrixFiller):
    """
    Used to fill a matrix with None.

    Methods
    -------
    get_item() -> object
        returns None as value for matrix initialization

    """

    def __init__(self):
        self._name = "NoneFiller"

    def get_item(self, point: tuple = None) -> object:
        """
        Returns None to initialize matrix content.

        :return: None
        """
        return None


class ColorFiller(MatrixFiller):
    """
    Used to fill a matrix with RGBAColor.

    Properties
    ----------
    cols : int
        returns the number of cols or None if not necessary

    rows : int
        returns the number of rows or None if not necessary

    Methods
    -------
    get_item() -> object
        returns a random RGBAColor as value for matrix initialization

    """

    @property
    def cols(self) -> int:
        return self._cols

    @property
    def rows(self) -> int:
        return self._rows

    def __init__(self, name: str, cols: int, rows: int):
        """
        :param str name: the name for the filler
        :param int cols: the number of cols
        :param int rows: the number of cols
        """
        self._name = name
        self._cols = cols
        self._rows = rows

    def get_item(self, point: tuple = None) -> Color:
        """
        Returns a random RGBAColor to initialize the matrix content.

        :return: Color
        """
        return RGBAColor.random()


class PaletteFiller(ColorFiller):
    """
    Used to fill a matrix with colors from a palette.

    Properties
    ----------
    cols : int
        returns the number of cols or None if not necessary

    rows : int
        returns the number of rows or None if not necessary

    Methods
    -------
    get_item() -> object
        returns a random RGBAColor from the palette

    """

    def __init__(self, cols: int, rows: int, palette=Palette.sample()):
        """
        :param int cols: the number of cols
        :param int rows: the number of cols
        :param Palette palette: the palette used as color source
        """
        super().__init__(name="PaletteFiller", cols=cols, rows=rows)
        self._palette = palette

    def get_item(self, point: tuple = None) -> Color:
        """
        Returns a random Color to initialize the matrix content.

        :return: Color
        """
        return self._palette.random()


class ImageFiller(ColorFiller):
    """
    Used to fill a matrix with colors from image.

    Properties
    ----------
    cols : int
        returns the number of cols or None if not necessary

    rows : int
        returns the number of rows or None if not necessary

    Methods
    -------
    get_item() -> object
        returns a random HtmlColor as value for matrix initialization

    """

    __valid_image_formats = ("GIF", "JPEG", "PNG")

    def __init__(self, cols: int, rows: int, image_name: str):
        """
        :param int cols: the number of cols
        :param int rows: the number of cols
        :param str image_name: the name of the image used as color source
        """
        super().__init__(name="ImageFiller", cols=cols, rows=rows)
        self._image_path = util.get_image_input_directory(image_name)
        self._resized_image = None
        self.__resize_image()

    def __resize_image(self):
        if self._image_path is None:
            raise NoImageSelectedException("No image was selected")
        try:
            image = Image.open(self._image_path)
            if image.format not in self.__valid_image_formats:
                extension = os.path.splitext(self._image_path)[1]
                raise InvalidFormatException(extension, "The image format is not valid")

            width, height = image.size
            cols = width / self._cols
            rows = height / self._rows
            if width >= height:
                self._cols = round(width / cols)
                self._rows = round(height / cols)
            else:
                self._rows = round(height / rows)
                self._cols = round(width / rows)
            self._resized_image = image.resize((self._cols, self._rows), Image.BILINEAR)
        except IOError:
            raise FileException(self._image_path, "There was a problem with the image file")

    def get_item(self, point: tuple = None) -> Color:
        """
        Overrides parent get_item().

        Returns the RGBAColor for the pixel in the point position

        :param Point point: an optional point
        :return: Color
        """

        if point is None:
            return RGBAColor.random()

        if self._resized_image is not None:
            pixel = self._resized_image.getpixel(point)
            color = RGBAColor(pixel[0], pixel[1], pixel[2])
        else:
            color = RGBAColor(255, 153, 0)
        return color


class RecoveryFiller(MatrixFiller):
    """
    Used to fill a matrix with colors from a palette.

    Properties
    ----------
    cols : int
        returns the number of cols or None if not necessary

    rows : int
        returns the number of rows or None if not necessary

    recovery : Recovery
        the Recovery object needed to make the tesserae

    bitmosaic_data : str
        the raw data of bitmosaic

    Methods
    -------
    get_item(point: tuple) -> object
        returns the object at point

    """

    def __init__(self, cols: int, rows: int, recovery: object, bitmosaic_data: str):
        """
        :param int cols: the number of cols
        :param int rows: the number of cols
        :param Recovery recovery: the recovery info used to create the tesserae
        :param bitmosaic_data: the raw data of bitmosaic
        """
        self._name = "RecoveryFiller"
        self._cols = cols
        self._rows = rows
        self._recovery = recovery
        self._bitmosaic_data = bitmosaic_data
        self.__matrix = []
        self.__setup_matrix()

    def __setup_matrix(self):
        from bitmosaic.core.mosaic import Tessera
        from bitmosaic.core.matrix import Point
        splitted_data = self._bitmosaic_data.split("|")
        for index in range(self._cols * self._rows):
            raw_secret = splitted_data[index]
            row = index // self._cols
            col = index if index < self._cols else index % self._cols
            try:
                tessera = Tessera.init_for_recovery(Point(col, row), raw_secret, self._recovery.components)
            except Exception as e:
                a = index
                pass
            self.__matrix.append(tessera)
        pass

    def get_item(self, point: tuple = None) -> object:
        """
        Returns the item at point.

        :return: object
        """
        if point is None:
            return random.choice(self.__matrix)
        index = point[1] * self._cols + point[0]
        return self.__matrix[index]
