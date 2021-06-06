# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# color_tests.py is part of Bitmosaic.
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

import unittest
import bitmosaic.drawing.color as color
import bitmosaic.util as util


class TestHtmlColor(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        # Test colors
        self.html_color_0 = color.HtmlColor("#000000")
        self.html_color_1 = color.HtmlColor("#AABBCC")
        self.html_color_2 = color.HtmlColor("#ABC")
        self.rgba_color_1 = color.RGBAColor(170, 187, 204)
        # Expected values
        self.expected_contrasted_color = "#FFFFFF"

    def test_valid_color(self) -> None:
        self.assertFalse(color.HtmlColor.is_valid("#GGAABB"))
        self.assertFalse(color.HtmlColor.is_valid("00AABB"))
        self.assertFalse(color.HtmlColor.is_valid("GGAABB"))
        self.assertTrue(color.HtmlColor.is_valid("#AABBCC"))
        self.assertTrue(color.HtmlColor.is_valid("#ABC"))

    def test_len(self) -> None:
        self.assertEqual(len(self.html_color_1), 6)
        self.assertEqual(len(self.html_color_2), 6)

    def test_color_equity(self) -> None:
        self.assertEqual(self.html_color_1, self.html_color_2)
        self.assertEqual(self.html_color_1, self.rgba_color_1.html_color())

    def test_color_as_str(self) -> None:
        self.assertEqual(self.html_color_1.code, "#AABBCC")
        self.assertEqual(self.html_color_2.code, "#AABBCC")

    def test_contrasted_color(self) -> None:
        self.assertEqual(self.html_color_0.contrasted_color().code, self.expected_contrasted_color)

    def test_random_color(self) -> None:
        random_color = color.HtmlColor.random()
        self.assertIsNotNone(random_color)
        self.assertNotEqual(random_color.code, "None")


class TesRgbaColor(unittest.TestCase):
    def setUp(self) -> None:
        # Test colors
        self.rgba_color_0 = color.RGBAColor(0, 0, 0)
        self.rgba_color_1 = color.RGBAColor(170 + 256, 187 + 256, 204 + 256)
        self.rgba_color_2 = color.RGBAColor(170, 187, 204)
        self.rgba_color_3 = color.RGBAColor(170, 187, 204)
        self.html_color_1 = color.HtmlColor("#AABBCC")
        # Expected values
        self.expected_rgba_color_str = "r: 170, g: 187, b: 204, a: 255"
        self.expected_contrasted_color = "r: 255, g: 255, b: 255, a: 255"

    def test_color_creation(self) -> None:
        self.assertEqual(self.rgba_color_1, self.rgba_color_2)

    def test_color_equity(self) -> None:
        self.assertEqual(self.rgba_color_2, self.rgba_color_3)

    def test_color_as_str(self) -> None:
        self.assertEqual(str(self.rgba_color_2), self.expected_rgba_color_str)

    def test_contrasted_color(self) -> None:
        self.assertEqual(str(self.rgba_color_0.contrasted_color()), self.expected_contrasted_color)

    def test_random_color(self) -> None:
        random_color = color.RGBAColor.random()
        self.assertIsNotNone(random_color)


class TestPalette(unittest.TestCase):
    def setUp(self) -> None:
        # Test colors
        self.rgba_color = color.RGBAColor(0, 255, 0)
        self.html_color = color.HtmlColor("#00FF00")
        self.rgba_similar_colors = None
        self.html_similar_colors = None
        self.number_of_colors = 10

    def test_similar_colors_from_rgb(self) -> None:
        self.rgba_similar_colors = color.Palette.similar_colors(self.rgba_color, self.number_of_colors)
        palette = color.Palette()
        palette.add_colors(self.rgba_similar_colors)
        self.assertIsNotNone(palette)
        self.assertEqual(len(palette), self.number_of_colors)

    def test_similar_colors_from_html(self) -> None:
        self.html_similar_colors = color.Palette.similar_colors(self.html_color, self.number_of_colors)
        palette = color.Palette()
        palette.add_colors(self.html_similar_colors)
        self.assertIsNotNone(palette)
        self.assertEqual(len(palette), self.number_of_colors)

    def test_add_color_as_str(self) -> None:
        palette = color.Palette()
        palette_length = len(palette)
        palette.add_color("#000000")
        self.assertEqual(len(palette), palette_length + 1)

    def test_remove_color_as_str(self) -> None:
        self.rgba_similar_colors = color.Palette.similar_colors(self.rgba_color, self.number_of_colors)
        palette = color.Palette()
        palette.add_colors(self.rgba_similar_colors)
        palette_length = len(palette)
        palette.remove_color(palette.colors[0])
        self.assertEqual(len(palette), palette_length - 1)

    def test_equal_similar_colors(self) -> None:
        self.assertEqual(self.rgba_similar_colors, self.html_similar_colors)

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()
