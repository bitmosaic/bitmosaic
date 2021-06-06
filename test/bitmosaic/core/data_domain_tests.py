# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# data_domain_tests.py is part of Bitmosaic.
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
from bitmosaic.exception import FileException
from bitmosaic.exception import ValueException
import bitmosaic.core.data_domain as data_domain
import bitmosaic.util as util


class TestDictionaryDomain(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        self.file_name = "bip-0039_english.txt"
        self.dictionary_domain = data_domain.DictionaryDomain(self.file_name)

    def test_invalid_file(self):
        file_name = "no_exist.txt"
        with self.assertRaises(FileException):
            dictionary_domain = data_domain.DictionaryDomain(file_name)

    def test_len(self) -> None:
        self.assertEqual(len(self.dictionary_domain), 2048)

    def test_contains(self) -> None:
        self.assertTrue(self.dictionary_domain.contains("zoo"))
        self.assertFalse(self.dictionary_domain.contains("zoology"))

    def test_random(self) -> None:
        random_items = self.dictionary_domain.random()
        self.assertIsNotNone(random_items)
        self.assertIs(type(random_items), list)

    def test_random_with_count(self) -> None:
        ten_random_items = self.dictionary_domain.random(count=10)
        self.assertEqual(len(ten_random_items), 10)

    def test_random_with_invalid_count(self) -> None:
        random_items = self.dictionary_domain.random(count=-1)
        self.assertEqual(len(random_items), 0)

    def test_random_with_max_length(self) -> None:
        self.assertLessEqual(len(self.dictionary_domain.random(max_length=5)), 5)

    def test_random_with_invalid_max_length(self) -> None:
        self.assertIsNotNone(self.dictionary_domain.random(max_length=0))

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestRegexDomain(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        self.regex = "^[a-zA-Z]+$"
        self.regex_domain = data_domain.RegexDomain(self.regex)

    def test_contains(self) -> None:
        self.assertTrue(self.regex_domain.contains("Word"))
        self.assertFalse(self.regex_domain.contains("W1rd"))

    def test_random(self) -> None:
        random_items = self.regex_domain.random()
        self.assertIsNotNone(random_items)
        self.assertEqual(type(random_items), list)

    def test_random_with_count(self) -> None:
        ten_random_items = self.regex_domain.random(count=10)
        self.assertEqual(len(ten_random_items), 10)

    def test_random_with_invalid_count(self) -> None:
        random_items = self.regex_domain.random(count=-1)
        self.assertEqual(len(random_items), 0)

    def test_random_with_max_length(self) -> None:
        item = self.regex_domain.random(max_length=5)
        self.assertLessEqual(len(item), 5)

    def test_random_with_invalid_max_length(self) -> None:
        with self.assertRaises(ValueException):
            self.regex_domain.random(max_length=0)

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestDomain(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        self.file_name = "bip-0039_english.txt"
        self.dictionary_domain = data_domain.DictionaryDomain(self.file_name)
        self.regex = "^[a-zA-Z]+$"
        self.regex_domain = data_domain.RegexDomain(self.regex)
        self.domain = data_domain.Domain()
        self.domain.add(self.dictionary_domain)
        self.domain.add(self.regex_domain)

    def test_add_dictionary_domain(self) -> None:
        dictionary_domain = data_domain.DictionaryDomain("bip-0039_japanese.txt")
        count = self.domain.count
        self.domain.add(dictionary_domain)
        self.assertEqual(self.domain.count, count+1)

    def test_add_regex_domain(self) -> None:
        regex_domain = data_domain.RegexDomain(regex="^\d+$")
        count = self.domain.count
        self.domain.add(regex_domain)
        self.assertEqual(self.domain.count, count+1)

    def test_add_repeated_dictionary_domain(self) -> None:
        count = self.domain.count
        self.domain.add(self.dictionary_domain)
        self.assertEqual(self.domain.count, count)

    def test_add_repeated_regex_domain(self) -> None:
        count = self.domain.count
        self.domain.add(self.regex_domain)
        self.assertEqual(self.domain.count, count)

    def test_generate_domain(self) -> None:
        self.domain.generate_domain(total_items=1024)
        self.assertEqual(len(self.domain), 1024)

    def test_contains_item(self) -> None:
        self.domain.generate_domain(total_items=1024)
        item = self.domain.data[0]
        self.assertTrue(self.domain.contains(item))

    def test_contains_invalid_item(self) -> None:
        item = "1"
        self.assertFalse(self.domain.contains(item))

    def test_random_item(self) -> None:
        self.domain.generate_domain(1024)
        self.assertIsNotNone(self.domain.random(count=1))
        self.assertEqual(len(self.domain.random(count=1)), 1)

    def test_multiple_items(self) -> None:
        self.domain.generate_domain(1024)
        self.assertEqual(len(self.domain.random(count=10)), 10)

    def test_remove_data_domain(self) -> None:
        self.assertEqual(self.domain.remove(self.regex_domain), 1)

    def test_remove_data_domain_by_name(self) -> None:
        self.assertEqual(self.domain.remove_by_name(self.file_name), 1)

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()
