# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# secret_tests.py is part of Bitmosaic.
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
import bitmosaic.core.secret as secret
import bitmosaic.util as util
from bitmosaic.core.matrix import Point
from bitmosaic.core.matrix import V2Component


class TestSecret(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        first_component = V2Component("a", 1)
        second_component = V2Component("b", 2)
        third_component = V2Component("c", 3)
        self.secret = secret.Secret(name="A secret", data=["this", "is", "my", "secret"], origin=Point.zero(),
                                    v2_components={first_component, second_component, third_component})

    def test_secret_as_string(self) -> None:
        self.assertTrue(str(self.secret), "(0, 0)|a:1 b:2 c:3|4")

    def test_is_complete(self) -> None:
        self.assertTrue(self.secret.is_complete())

    def test_invalid_data_none(self) -> None:
        invalid_secret = secret.Secret(name="Invalid data secret", data=None, origin=Point.zero(),
                                       v2_components={V2Component.random_fake_component(),
                                                      V2Component.random_fake_component()})
        self.assertFalse(invalid_secret.is_complete())

    def test_invalid_data_type(self) -> None:
        invalid_secret = secret.Secret(name="Invalid data secret", data="", origin=Point.zero(),
                                       v2_components={V2Component.random_fake_component(),
                                                      V2Component.random_fake_component()})
        self.assertFalse(invalid_secret.is_complete())

    def test_invalid_data_length(self) -> None:
        invalid_secret = secret.Secret(name="Invalid data secret", data=[], origin=Point.zero(),
                                       v2_components={V2Component.random_fake_component(),
                                                      V2Component.random_fake_component()})
        self.assertFalse(invalid_secret.is_complete())

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestRecovery(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        first_component = V2Component("a", 1)
        second_component = V2Component("b", 2)
        third_component = V2Component("c", 3)
        self.recovery = secret.Recovery(name="Recovery info", origin=Point.zero(),
                                        v2_components={first_component, second_component, third_component},
                                        cols=5, rows=3, length=3)

    def test_recovery_as_string(self) -> None:
        self.assertTrue(str(self.recovery), "5x3|(0, 0)|a:1 b:2 c:3|3")

    def test_card(self) -> None:
        self.assertTrue(str(self.recovery), "5x3\n\n(0, 0)\na:1 b:2 c:3\n\n\n3")

    def test_is_complete(self) -> None:
        self.assertTrue(self.recovery.is_complete())

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestVault(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        first_component = V2Component("a", 1)
        second_component = V2Component("b", 2)
        third_component = V2Component("c", 3)
        self.first_secret = secret.Secret(name="First secret", data=["this", "is", "the", "first", "secret"],
                                          origin=Point.zero(),
                                          v2_components={first_component, second_component, third_component})
        self.second_secret = secret.Secret(name="Second secret", data=["this", "is", "the", "second", "secret"],
                                           origin=Point(4, 4),
                                           v2_components={first_component, second_component, third_component})
        self.invalid_secret = secret.Secret(name="Invalid data secret", data=None, origin=Point(3, 3),
                                            v2_components={V2Component.random_fake_component(),
                                                           V2Component.random_fake_component()})
        self.other_invalid_secret = secret.Secret(name="Invalid data secret", data="zoo zoo zoo", origin=Point.zero(),
                                            v2_components={V2Component.random_fake_component(),
                                                           V2Component.random_fake_component()})
        self.vault = secret.Vault()

    def test_add_valid_secrets(self) -> None:
        self.vault.add_secret(self.first_secret)
        self.vault.add_secret(self.second_secret)
        self.assertEqual(len(self.vault), 2)

    def test_add_invalid_secrets(self) -> None:
        self.vault.add_secret(self.first_secret)
        self.vault.add_secret(self.invalid_secret)
        self.vault.add_secret(self.other_invalid_secret)
        self.assertEqual(len(self.vault), 1)

    def test_remove_valid_secret(self) -> None:
        self.vault.add_secret(self.first_secret)
        self.vault.remove_secret(self.first_secret)
        self.assertEqual(len(self.vault), 0)

    def test_remove_valid_secret_by_name(self) -> None:
        self.vault.add_secret(self.first_secret)
        self.vault.remove_secret_by_name("First secret")
        self.assertEqual(len(self.vault), 0)

    def test_remove_invalid_secret(self) -> None:
        self.vault.add_secret(self.first_secret)
        self.vault.remove_secret(self.second_secret)
        self.assertEqual(len(self.vault), 1)

    def test_remove_incomplete_secret(self) -> None:
        self.vault.add_secret(self.first_secret)
        first_secret = secret.Secret(name="First secret", data=[], origin=Point.zero(),
                                     v2_components=V2Component.components_from_string("a:1 b:2 c:3"))
        self.vault.remove_secret(first_secret)
        self.assertEqual(len(self.vault), 1)

    def test_get_secret_at_index(self) -> None:
        self.vault.add_secret(self.first_secret)
        self.vault.add_secret(self.second_secret)
        self.assertEqual(self.vault.get_secret(index=1), self.second_secret)

    def test_get_secret_out_of_index(self) -> None:
        self.vault.add_secret(self.first_secret)
        self.vault.add_secret(self.second_secret)
        self.assertIsNone(self.vault.get_secret(index=8))

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()
