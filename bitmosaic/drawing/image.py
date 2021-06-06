# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# image.py is part of Bitmosaic.
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

import bitmosaic.util as util
from enum import Enum
from enum import auto
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from bitmosaic.drawing.color import Color
from bitmosaic.drawing.color import RGBAColor
from bitmosaic.core.matrix import Point
from bitmosaic.core.mosaic import Mosaic
from bitmosaic.core.mosaic import Tessera
from bitmosaic.core.secret import Recovery


class Margin:
    top: int = 20
    right: int = 20
    bottom: int = 20
    left: int = 20


class Frame:
    color: Color = RGBAColor(60, 60, 60)
    border_width: int = 1
    border_color: Color = RGBAColor(50, 50, 50)
    text_color = color.contrasted_color()
    show_text = True


class FramePosition(Enum):
    none = auto()
    top = auto()
    right = auto()
    bottom = auto()
    left = auto()
    corner = auto()


class Bitmosaic:

    """
    This class creates and saves the bitmosaic image.

    Attributes
    ----------
    mode : str
        the image mode, default is RGB
    dpi : int
        the resolution for the resulting image (dots per inch)
    color : Color
        the background color for the image
    framed : bool
        indicates if the bitmosaic has a frame with col and row numbers
    tessera_side : int
        the side in pixels for the tessera
    tessera_border_width:
        the width in pixels for the tessera border
    tessera_border_color : Color
        the tessera's border's color
    coordinates : bool
        indicates if the tessera content should show the tessera's coordinates

    Properties
    ----------

    border_correction : int
        necessary to apply a correction to the outter tesserae border
    cols : int
        the number of cols for the bitmosaic
    width : int
        the image width
    height : int
        the image height
    size_in_inches : str
        the image size in inches
    size_in_cms : str
        the image size in centimeters

    Methods
    -------

    save():
        saves the bitmosaic image and extra files (when needed)

    """

    mode = "RGB"
    dpi = 150
    color = RGBAColor(255, 153, 0)
    framed = True
    tessera_side = 150
    tessera_border_width = 1
    tessera_border_color = RGBAColor(50, 50, 50)
    coordinates = True

    @property
    def border_correction(self) -> int:
        return Frame.border_width if self.framed else self.tessera_border_width

    @property
    def cols(self) -> int:
        return self._mosaic.cols + (2 if self.framed else 0)

    @property
    def rows(self) -> int:
        return self._mosaic.rows + (2 if self.framed else 0)

    @property
    def width(self) -> int:
        return Margin.left + Margin.right + self.cols * self.tessera_side + self.border_correction * 2

    @property
    def height(self) -> int:
        return Margin.top + Margin.bottom + self.rows * self.tessera_side + self.border_correction * 2

    @property
    def size_in_inches(self) -> str:
        return "{0}x{1} inches".format(round(self.width / self.dpi, 2), round(self.height / self.dpi, 2))

    @property
    def size_in_cms(self) -> str:
        return "{0}x{1} cms".format(round(self.width / self.dpi * 2.54, 2), round(self.height / self.dpi * 2.54, 2))

    def __init__(self, mosaic: Mosaic):
        """
        :param Mosaic mosaic: the source mosaic to create the bitmosaic.
        """
        self._mosaic = mosaic

    def __repr__(self):
        return "Bitmosaic(mode: {0}, dpi: {1}, color: {2}, framed: {3}, tessera_side: {4}, tessera_border_width: {5)," \
               " tessera_border_color: {6}, coordinates: {7}".format(self.mode, self.dpi, self.color, self.framed,
                                                                     self.tessera_side, self.tessera_border_width,
                                                                     self.tessera_border_color, self.coordinates)

    def __str__(self):
        return str(self._mosaic)

    def save(self, bitmosaic_txt=True, recovery_txt = True, recovery_cards=True):
        """
        Saves the files for the bitmosaic.

        :param bool bitmosaic_txt: to save the bitmosaic as text file.
        :param bool recovery_txt: to save the recovery info as text file.
        :param bool recovery_cards: to save the recovery cards.
        """
        self.__draw()
        self.__save_txt(bitmosaic=bitmosaic_txt, recovery=recovery_txt)
        if recovery_cards:
            self.__save_recovery_cards()

    def __draw(self):
        """
        Draws an saves a bitmosaic png file.
        """
        size = (self.width, self.height)

        image = Image.new(self.mode, size, self.color.tuple())
        draw = ImageDraw.Draw(image, self.mode)

        font_file = util.get_fonts_directory("Code2003-W8nn.ttf")
        font = ImageFont.truetype(font_file, round((self.tessera_side - self.tessera_border_width * 2) / 10))

        for col in range(self.cols):
            for row in range(self.rows):
                tessera = self._mosaic.get_tessera(Point(col, row))
                color = self._mosaic.get_color(Point(col, row))
                self.__draw_in_content(tessera, color, draw, font)

        if self.framed:
            for col in range(-1, self.cols - 1):
                self.__draw_in_frame(col, 0, FramePosition.top, draw, font)
                self.__draw_in_frame(col, self.rows, FramePosition.bottom, draw, font)
            for row in range(0, self.rows - 2):
                self.__draw_in_frame(0, row, FramePosition.left, draw, font)
                self.__draw_in_frame(self.cols, row, FramePosition.right, draw, font)

        file = util.get_output_directory("bitmosaic.png")
        image.save(str(file), dpi=(self.dpi, self.dpi))

    def __save_txt(self, bitmosaic=True, recovery=True):
        """
        Saves the bitmosaic as txt file and the recovery info for the mosaic's secrets.
        """
        if bitmosaic:
            with open(util.get_output_directory("bitmosaic.txt"), "w", encoding="utf-8") as file:
                file.write(str(self))

        if recovery:
            for recovery_info in self._mosaic.recoveries:
                with open(util.get_output_directory("recovery_{0}.txt".format(recovery_info.name).replace(" ", "_")),
                          "w", encoding="utf-8") as file:
                    file.write(str(recovery_info))

    def __save_recovery_cards(self):
        """
        Saves the recovery cards as png images.
        """
        for recovery_info in self._mosaic.recoveries:
            self.__draw_recovery_card(recovery_info)

    def __draw_in_content(self, tessera: Tessera, color: Color, draw: ImageDraw, font: ImageFont):
        """
        Draws a tessera in the content zone of the bitmosaic image.

        :param Tessera tessera: the tessera to draw.
        :param Color color: the image background color.
        :param ImageDraw draw: the image draw where the tessera will be drawn.
        :param ImageFont font: the font used to write the tessera's content.
        """
        # Drawing the border
        border_start = self.__point_in_content(tessera.position)
        border_end = border_start + Point(self.tessera_side - 1, self.tessera_side - 1)
        border_color = self.tessera_border_color.tuple() or None
        draw.rectangle([border_start.tuple(), border_end.tuple()], border_color)

        # Drawing the fill
        border_point = Point(self.tessera_border_width, self.tessera_border_width)
        fill_start = border_start + border_point if self.tessera_border_color is not None else border_start
        fill_end = border_end - border_point if self.tessera_border_color is not None else border_end
        fill_color = color.tuple() or None
        draw.rectangle([fill_start.tuple(), fill_end.tuple()], fill_color)

        # Drawing the tessera content
        text = "{0}\n\n{1}\n\n{2}".format(tessera.position if self.coordinates else "", tessera.data,
                                          tessera.v2_point.labels())
        text_size = draw.multiline_textbbox((fill_start.x, fill_start.y), text, font)
        text_x = fill_start.x + self.tessera_side / 2 - self.tessera_border_width - (text_size[2] - text_size[0]) / 2
        text_y = fill_start.y + self.tessera_side / 2 - self.tessera_border_width - (text_size[3] - text_size[1]) / 2
        text_point = Point(text_x, text_y)
        text_color = color.contrasted_color().tuple() or None
        draw.multiline_text(text_point.tuple(), text, fill=text_color, font=font, align="center")

    def __draw_in_frame(self, col: int, row: int, position: FramePosition, draw: ImageDraw, font: ImageFont):
        """
        Draws a tessera in the frame zone of the bitmosaic image.

        :param int col: the col for the tessera.
        :param int row: the row for the tessera.
        :param FramePosition position: the position in the frame.
        :param ImageDraw draw: the image draw where the tessera will be drawn.
        :param ImageFont font: the font used to write the tessera's content.
        """
        # Drawing the border
        border_start = self.__point_in_frame(Point(col, row), position)
        border_end = border_start + Point(self.tessera_side - 1, self.tessera_side - 1)
        border_color = None if Frame.border_color is None else Frame.border_color.tuple()
        draw.rectangle([border_start.tuple(), border_end.tuple()], border_color)

        # Drawing the fill
        border_point = Point(Frame.border_width, Frame.border_width)
        fill_start = border_start + border_point if Frame.border_color is not None else border_start
        fill_end = border_end - border_point if Frame.border_color is not None else border_end
        background_color = None if Frame.color is None else Frame.color.tuple()
        draw.rectangle([fill_start.tuple(), fill_end.tuple()], background_color)

        # Drawing the tessera content
        if Frame.show_text:
            if col == -1 or col == self.cols - 2:
                text = ""
            else:
                text = "\n\n{0}\n\n".format(
                    col if position == FramePosition.top or position == FramePosition.bottom else row)

            text_size = draw.multiline_textbbox((fill_start.x, fill_start.y), text, font)
            text_x = fill_start.x + self.tessera_side / 2 - self.tessera_border_width - (
                        text_size[2] - text_size[0]) / 2
            text_y = fill_start.y + self.tessera_side / 2 - self.tessera_border_width - (
                        text_size[3] - text_size[1]) / 2
            text_point = Point(text_x, text_y)
            text_color = None if Frame.text_color is None else Frame.text_color.tuple()
            draw.multiline_text(text_point.tuple(), text, fill=text_color, font=font, align="center")

    def __draw_recovery_card(self, recovery_info: Recovery, dpi=150, width_inches=2.5, height_inches=3.5):
        """
        Saves the recovery info as image.

        :param Recovery recovery_info: the recovery information to save as image.
        :param int dpi: the resolution in dots per inch.
        :param int width_inches: the width for the image (in inches).
        :param int height_inches: the height for the image (in inches).
        """
        border_margin = 20
        border_width = 2
        width = round(width_inches * dpi)
        height = round(height_inches * dpi)
        size = (width, height)
        mode = "RGB"
        background_color = RGBAColor(255, 255, 255)
        image = Image.new(mode, size, background_color.tuple())
        draw = ImageDraw.Draw(image, mode)
        font_file = util.get_fonts_directory("Code2003-W8nn.ttf")
        font = ImageFont.truetype(font_file, round(width / 25))

        border_start = Point(border_margin, border_margin)
        border_end = Point(width - border_margin, height - border_margin)
        border_color = RGBAColor(0, 0, 0)
        draw.line((border_start.tuple(),
                   (width - border_margin, border_margin),
                   border_end.tuple(),
                   (20, height - border_margin),
                   border_start.tuple()),
                  border_color.tuple(), border_width)

        text_margin = 22
        text_start = Point(text_margin, text_margin)
        text_end = Point(width - text_margin, height - text_margin)
        text_color = RGBAColor(0, 0, 0)
        text = recovery_info.card()
        text_size = draw.multiline_textbbox(text_start.tuple(), text, font)
        text_x = (text_end.x - text_start.x) / 2 - (text_size[2] - text_size[0]) / 2 + text_margin
        text_y = (text_end.y - text_start.y) / 2 - (text_size[3] - text_size[1]) / 2 + text_margin
        text_point = Point(text_x, text_y)
        draw.multiline_text(text_point.tuple(), text, fill=text_color.tuple(), font=font, align="center")
        image.save(util.get_output_directory("recovery_{0}.png".format(recovery_info.name).replace(" ", "_")),
                   dpi=(dpi, dpi))

    def __point_in_frame(self, point: Point, position: FramePosition) -> Point:
        """
        Gets the x and y image coordinates for a point in the frame

        :param Point point: the point.
        :param FramePosition position: the position in the frame.
        :return: Point
        """
        if position == FramePosition.top:
            x = Margin.left + point.x * self.tessera_side + self.tessera_side + self.border_correction
            y = Margin.top + point.y + self.border_correction
        elif position == FramePosition.right:
            x = self.width - Margin.right - self.tessera_side - self.border_correction
            y = Margin.top + point.y * self.tessera_side + self.tessera_side + self.border_correction
        elif position == FramePosition.bottom:
            x = Margin.left + point.x * self.tessera_side + self.tessera_side + self.border_correction
            y = self.height - Margin.bottom - self.tessera_side - self.border_correction
        else:
            x = Margin.left + self.border_correction
            y = Margin.top + point.y * self.tessera_side + self.tessera_side + self.border_correction
        return Point(x, y)

    def __point_in_content(self, point: Point) -> Point:
        """
        Gets the x and y image coordinates for a point in the image content (not frame)

        :param Point point: the point.
        :return: Point
        """
        x = Margin.left + self.border_correction + (self.tessera_side if self.framed else 0) + point.x * self.tessera_side
        y = Margin.top + self.border_correction + (self.tessera_side if self.framed else 0) + point.y * self.tessera_side
        return Point(x, y)




