# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# bitmosaic.py is part of Bitmosaic.
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

import eel
import os
import sys
import time
import bitmosaic.util as util
from bitmosaic.core.data_domain import DictionaryDomain
from bitmosaic.core.data_domain import Domain
from bitmosaic.core.data_domain import RegexDomain
from bitmosaic.core.filler import ImageFiller
from bitmosaic.core.filler import PaletteFiller
from bitmosaic.core.matrix import Point
from bitmosaic.core.matrix import V2Component
from bitmosaic.core.mosaic import Mosaic
from bitmosaic.core.secret import Recovery
from bitmosaic.core.secret import Secret
from bitmosaic.core.secret import Vault
from bitmosaic.drawing.color import HtmlColor
from bitmosaic.drawing.color import Palette
from bitmosaic.drawing.image import Bitmosaic
from bitmosaic.drawing.image import Frame
from bitmosaic.drawing.image import Margin
from bitmosaic.exception import ErrorCodes
from bitmosaic.exception import FileException
from bitmosaic.exception import InvalidColorException
from bitmosaic.exception import InvalidComponentException
from bitmosaic.exception import MosaicItemCollisionException
from bitmosaic.exception import ValueException

english_data_domain = DictionaryDomain("bip-0039_english.txt")
domain = Domain()
domain.add(english_data_domain)
vault = Vault()

secret_components = ""

save_bitmosaic_txt = True
save_recovery_txt = True
save_recovery_card = True

cols = 64
rows = 64
palette = Palette.sample()
image = None

eel.init("bitmosaic/gui")


def __color_from_str(value):
    if value == "random":
        color = HtmlColor.random()
    else:
        try:
            color = HtmlColor(value)
        except InvalidColorException as e:
            return e.error_code, e.message, None
    return ErrorCodes.no_error, "", color


@eel.expose
def add_dictionary_data_domain(file: str) -> tuple:
    global domain
    try:
        dictionary_domain = DictionaryDomain(file)
        if domain.add(dictionary_domain):
            return ErrorCodes.no_error.value, "", file
        else:
            return ErrorCodes.value_error, "A domain with this name already exists"
    except FileException as e:
        return ErrorCodes.file_error, "The file does not exist", file


@eel.expose
def add_regex_data_domain(regex: str) -> tuple:
    global domain
    if len(regex) == 0 or regex.replace(" ", "") == "":
        return ErrorCodes.value_error, "The regex is not valid", regex
    try:
        regex_domain = RegexDomain(regex)
        if domain.add(regex_domain):
            return ErrorCodes.no_error.value, "", regex
        else:
            return ErrorCodes.value_error, "A domain with this name already exists"
    except ValueException as e:
        return ErrorCodes.value_error, "The regex is not valid", regex


@eel.expose
def remove_data_domain(name: str) -> tuple:
    global domain
    if domain.remove_by_name(name[1:-1]):
        return ErrorCodes.no_error, "", name
    return ErrorCodes.value_error, "Data domain not found", name


@eel.expose
def add_secret(name: str, data: str, col: int, row: int, components: str) -> tuple:
    global vault

    result = (ErrorCodes.no_error.value, "", name)

    if name is None or len(name) == 0:
        result = (ErrorCodes.incomplete_secret.value, "You have to name your secret", None)
    if data is None or len(data) == 0:
        result = (ErrorCodes.incomplete_secret.value, "You have to add the data you want to hide", None)

    data = data.split(" ")
    origin = Point.zero()

    try:
        origin = Point(int(col), int(row))
    except ValueError:
        result = (ErrorCodes.value_error.value, "Invalid value for the origin coordinates", None)

    if components is None or len(components) == 0:
        return ErrorCodes.invalid_component.value, "The components can not be empty", None
    else:
        try:
            components = V2Component.components_from_string(components)
        except InvalidComponentException as e:
            return e.error_code.value, e.message, None

    secret = Secret(name, data, origin, components)
    if not vault.add_secret(secret):
        result = ErrorCodes.value_error, "A secret with this name already exist", None
    return result


@eel.expose
def remove_secret(name: str) -> tuple:
    global vault
    vault.remove_secret_by_name(name[1:-1])
    return ErrorCodes.no_error.value, "", name


@eel.expose
def set_secret_components(components: str):
    global secret_components
    if secret_components is None or len(secret_components) == 0:
        return ErrorCodes.invalid_component, "The components cant be empty", None
    try:
        secret_components = V2Component.components_from_string(components)
        return ErrorCodes.no_error, "", None
    except InvalidComponentException as e:
        return e.error_code.value, e.message, None


@eel.expose
def set_save_bitmosaic_txt_file(save):
    global save_bitmosaic_txt
    try:
        save_bitmosaic_txt = bool(save)
        return ErrorCodes.no_error.value, "", None
    except ValueError:
        return ErrorCodes.value_error.value, "", None


