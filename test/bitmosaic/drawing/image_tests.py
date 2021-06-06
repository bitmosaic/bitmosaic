# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# image_tests.py is part of Bitmosaic.
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
import os
import bitmosaic.drawing.image as bitmosaic_image
import bitmosaic.core.data_domain as data_domain
import bitmosaic.core.filler as filler
import bitmosaic.core.matrix as matrix
import bitmosaic.core.mosaic as mosaic
import bitmosaic.core.secret as secret
import bitmosaic.util as util


class TestHtmlColor(unittest.TestCase):
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

        self.image_filler = filler.ImageFiller(cols=self.cols, rows=self.rows, image_name="wave.jpg")
        self.mosaic = mosaic.Mosaic(domain=self.domain, color_filler=self.image_filler)
        self.vault = secret.Vault()
        self.vault.add_secret(secret=self.secret1)
        self.vault.add_secret(secret=self.secret2)
        self.mosaic.hide_secrets(vault=self.vault)
        self.bitmosaic = bitmosaic_image.Bitmosaic(mosaic=self.mosaic)
        self.bitmosaic_no_frame = bitmosaic_image.Bitmosaic(mosaic=self.mosaic)
        self.bitmosaic_no_frame.framed = False

    def test_bitmosaic_size_with_frame(self) -> None:
        self.assertEqual(self.bitmosaic.cols, self.mosaic.cols + 2)
        self.assertEqual(self.bitmosaic.rows, self.mosaic.rows + 2)
        self.bitmosaic.framed = False

    def test_bitmosaic_size_without_frame(self) -> None:
        self.assertEqual(self.bitmosaic_no_frame.cols, self.mosaic.cols)
        self.assertEqual(self.bitmosaic_no_frame.rows, self.mosaic.rows)

    def test_bitmosaic_width_with_frame(self) -> None:
        pass

    def test_bitmosaic_width_without_frame(self) -> None:
        pass

    def test_bitmosaic_height_with_frame(self) -> None:
        pass

    def test_bitmosaic_height_without_frame(self) -> None:
        pass

    def test_bitmosaic_without_frame_draw(self) -> None:
        self.bitmosaic.framed = False
        self.delete_output_files()
        self.bitmosaic.save(bitmosaic_txt=False, recovery_txt=False, recovery_cards=False)
        file = util.get_output_directory("bitmosaic.png")
        self.assertTrue(os.path.exists(file))

    def test_do_not_save_bitmosaic_txt_files(self) -> None:
        file = util.get_output_directory("bitmosaic.txt")
        self.assertFalse(os.path.exists(file))

    def test_do_not_save_bitmosaic_recovery_txt_files(self) -> None:
        for recovery in self.mosaic.recoveries:
            file = util.get_output_directory("recovery_{0}.txt".format(recovery.name).replace(" ", "_"))
            self.assertFalse(os.path.exists(file))

    def test_do_not_save_bitmosaic_recovery_cards(self) -> None:
        for recovery in self.mosaic.recoveries:
            file = util.get_output_directory("recovery_{0}.png".format(recovery.name).replace(" ", "_"))
            self.assertFalse(os.path.exists(file))

    def test_bitmosaic_with_frame_draw(self) -> None:
        self.delete_output_files()
        self.bitmosaic.save()
        file = util.get_output_directory("bitmosaic.png")
        self.assertTrue(os.path.exists(file))

    def test_save_bitmosaic_recovery_txt_files(self) -> None:
        self.delete_output_files()
        self.bitmosaic.save()
        for recovery in self.mosaic.recoveries:
            file = util.get_output_directory("recovery_{0}.txt".format(recovery.name).replace(" ", "_"))
            self.assertTrue(os.path.exists(file))

    def delete_output_files(self):
        directory = util.get_output_directory()
        for file in os.listdir(directory):
            os.remove(os.path.join(directory, file))

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()
