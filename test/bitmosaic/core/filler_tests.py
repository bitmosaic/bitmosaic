# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# filler_tests.py is part of Bitmosaic.
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
import bitmosaic.drawing.image as image
import bitmosaic.util as util


class TestNoneFiller(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        self.filler = filler.NoneFiller()

    def test_get_item(self) -> None:
        self.assertIsNone(self.filler.get_item())

    def test_get_item_at_point(self) -> None:
        point = matrix.Point.zero().tuple()
        self.assertIsNone(self.filler.get_item(point))

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestColorFiller(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        self.filler = filler.ColorFiller(name="ColorFiller", cols=0, rows=0)

    def test_get_item(self) -> None:
        self.assertIsInstance(self.filler.get_item(), color.Color)

    def test_get_item_at_point(self) -> None:
        point = matrix.Point.zero().tuple()
        self.assertIsInstance(self.filler.get_item(point), color.Color)

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestPaletteFiller(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        self.filler = filler.PaletteFiller(cols=0, rows=0, palette=color.Palette.sample())
        self.palette = color.Palette.sample()

    def test_get_item(self) -> None:
        random_color = self.filler.get_item()
        self.assertIsInstance(random_color, color.Color)
        self.assertTrue(random_color in self.palette.colors)

    def test_get_item_at_point(self) -> None:
        random_color = self.filler.get_item(matrix.Point.zero().tuple())
        self.assertIsInstance(random_color, color.Color)
        self.assertTrue(random_color in self.palette.colors)

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestImageFiller(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        self.expected_color = color.RGBAColor(r=209, g=198, b=166)
        self.filler = filler.ImageFiller(cols=24, rows=12, image_name="wave.jpg")

    def test_get_item(self) -> None:
        random_color = self.filler.get_item()
        self.assertIsInstance(random_color, color.RGBAColor)

    def test_get_item_at_point(self) -> None:
        random_color = self.filler.get_item(matrix.Point.zero().tuple())
        self.assertIsInstance(random_color, color.RGBAColor)
        self.assertEqual(random_color, self.expected_color)

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestRecoveryFiller(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        self.recovery1 = secret.Recovery(name="Recovery1", origin=matrix.Point.zero(),
                                         v2_components=matrix.V2Component.components_from_string("a:1 b:2 c:3"),
                                         cols=64, rows=64, length=4)

        self.recovery2 = secret.Recovery(name="Recovery2", origin=matrix.Point(10, 10),
                                         v2_components=matrix.V2Component.components_from_string("a:5 b:10 c:15"),
                                         cols=64, rows=64, length=4)

        self.secret1 = secret.Secret(name="Secret1", data=["zoo", "zoo", "zoo", "zoo"], origin=self.recovery1.origin,
                                     v2_components=self.recovery1.components)
        self.secret2 = secret.Secret(name="Secret2", data=["act", "action", "actor", "actress"],
                                     origin=self.recovery2.origin, v2_components=self.recovery2.components)
        self.vault = secret.Vault()
        self.vault.add_secret(secret=self.secret1)
        self.vault.add_secret(secret=self.secret2)
        self.english_data_domain = data_domain.DictionaryDomain(file_name="bip-0039_english.txt")
        self.domain = data_domain.Domain()
        self.domain.add(data_domain=self.english_data_domain)
        self.domain.generate_domain(total_items=64 * 64)
        self.mosaic = mosaic.Mosaic(domain=self.domain,
                                    color_filler=filler.PaletteFiller(cols=64, rows=64, palette=color.Palette.sample()))
        self.mosaic.hide_secrets(self.vault)
        self.bitmosaic = image.Bitmosaic(self.mosaic)
        self.bitmosaic.save(recovery_txt=False, recovery_cards=False)

    def test_recover_secret1(self) -> None:
        data = util.read_txt_file(util.get_output_directory("bitmosaic.txt"))
        recovered_mosaic = mosaic.Mosaic.from_recovery(bitmosaic_data=data, recovery=self.recovery1)
        recovery = recovered_mosaic.recover_secret(recovery=self.recovery1)
        self.assertEqual(recovery.data, self.secret1.data)

    def test_recover_secret2(self) -> None:
        data = util.read_txt_file(util.get_output_directory("bitmosaic.txt"))
        recovered_mosaic = mosaic.Mosaic.from_recovery(bitmosaic_data=data, recovery=self.recovery2)
        recovery = recovered_mosaic.recover_secret(recovery=self.recovery2)
        self.assertEqual(recovery.data, self.secret2.data)

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()