@eel.expose
def set_save_recovery_txt_file(save):
    global save_recovery_txt
    try:
        save_recovery_txt = bool(save)
        return ErrorCodes.no_error.value, "", None
    except ValueError:
        return ErrorCodes.value_error.value, "", None


@eel.expose
def set_save_recovery_card(save):
    global save_recovery_card
    try:
        save_recovery_card = bool(save)
        return ErrorCodes.no_error.value, "", None
    except ValueError:
        return ErrorCodes.value_error.value, "", None


# Margin Setup

@eel.expose
def set_margin(top, right, bottom, left):
    try:
        Margin.top = int(top)
        Margin.right = int(right)
        Margin.bottom = int(bottom)
        Margin.left = int(left)
        return ErrorCodes.no_error.value, "", None
    except ValueError:
        return ErrorCodes.invalid_value.value, "Invalid values for margin", None


@eel.expose
def set_frame(enabled):
    try:
        Bitmosaic.framed = bool(enabled)
        return ErrorCodes.no_error.value, "", enabled
    except ValueError:
        return ErrorCodes.invalid_value.value, "Bool value expected for show frame", None


@eel.expose
def set_frame_background_color(color):
    color = __color_from_str(color)
    if color[0] == ErrorCodes.no_error:
        Frame.color = color[2]
        return ErrorCodes.no_error.value, "", str(color[2])
    return color


@eel.expose
def set_frame_text_color(color):
    color = __color_from_str(color)
    if color[0] == ErrorCodes.no_error:
        Frame.text_color = color[2]
        return ErrorCodes.no_error.value, "", str(color[2])
    return color


@eel.expose
def set_frame_text_visibility(visibility):
    try:
        Frame.show_text = bool(visibility)
        return ErrorCodes.no_error.value, "", Frame.show_text
    except ValueError:
        return ErrorCodes.invalid_value.value, "Bool value expected for show text in frame", None


# Mosaic

@eel.expose
def set_mosaic_size(col_number, row_number):
    global cols, rows
    try:
        cols = int(col_number)
        rows = int(row_number)
        return ErrorCodes.no_error.value, "", None
    except ValueError:
        return ErrorCodes.invalid_value.value, "Invalid values for cols or rows", None


@eel.expose
def set_mosaic_dpi(dpi):
    try:
        Bitmosaic.dpi = int(dpi)
        return ErrorCodes.no_error.value, "", None
    except ValueError:
        return ErrorCodes.invalid_value.value, "Invalid value for dpi", None


@eel.expose
def set_mosaic_tessera_side(side):
    try:
        Bitmosaic.tessera_side = int(side)
        return ErrorCodes.no_error.value, "", None
    except ValueError:
        return ErrorCodes.invalid_value.value, "Invalid value for tessera side", None


@eel.expose
def set_mosaic_background_color(color):
    color = __color_from_str(color)
    if color[0] == ErrorCodes.no_error:
        Bitmosaic.color = color[2]
        return ErrorCodes.no_error.value, "", str(color[2])
    return color


@eel.expose
def set_mosaic_border_color(color):
    color = __color_from_str(color)
    if color[0] == ErrorCodes.no_error:
        Frame.border_color = color[2]
        Bitmosaic.tessera_border_color = color[2]
        return ErrorCodes.no_error.value, "", str(color[2])
    return color


@eel.expose
def set_mosaic_border_width(width):
    try:
        Frame.border_width = int(width)
        Bitmosaic.tessera_border_width = int(width)
        return ErrorCodes.no_error.value, "", None
    except ValueError:
        return ErrorCodes.invalid_value.value, "Invalid value for mosaic border width", None


@eel.expose
def set_mosaic_show_coordinates(show):
    try:
        Bitmosaic.coordinates = bool(show)
        return ErrorCodes.no_error.value, "", None
    except ValueError:
        return ErrorCodes.invalid_value.value, "Bool value expected for show coordinates", None


@eel.expose
def set_mosaic_palette_colors(base_color, number_of_colors):
    global image, palette
    image = None
    color = __color_from_str(base_color)
    if color[0] == ErrorCodes.no_error:
        colors = Palette.similar_colors(color[2], int(number_of_colors))
        palette = Palette()
        palette.add_colors(colors)
        return ErrorCodes.no_error.value, "", str(color[2])
    return color


@eel.expose
def set_mosaic_image(image_name):
    global image, palette
    palette = None
    image = image_name


def __exist_file(file_path: str):
    return os.path.exists(file_path)


