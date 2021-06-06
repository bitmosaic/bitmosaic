# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# util.py is part of Bitmosaic.
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

import os
from pathlib import Path
from bitmosaic.exception import ErrorCodes
from bitmosaic.exception import FileException


testing = False


def get_project_root(subdir=None) -> Path:
    # To avoid duplicating the font file (24MB), the font in app directory is used
    if testing and "Code2003-W8nn.ttf" not in subdir:
        return os.path.normpath(Path.joinpath(Path(__file__).parent.parent, "test/" + subdir or ""))
    return os.path.normpath(Path.joinpath(Path(__file__).parent.parent, subdir or ""))


def get_data_directory(file=None) -> Path:
    return get_project_root("data{0}".format("/" + file if file else ""))


def get_domains_directory(file=None) -> Path:
    return get_project_root("data/domains{0}".format("/" + file if file else ""))


def get_fonts_directory(file=None) -> Path:
    return get_project_root("data/fonts{0}".format("/" + file if file else ""))


def get_images_directory(file=None) -> Path:
    return get_project_root("data/images{0}".format("/" + file if file else ""))


def get_output_directory(file=None) -> Path:
    return get_project_root("data/output{0}".format("/" + file if file else ""))


def get_image_input_directory(file=None) -> Path:
    return get_project_root("bitmosaic/gui/bitmosaic_images{0}".format("/" + file if file else ""))


def read_txt_file(file_path: str):
    try:
        with open(file_path, 'r') as file:
            text = file.read()
        return text
    except IOError:
        raise FileException(ErrorCodes.file_error, "There was a problem reading the file {0}".format(file_path))


def write_in_file(file_path: str, text: str):
    with open(file_path, "w") as file:
        file.write(text)


def possible_sizes(length: int) -> int:
    divs = []
    for number in range(1, length + 1):
        if length % number == 0:
            divs.append(number)
    return (len(divs) - 2) // 2
