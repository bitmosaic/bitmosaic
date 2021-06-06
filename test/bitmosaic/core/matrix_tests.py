# Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
#
# matrix_tests.py is part of Bitmosaic.
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
import bitmosaic.core.matrix as matrix
import bitmosaic.core.filler as filler
import bitmosaic.util as util


class TestPoint(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        self.expected_point_x = 1
        self.expected_point_y = 1
        self.zero = matrix.Point.zero()
        self.other = matrix.Point(3, 7)

    def test_point_creation(self) -> None:
        point = matrix.Point(1, 1)
        self.assertEqual(self.expected_point_x, point.x)
        self.assertEqual(self.expected_point_y, point.y)

    def test_point_addition(self):
        point = matrix.Point(7, 3)
        result = point + self.other
        self.assertEqual(result, matrix.Point(10, 10))

    def test_point_substraction(self):
        point = matrix.Point(7, 3)
        result = point - self.other
        self.assertEqual(result, matrix.Point(4, -4))

    def test_point_equal(self):
        point = matrix.Point(3, 7)
        self.assertEqual(point, self.other)

    def test_point_not_equal(self):
        point = matrix.Point(7, 3)
        self.assertNotEqual(point, self.other)

    def test_point_zero(self) -> None:
        point = matrix.Point(0, 0)
        self.assertEqual(point, self.zero)

    def test_random_point(self):
        valid_range = range(100)
        for _ in valid_range:
            point = matrix.Point.random(valid_range)
            self.assertGreaterEqual(point.x, valid_range.start)
            self.assertLess(point.x, valid_range.stop)
            self.assertGreaterEqual(point.y, valid_range.start)
            self.assertLess(point.y, valid_range.stop)

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestV2Component(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        # Test components
        self.component_1 = matrix.V2Component("a", 0)
        self.component_2 = matrix.V2Component("b", 1)
        self.component_3 = matrix.V2Component("c", -1)
        # Components as Text
        self.components_text = "a:0 b:1 c:2"
        # Expected values
        self.expected_component_1_value = "a:0"
        self.expected_component_2_value = "b:1"
        self.expected_component_3_value = "C:-1"
        self.expected_set_value = {self.component_1, self.component_2, self.component_3}

    def test_invalid_label_for_component(self):
        with self.assertRaises(ValueError):
            self.invalid_component = matrix.V2Component("1", -1)

    def test_invalid_value_for_component(self):
        with self.assertRaises((ValueError, TypeError)):
            self.invalid_component = matrix.V2Component("a", "s")

    def test_component_in_set(self) -> None:
        the_set = {self.component_1, self.component_2, self.component_3}
        self.assertEqual(self.component_1.in_set(the_set), self.component_1)

    def test_component_not_in_set(self) -> None:
        the_set = {self.component_1, self.component_2}
        self.assertIsNone(self.component_3.in_set(the_set))

    def test_component_as_str(self):
        self.assertEqual(str(self.component_1), self.expected_component_1_value)
        self.assertEqual(str(self.component_2), self.expected_component_2_value)
        self.assertEqual(str(self.component_3), self.expected_component_3_value)

    def test_fake_components(self):
        self.assertIsNotNone(matrix.V2Component.random_fake_component())

    def test_random_component(self):
        self.assertIsNotNone(matrix.V2Component.random(["a", "b", "c"], range(-10, 10)))

    def test_set_components_from_string(self):
        components_set = matrix.V2Component.components_from_string(self.components_text)
        self.assertEqual(components_set, self.expected_set_value)

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestV2Point(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        # Test point
        self.component_1 = matrix.V2Component("a", 0)
        self.component_2 = matrix.V2Component("b", 10)
        self.component_3 = matrix.V2Component("c", -2)
        self.component_4 = matrix.V2Component("d", -10)
        self.point_1 = matrix.V2Point(self.component_1, self.component_2)
        self.point_2 = matrix.V2Point(self.component_3, self.component_4)
        # Expected values
        self.expected_str_point_1 = "(a:0,b:10)"
        self.expected_str_point_2 = "(C:-2,D:-10)"
        self.expected_str_point_only_labels_1 = "ab"
        self.expected_str_point_only_labels_2 = "CD"
        self.expected_matrix_point = matrix.Point(0, 10)

    def test_v2_points_as_str(self):
        self.assertEqual(str(self.point_1), self.expected_str_point_1)
        self.assertEqual(str(self.point_2), self.expected_str_point_2)

    def test_v2_points_as_str_only_labels(self):
        self.assertEqual(self.point_1.labels(), self.expected_str_point_only_labels_1)
        self.assertEqual(self.point_2.labels(), self.expected_str_point_only_labels_2)

    def test_v2_point_as_matrix_point(self):
        self.assertEqual(self.point_1.to_point(), self.expected_matrix_point)

    def test_v2_point_random_fake(self):
        self.assertIsNotNone(matrix.V2Point.random_fake())

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()


class TestMatrix(unittest.TestCase):
    def setUp(self) -> None:
        util.testing = True
        self.none_filler = filler.NoneFiller()
        self.matrix = matrix.Matrix(cols=10, rows=5, filler=self.none_filler)
        self.fill_matrix()
        # Test points
        self.point_5_2 = matrix.Point(5, 2)
        self.point_lt_0 = matrix.Point(-1, 0)
        self.point_lt_0_a = matrix.Point(-22, 0)
        self.point_gt_9 = matrix.Point(10, 0)
        self.point_gt_9_a = matrix.Point(31, 0)
        # Expected values
        self.expected_5_2_value = "(5, 2)"
        self.expected_lt_0_value = "(9, 0)"
        self.expected_lt_0_a_value = "(8, 0)"
        self.expected_gt_9_value = "(0, 0)"
        self.expected_gt_9_a_value = "(1, 0)"

    def fill_matrix(self) -> None:
        for y in range(self.matrix.rows):
            for x in range(self.matrix.cols):
                point = matrix.Point(x, y)
                self.matrix.set_item(str(point), point)

    def test_get_item(self) -> None:
        self.assertEqual(self.matrix.get_item(self.point_5_2), self.expected_5_2_value)

    def test_set_item(self) -> None:
        new_item = "Zero"
        self.matrix.set_item(new_item, matrix.Point.zero(), replace=True)
        self.assertEqual(self.matrix.get_item(matrix.Point.zero()), new_item)

    def test_set_item_without_replacing(self) -> None:
        new_item = "Zero"
        self.matrix.set_item(new_item, matrix.Point.zero(), replace=False)
        self.assertEqual(self.matrix.get_item(matrix.Point.zero()), str(matrix.Point.zero()))

    def test_get_item_out_of_min_index(self) -> None:
        self.assertEqual(self.matrix.get_item(self.point_lt_0), self.expected_lt_0_value)
        self.assertEqual(self.matrix.get_item(self.point_lt_0_a), self.expected_lt_0_a_value)

    def test_set_item_out_of_min_index(self) -> None:
        self.matrix.set_item("Change 1", self.point_lt_0, replace=True)
        self.matrix.set_item("Change 2", self.point_lt_0_a, replace=True)
        self.assertEqual(self.matrix.get_item(self.point_lt_0), "Change 1")
        self.assertEqual(self.matrix.get_item(self.point_lt_0_a), "Change 2")

    def test_get_item_out_of_max_index(self) -> None:
        self.assertEqual(self.matrix.get_item(self.point_gt_9), self.expected_gt_9_value)
        self.assertEqual(self.matrix.get_item(self.point_gt_9_a), self.expected_gt_9_a_value)

    def test_set_item_out_of_max_index(self) -> None:
        self.matrix.set_item("Change 3", self.point_gt_9, replace=True)
        self.matrix.set_item("Change 4", self.point_gt_9_a, replace=True)
        self.assertEqual(self.matrix.get_item(self.point_gt_9), "Change 3")
        self.assertEqual(self.matrix.get_item(self.point_gt_9_a), "Change 4")

    def test_remove_item(self) -> None:
        to_remove = matrix.Point.zero()
        self.matrix.remove_item(to_remove)
        self.assertIsNone(self.matrix.get_item(matrix.Point.zero()))

    def test_same_point(self) -> None:
        self.assertTrue(self.matrix.same_point(matrix.Point.zero(), self.matrix.normalize_point(matrix.Point(10, 5))))

    @staticmethod
    def disconnect():
        util.testing = False

    @classmethod
    def tearDown(cls):
        cls.disconnect()