@eel.expose
def create_bitmosaic():
    global domain, vault, secret_components, save_bitmosaic_txt, save_recovery_txt, save_recovery_card, cols, rows, \
        palette, image

    if domain.count == 0:
        return ErrorCodes.no_data_domain, "A data domain is needed", None
    if len(vault) == 0:
        return ErrorCodes.no_secret, "A secret is needed", None

    try:
        if image is not None:
            color_filler = ImageFiller(cols, rows, image)
        elif palette is not None:
            color_filler = PaletteFiller(cols, rows, palette)
        else:
            color_filler = PaletteFiller(cols, rows, Palette.sample())
        build_start_time = time.time()
        domain.generate_domain(cols * rows)
        domain_time = "{0:.2f}s".format(time.time() - build_start_time)
        start_time = time.time()
        mosaic = Mosaic(domain, color_filler)
        mosaic_time = "{0:.2f}s".format(time.time() - start_time)
        start_time = time.time()
        mosaic.hide_secrets(vault)
        hiding_time = "{0:.2f}s".format(time.time() - start_time)
        start_time = time.time()
        bitmosaic = Bitmosaic(mosaic)
        bitmosaic.save(bitmosaic_txt=save_bitmosaic_txt, recovery_txt=save_recovery_txt,
                       recovery_cards=save_recovery_card)
        build_end_time = time.time()
        bitmosaic_time = "{0:.2f}s".format(build_end_time - start_time)
        total_time = "{0:.2f}s".format(build_end_time - build_start_time)
        result = (ErrorCodes.no_error.value, 'Bitmosaic file created.', ("Saved in: bitmosaic -> data -> output\n\n"
                                                                        "Size in inches: {0}\n" 
                                                                        "Size in cms: {1}\n\n"
                                                                        "Times\n"
                                                                        "------\n"
                                                                        "Domain: {2}\n"
                                                                        "Mosaic: {3}\n"
                                                                        "Hiding: {4}\n"
                                                                        "Bitmosaic: {5}\n\n"
                                                                        "Total: {6}"
                                                                         .format(bitmosaic.size_in_inches,
                                                                                 bitmosaic.size_in_cms,
                                                                                 domain_time,
                                                                                 mosaic_time,
                                                                                 hiding_time,
                                                                                 bitmosaic_time,
                                                                                 total_time)))
    except ValueException as e:
        result = (e.error_code.value, e.message, None)
    except MosaicItemCollisionException as e:
        result = (e.error_code.value, e.message, None)
    except Exception:
        result = (ErrorCodes.value_error.value, "There was an error creating the bitmosaic", None)
    return result


@eel.expose
def recover_secret_from_file(bitmosaic_txt: str, recovery_txt: str):
    bitmosaic_file = util.get_output_directory(bitmosaic_txt)
    recovery_file = util.get_output_directory(recovery_txt)
    if not __exist_file(str(bitmosaic_file)) or not __exist_file(str(recovery_file)):
        return ErrorCodes.recovery_info_incomplete, \
               "You have to select the bitmosaic txt file and recovery txt file.\r" \
               "The file location must be: app directory -> data -> output", None
    try:
        data = util.read_txt_file(bitmosaic_file)
        recovery = Recovery.create_from_file(recovery_txt)
        if not recovery.is_complete():
            return ErrorCodes.recovery_info_incomplete.value, "The recovery information is not complete", None

        mosaic = Mosaic.from_recovery(data, recovery)
        result = (ErrorCodes.no_error, " ".join(mosaic.recover_secret(recovery).data), None)
    except ValueException as e:
        result = (e.error_code, e.message)
    except IOError:
        result = (ErrorCodes.file_read, "Error reading bitmosaic txt file", None)
    return result


@eel.expose
def recover_secret_from_form(bitmosaic_txt: str, cols: str, rows: str, col: str, row: str, components: str, length: str):
    bitmosaic_file = util.get_output_directory(bitmosaic_txt)
    if not __exist_file(bitmosaic_file):
        return ErrorCodes.recovery_info_incomplete, "You have to select the bitmosaic txt file", None
    try:
        data = util.read_txt_file(bitmosaic_file)
    except IOError:
        return ErrorCodes.file_read, "Error reading bitmosaic txt file", None
    if components != '':
        try:
            components = V2Component.components_from_string(components)
        except InvalidComponentException as e:
            return e.error_code.value, e.message, None
    try:
        cols = int(cols)
        rows = int(rows)
    except ValueError:
        return ErrorCodes.invalid_value.value, "Invalid value for recovery size", None
    try:
        col = int(col)
        row = int(row)
        origin = Point(col, row)
    except:
        return ErrorCodes.invalid_value.value, "Invalid value for recovery info origin", None
    try:
        length = int(length)
    except ValueError:
        return ErrorCodes.invalid_value.value, "Invalid value for recovery length", None

    try:
        recovery = Recovery(name="Recovery", origin=origin, v2_components=components,
                            cols=cols, rows=rows, length=length)
        mosaic = Mosaic.from_recovery(data, recovery)
        result = (ErrorCodes.no_error, mosaic.recover_secret(recovery).data, None)
    except ValueException as e:
        result = (e.error_code, e.message)
    return result


if __name__ == "__main__":
    try:
        if len(sys.argv) == 2:
            browser = sys.argv[1].lower()
            if not browser in ["chrome", "edge"]:
                browser = "chrome"
        else:
            browser = "chrome"
        eel.start('index.html', mode=browser)
    except KeyboardInterrupt:
        exit(0)
