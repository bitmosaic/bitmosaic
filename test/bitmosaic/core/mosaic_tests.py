# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# mosaic_tests.py is part of Bitmosaic.
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
import bitmosaic.core.data_domain as data_domain
import bitmosaic.core.filler as filler
import bitmosaic.core.matrix as matrix
import bitmosaic.core.mosaic as mosaic
import bitmosaic.core.secret as secret
import bitmosaic.drawing.color as color
import bitmosaic.util as util


class TestTessera(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        first_component = matrix.V2Component(label="a", value=2)
        second_component = matrix.V2Component(label="b", value=5)
        v2_point = matrix.V2Point(x=first_component, y=second_component)
        self.tessera = mosaic.Tessera(position=matrix.Point(x=1, y=2), data="First", v2_point=v2_point)

    def test_str(self) -> None:
        self.assertEqual(str(self.tessera), "Firstab|")

    def test_next(self) -> None:
        self.assertEqual(self.tessera.next(), matrix.Point(3, 7))

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestMosaic(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        self.rows = 12
        self.cols = 24
        regex = "^[a-zA-Z]+$"
        regex_domain = data_domain.RegexDomain(regex)
        self.domain = data_domain.Domain()
        self.domain.add(regex_domain)
        self.domain.generate_domain(total_items=self.rows * self.cols)
        self.components = matrix.V2Component.components_from_string("a:1 b:2 c:3")
        self.secret1 = secret.Secret(name="My secret", data=["my", "secret", "data"], origin=matrix.Point.zero(),
                                     v2_components=self.components)
        self.secret2 = secret.Secret(name="My secret 2", data=["this", "is", "my", "other", "secret"],
                                     origin=matrix.Point.random(values=range(10)), v2_components=self.components)

        self.vault = secret.Vault()
        self.vault.add_secret(self.secret1)
        self.vault.add_secret(self.secret2)

        self.landspcape_image_filler = filler.ImageFiller(cols=self.cols, rows=self.rows, image_name="landscape.jpg")
        self.landscape_image_mosaic = mosaic.Mosaic(domain=self.domain, color_filler=self.landspcape_image_filler)

        self.portrait_image_filler = filler.ImageFiller(cols=self.cols, rows=self.rows, image_name="portrait.jpg")
        self.portrait_image_mosaic = mosaic.Mosaic(domain=self.domain, color_filler=self.portrait_image_filler)

        self.square_image_filler = filler.ImageFiller(cols=self.cols, rows=self.rows, image_name="square.png")
        self.square_image_mosaic = mosaic.Mosaic(domain=self.domain, color_filler=self.square_image_filler)

        self.palette_filler = filler.PaletteFiller(cols=self.cols, rows=self.rows, palette=color.Palette.sample())
        self.mosaic_from_palette = mosaic.Mosaic(domain=self.domain, color_filler=self.palette_filler)

    def test_landscape_image_mosaic_size(self) -> None:
        self.assertLessEqual(self.landscape_image_mosaic.cols, max(self.cols, self.rows))
        self.assertLessEqual(self.landscape_image_mosaic.rows, max(self.cols, self.cols))

    def test_portrait_image_mosaic_size(self) -> None:
        self.assertLessEqual(self.portrait_image_mosaic.cols, max(self.cols, self.rows))
        self.assertLessEqual(self.portrait_image_mosaic.rows, max(self.cols, self.rows))

    def test_square_image_mosaic_size(self) -> None:
        self.assertEqual(self.square_image_mosaic.cols, self.square_image_mosaic.rows)
        self.assertLessEqual(self.square_image_mosaic.cols, max(self.cols, self.rows))
        self.assertLessEqual(self.square_image_mosaic.rows, max(self.cols, self.rows))

    def test_palette_mosaic_size(self) -> None:
        self.assertEqual(len(self.mosaic_from_palette), self.rows * self.cols)

    def test_mosaic_data(self) -> None:
        for row in range(0, self.landscape_image_mosaic.rows):
            for col in range(0, self.landscape_image_mosaic.cols):
                self.assertIsNone(self.landscape_image_mosaic.get_tessera(matrix.Point(col, row)))

    def test_mosaic_color(self) -> None:
        for row in range(0, self.landscape_image_mosaic.rows):
            for col in range(0, self.landscape_image_mosaic.cols):
                self.assertIsInstance(self.landscape_image_mosaic.get_color(matrix.Point(col, row)), color.Color)

    def test_hide_secret(self) -> None:
        self.vault.remove_secret(self.secret2)
        self.landscape_image_mosaic.hide_secrets(vault=self.vault)
        for row in range(0, self.landscape_image_mosaic.rows):
            for col in range(0, self.landscape_image_mosaic.cols):
                self.assertIsNotNone(self.landscape_image_mosaic.matrix.get_item(matrix.Point(col, row)))

    def test_hide_two_secret(self) -> None:
        self.landscape_image_mosaic.hide_secrets(vault=self.vault)
        for row in range(0, self.landscape_image_mosaic.rows):
            for col in range(0, self.landscape_image_mosaic.cols):
                self.assertIsNotNone(self.landscape_image_mosaic.matrix.get_item(matrix.Point(col, row)))

    def test_recover_secret(self) -> None:
        self.landscape_image_mosaic.hide_secrets(vault=self.vault)
        recovery = secret.Recovery(name="Recovering secret 1", origin=self.secret1.origin,
                                   v2_components=self.secret1.components, cols=self.cols, rows=self.rows, length=3)
        self.assertEqual(self.landscape_image_mosaic.recover_secret(recovery=recovery).data, ["my", "secret", "data"])

    def test_recover_secret_2(self) -> None:
        self.landscape_image_mosaic.hide_secrets(vault=self.vault)
        recovery = secret.Recovery(name="Recovering secret 2", origin=self.secret2.origin,
                                   v2_components=self.secret2.components, cols=self.cols, rows=self.rows, length=5)
        self.assertEqual(self.landscape_image_mosaic.recover_secret(recovery=recovery).data,
                         ["this", "is", "my", "other", "secret"])

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()
