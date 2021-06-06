# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# data_domain.py is part of Bitmosaic.
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
import re
import time
import unicodedata
import bitmosaic.util as util
from xeger import Xeger
from bitmosaic.exception import ErrorCodes
from bitmosaic.exception import FileException
from bitmosaic.exception import ValueException


class DataDomain(abc.ABC):

    """
    Defines the Datadomain protocol.

    Properties
    ----------
    data : [str]
        read only property that returns the data as list of strings


    Methods
    -------
    random(length: int)
        returns a random value from data
        if 0

    """

    @property
    @abc.abstractmethod
    def hash(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def data(self) -> [str]:
        pass

    @abc.abstractmethod
    def contains(self, item: str) -> bool:
        pass

    @abc.abstractmethod
    def random(self, count: int, max_length: int) -> [str]:
        pass


class DictionaryDomain(DataDomain):

    """
    This class get the contents of file and make it available as a data domain.

    The file is a dictionary with a word in each line.
    Conforms the DataDomain protocol.

    Properties:
    -----------
    name : str
        the name for the data domain

    hash : str
        read only property that return the object's hash

    data : [str]
        read only property that returns the data as list of strings

    file_name : str
        the file name

    file_path: str
        the complete file path

    Methods
    -------

    contains(item: str)
        Returns if the item is contained in the data list.

    random(count: int, max_length: int)
        Returns a list with random items.

        The count parameter indicates the length of the list.
        The maximum length of each item can be limited by the max_length parameter.

    """

    @property
    def name(self) -> str:
        return self._name

    @property
    def hash(self) -> int:
        return self.__hash__()

    @property
    def data(self) -> [str]:
        return self._data

    @property
    def file_name(self) -> str:
        return self._file_name

    @property
    def file_path(self) -> str:
        return str(self._file_path)

    def __init__(self, file_name: str):
        """
        :param str file_name: the name of the file to load
        """
        self._name = file_name
        self._file_name = file_name
        self._file_path = util.get_domains_directory(self._file_name)
        if not os.path.exists(self._file_path):
            raise FileException(self._file_name, "The file {0} does not exist".format(self._file_name))
        self._data = []
        try:
            self.__load_data()
        except FileException as e:
            raise e

    def __eq__(self, other: DataDomain):
        return type(other) == DictionaryDomain and set(self._data) == set(other.data)

    def __hash__(self):
        return hash(set(self._data))

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return "FileDomain({0})".format(self._file_name)

    def __str__(self):
        return "{0}".format(self._file_path)

    def __load_data(self):
        """
        Loads the data from the file into the data list.

        :raises FileException: if there is some error while reading the file content.
        :return: None
        """
        try:
            with open(self._file_path, "r", encoding="utf-8") as data_file:
                self._data = data_file.read().split("\n")
        except Exception:
            raise FileException(ErrorCodes.file_error, "There was a problem reading the data domain file(s)")

    def contains(self, item: str) -> bool:
        """
        Checks if the item is in list.

        :param str item: the string to find.
        :return: bool
        """
        for data in self._data:
            if unicodedata.normalize("NFD", data) == unicodedata.normalize("NFD", item):
                return True
        return False

    def random(self, count=1, max_length=0) -> [str]:
        """
        Returns a random item from the data list.

        :param int count: the number of items to generate.
        :param int max_length: the desired length for the words to return from dictionary, or 0 to use all.
        :return: [str]
        """
        valid = self._data
        if max_length > 0:
            valid = [item for item in self._data if 0 < len(item) <= max_length]
            if valid is []:
                raise ValueException(max_length, "There are no words in dictionary which length is less or equals "
                                                 "than {0}".format(max_length))
        return random.choices(valid, k=count)


class RegexDomain(DataDomain):

    """
    This class uses a regex as data domain.
    Conforms the DataDomain protocol.

    Properties:
    -----------
    hash : str
        read only property that return the object's hash.

    data : [str]
        read only property that returns the data as list of strings.

    regex : str
        the regular expression as string.

    Methods
    -------

    contains(item: str)
        Returns if the item match the regex.

    random(count: int, max_length: int)
        Returns a list with random items.
        The count parameter indicates the length of the list.
        The maximum length of each item can be limited by the max_length parameter.

    """

    @property
    def name(self) -> str:
        return self._name

    @property
    def hash(self) -> int:
        return self.__hash__()

    @property
    def data(self) -> [str]:
        return self.random()

    @property
    def regex(self) -> str:
        return self._regex

    def __init__(self, regex: str):
        """
        :param str regex: the regular expression
        :raises ValueException: if the regex is not valid
        """
        self._name = regex
        try:
            re.compile(regex)
            self._regex = regex
        except re.error:
            raise ValueException(regex, re.error.msg)

    def __eq__(self, other: DataDomain):
        return type(other) == RegexDomain and self._regex == other.regex

    def __hash__(self):
        return hash(self._regex)

    def __repr__(self):
        return "RegexDomain({0})".format(self._regex)

    def __str__(self):
        return "{0}".format(self._regex)

    def contains(self, item: str) -> bool:
        """
        Checks if the item match the regex.

        :param str item: the string to check.
        :return: bool
        """
        return not re.match(self._regex, item) is None

    def __random(self, max_length=5) -> str:
        """
        Returns a random item from the data list.

        :param int max_length: the maximum length for the strings returned.
        :return: str
        """
        if max_length <= 0:
            raise ValueException(max_length, "max_length must be greater than 0")
        x = Xeger(limit=max_length)
        return x.xeger(self._regex)

    def random(self, count=1, max_length=5) -> [str]:
        """
        Returns a random list of items from the data list.

        :param int count: the number of items.
        :param int max_length: the maximum length for the strings returned.
        :return: [str]
        """
        items = []
        while len(items) < count:
            items.append(self.__random(max_length))
        return items


class Domain(DataDomain):
    """
    This class builds a data domain from multiple DataDomain objects.

    Properties
    ----------
    available_items : int
        returns the sum for the items in all domains

    count : int
        returns the number of domains

    hash : int
        returns the hash for the domain

    data : [str]
        returns the items for the domain
    """

    @property
    def available_items(self) -> int:
        return sum(map(len, self._domains))

    @property
    def count(self) -> int:
        return len(self._domains)

    @property
    def hash(self) -> int:
        return hash(self._data)

    @property
    def data(self) -> [str]:
        return self._data

    def __init__(self):
        self._domains = []
        self._data = []

    def __len__(self) -> int:
        return len(self._data)

    def add(self, data_domain: DataDomain) -> bool:
        """
        Adds the data_domain to the domain list, if not was already added.

        :param DataDomain data_domain: the data_domain to add.
        :return: None
        """
        if data_domain not in self._domains:
            self._domains.append(data_domain)
            return True
        return False

    def remove(self, data_domain: DataDomain) -> bool:
        """
        Removes the data_domain from the domains list.

        :param DataDomain data_domain: the data_domain to remove.
        :return: None
        """
        if data_domain in self._domains:
            self._domains.remove(data_domain)
            return True
        return False

    def remove_by_name(self, name: str) -> bool:
        """
        Removes the data_domain from the domains list, by name.

        :param str name: the data domain's name
        :return: bool
        """
        for data_domain in self._domains:
            if data_domain.name == name:
                self.remove(data_domain)
                return True
        return False

    def generate_domain(self, total_items: int):
        """
        Populates the _data attribute picking random items from each domain.

        :param int total_items: the number of items to pick.
        :return: None
        """
        start_time = time.time()
        self._data = []
        random.shuffle(self._domains)
        for index, data_domain in enumerate(self._domains):
            remaining_items = total_items - len(self._data)
            if index < len(self._domains)-1:
                min_items = round(remaining_items / self.count)
                max_items = random.randint(min_items, remaining_items)
                number_of_items = random.randint(min_items, max_items)
            else:
                number_of_items = remaining_items
            random_items = data_domain.random(count=number_of_items)
            self._data.extend(random_items)
        random.shuffle(self._data)
        self._time = time.time() - start_time

    def contains(self, item: str) -> bool:
        """
        Checks if the item is in _data list.

        :param str item: the string to check.
        :return: bool
        """
        if self._data.__contains__(item):
            return True
        else:
            for domain in self._domains:
                if type(domain) is RegexDomain and domain.contains(item):
                    return True
                elif type(domain) is not RegexDomain:
                    if domain.contains(item):
                        return True
        return False

    def random(self, count: int, max_length=0) -> [str]:
        """
        Returns a random list of items from the _data list.

        :param int count: the number of items.
        :param int max_length: the desired length for the words to return from dictionary, or 0 to use complete.
        :return: [str]
        """
        return random.choices(self._data, k=count)
