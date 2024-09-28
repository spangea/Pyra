import unittest
from lyra.statistical.statistical_type_domain import StatisticalTypeLattice


class TestStatisticalTypeLattice(unittest.TestCase):

    @staticmethod
    def bottom_el() -> StatisticalTypeLattice:
        return StatisticalTypeLattice().bottom()

    @staticmethod
    def top_el() -> StatisticalTypeLattice:
        return StatisticalTypeLattice()

    @staticmethod
    def series() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.Series)

    @staticmethod
    def ratio_series() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.RatioSeries)

    @staticmethod
    def exp_series() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.ExpSeries)

    @staticmethod
    def int_series() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.IntSeries)

    @staticmethod
    def std_series() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.StdSeries)

    @staticmethod
    def norm_series() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.NormSeries)

    @staticmethod
    def cat_series() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.CatSeries)

    @staticmethod
    def numeric_series() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.NumericSeries)

    @staticmethod
    def string_series() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.StringSeries)

    @staticmethod
    def data_frame() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.DataFrame)

    @staticmethod
    def string() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.String)

    @staticmethod
    def numeric() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.Numeric)

    @staticmethod
    def array() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.Array)

    @staticmethod
    def list() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.List)

    @staticmethod
    def tuple() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.Tuple)

    @staticmethod
    def dict() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.Dict)

    @staticmethod
    def boolean() -> StatisticalTypeLattice:
        return StatisticalTypeLattice(StatisticalTypeLattice.Status.Boolean)

    def test_is_top(self):
        """
        Test the `is_top` method for all types in `StatisticalTypeLattice`.

        Asserts that `is_top()` returns True for the top element and False for all other types.
        """
        for t in StatisticalTypeLattice.get_all_types():
            if t == self.top_el():
                self.assertTrue(t.is_top())
            else:
                self.assertFalse(t.is_top())

    def test_is_bottom(self):
        """
         Test the `is_bottom` method for all types in `StatisticalTypeLattice`.

         Asserts that `is_bottom()` returns True for the bottom element and False for all other types.
         """
        for t in StatisticalTypeLattice.get_all_types():
            if t == self.bottom_el():
                self.assertTrue(t.is_bottom())
            else:
                self.assertFalse(t.is_bottom())

    def test_less_equal_top(self):
        """
        Test `_less_equal` method for all types in `StatisticalTypeLattice` against the top element.

        Asserts that:
        - Each type is less than or equal to the top element.
        - The top element is not less than any type except itself.
        """
        for t in StatisticalTypeLattice.get_all_types():
            self.assertTrue(t._less_equal(self.top_el()))
            if t != self.top_el():
                self.assertFalse(self.top_el()._less_equal(t))

    def test_less_equal_bottom(self):
        """
        Test `_less_equal` method for all types in `StatisticalTypeLattice` against the bottom element.

        Asserts that:
        - The bottom element is less than or equal to every type.
        - No type (except itself) is less than or equal to the bottom element.
        """
        for t in StatisticalTypeLattice.get_all_types():
            self.assertTrue(self.bottom_el()._less_equal(t))
            if t != self.bottom_el():
                self.assertFalse(t._less_equal(self.bottom_el()))

    def test_less_equal_same(self):
        """
        Test `_less_equal` method for each type in `StatisticalTypeLattice` against itself.

        Asserts that each type is less than or equal to itself, ensuring reflexivity of the `_less_equal` method.
        """
        for t in StatisticalTypeLattice.get_all_types():
            self.assertTrue(t._less_equal(t))

    def test_less_equal(self):
        self.assertTrue(self.numeric_series()._less_equal(self.series()))
        self.assertFalse(self.series()._less_equal(self.numeric_series()))
        self.assertTrue(self.string_series()._less_equal(self.series()))
        self.assertFalse(self.series()._less_equal(self.string_series()))

        for num_series_status in StatisticalTypeLattice._numeric_series_types():
            self.assertTrue(StatisticalTypeLattice(num_series_status)._less_equal(self.numeric_series()))
            if num_series_status != StatisticalTypeLattice.Status.NumericSeries:
                self.assertFalse(self.numeric_series()._less_equal(StatisticalTypeLattice(num_series_status)))

        for string_series_status in StatisticalTypeLattice._string_series_types():
            self.assertTrue(StatisticalTypeLattice(string_series_status)._less_equal(self.string_series()))
            if string_series_status != StatisticalTypeLattice.Status.StringSeries:
                self.assertFalse(self.string_series()._less_equal(StatisticalTypeLattice(string_series_status)))

        for array_status in StatisticalTypeLattice._array_types():
            self.assertTrue(StatisticalTypeLattice(array_status)._less_equal(self.array()))
            if array_status != StatisticalTypeLattice.Status.Array:
                self.assertFalse(self.array()._less_equal(StatisticalTypeLattice(array_status)))

        for list_status in StatisticalTypeLattice._list_types():
            self.assertTrue(StatisticalTypeLattice(list_status)._less_equal(self.list()))
            if list_status != StatisticalTypeLattice.Status.List:
                self.assertFalse(self.list()._less_equal(StatisticalTypeLattice(list_status)))

    def test_neg_top(self):
        self.assertEqual(self.top_el()._neg(), self.top_el())
        self.assertEqual(self.ratio_series()._neg(), self.top_el())
        self.assertEqual(self.string()._neg(), self.top_el())
        self.assertEqual(self.boolean()._neg(), self.top_el())
        self.assertEqual(self.bottom_el()._neg(), self.top_el())

    def test_neg(self):
        self.assertEqual(self.series()._neg(), self.series())
        self.assertEqual(self.numeric()._neg(), self.numeric())
        self.assertEqual(self.data_frame()._neg(), self.data_frame())

    def test_add_top(self):
        self.assertEqual(self.top_el()._add(self.top_el()), self.top_el())
        self.assertEqual(self.series()._add(self.top_el()), self.top_el())
        self.assertEqual(self.ratio_series()._add(self.top_el()), self.top_el())
        self.assertEqual(self.data_frame()._add(self.top_el()), self.top_el())
        self.assertEqual(self.string()._add(self.top_el()), self.top_el())
        self.assertEqual(self.numeric()._add(self.top_el()), self.top_el())
        self.assertEqual(self.boolean()._add(self.top_el()), self.top_el())
        self.assertEqual(self.bottom_el()._add(self.top_el()), self.top_el())

    def test_add(self):
        self.assertEqual(self.numeric()._add(self.numeric()), self.numeric())
        self.assertEqual(self.series()._add(self.series()), self.series())
        self.assertEqual(self.data_frame()._add(self.data_frame()), self.data_frame())

    def test_sub_top(self):
        self.assertEqual(self.top_el()._sub(self.top_el()), self.top_el())
        self.assertEqual(self.series()._sub(self.top_el()), self.top_el())
        self.assertEqual(self.ratio_series()._sub(self.top_el()), self.top_el())
        self.assertEqual(self.data_frame()._sub(self.top_el()), self.top_el())
        self.assertEqual(self.string()._sub(self.top_el()), self.top_el())
        self.assertEqual(self.numeric()._sub(self.top_el()), self.top_el())
        self.assertEqual(self.boolean()._sub(self.top_el()), self.top_el())
        self.assertEqual(self.bottom_el()._sub(self.top_el()), self.top_el())

    def test_sub(self):
        self.assertEqual(self.series()._sub(self.series()), self.series())
        self.assertEqual(self.numeric()._sub(self.numeric()), self.numeric())
        self.assertEqual(self.data_frame()._sub(self.data_frame()), self.data_frame())

    def test_mult_top(self):
        self.assertEqual(self.top_el()._mult(self.top_el()), self.top_el())
        self.assertEqual(self.series()._mult(self.top_el()), self.top_el())
        self.assertEqual(self.ratio_series()._mult(self.top_el()), self.top_el())
        self.assertEqual(self.data_frame()._mult(self.top_el()), self.top_el())
        self.assertEqual(self.string()._mult(self.top_el()), self.top_el())
        self.assertEqual(self.numeric()._mult(self.top_el()), self.top_el())
        self.assertEqual(self.boolean()._mult(self.top_el()), self.top_el())
        self.assertEqual(self.bottom_el()._mult(self.top_el()), self.top_el())

    def test_mult(self):
        self.assertEqual(self.series()._mult(self.series()), self.series())
        self.assertEqual(self.numeric()._mult(self.numeric()), self.numeric())
        self.assertEqual(self.data_frame().mult(self.data_frame()), self.data_frame())
        self.assertEqual(self.data_frame().mult(self.numeric()), self.data_frame())
        self.assertEqual(self.numeric().mult(self.data_frame()), self.data_frame())

    def test_div_top(self):
        self.assertEqual(self.top_el()._div(self.top_el()), self.top_el())
        self.assertEqual(self.series()._div(self.top_el()), self.top_el())
        self.assertEqual(self.ratio_series()._div(self.top_el()), self.top_el())
        self.assertEqual(self.data_frame()._div(self.top_el()), self.top_el())
        self.assertEqual(self.string()._div(self.top_el()), self.top_el())
        self.assertEqual(self.numeric()._div(self.top_el()), self.top_el())
        self.assertEqual(self.boolean()._div(self.top_el()), self.top_el())
        self.assertEqual(self.bottom_el()._div(self.top_el()), self.top_el())

    def test_div(self):
        self.assertEqual(self.series()._div(self.series()), self.ratio_series())
        self.assertEqual(self.numeric()._div(self.numeric()), self.numeric())
        self.assertEqual(self.data_frame()._div(self.data_frame()), self.data_frame())

    def test_mod_top(self):
        self.assertEqual(self.top_el()._mod(self.top_el()), self.top_el())
        self.assertEqual(self.series()._mod(self.top_el()), self.top_el())
        self.assertEqual(self.ratio_series()._mod(self.top_el()), self.top_el())
        self.assertEqual(self.data_frame()._mod(self.top_el()), self.top_el())
        self.assertEqual(self.string()._mod(self.top_el()), self.top_el())
        self.assertEqual(self.numeric()._mod(self.top_el()), self.top_el())
        self.assertEqual(self.boolean()._mod(self.top_el()), self.top_el())
        self.assertEqual(self.bottom_el()._mod(self.top_el()), self.top_el())

    def test_mod(self):
        self.assertEqual(self.series()._mod(self.series()), self.series())
        self.assertEqual(self.numeric()._mod(self.numeric()), self.numeric())
        self.assertEqual(self.data_frame()._mod(self.data_frame()), self.data_frame())

    def test_concat_top(self):
        # At the moment _concat always returns top
        self.assertEqual(self.top_el()._concat(self.top_el()), self.top_el())
        self.assertEqual(self.series()._concat(self.top_el()), self.top_el())
        self.assertEqual(self.ratio_series()._concat(self.top_el()), self.top_el())
        self.assertEqual(self.data_frame()._concat(self.top_el()), self.top_el())
        self.assertEqual(self.string()._concat(self.top_el()), self.top_el())
        self.assertEqual(self.numeric()._concat(self.top_el()), self.top_el())
        self.assertEqual(self.boolean()._concat(self.top_el()), self.top_el())
        self.assertEqual(self.bottom_el()._concat(self.top_el()), self.top_el())

    def test_join_top(self):
        self.assertEqual(self.top_el()._join(self.top_el()), self.top_el())
        self.assertEqual(self.data_frame()._join(self.top_el()), self.top_el())
        self.assertEqual(self.string()._join(self.top_el()), self.top_el())
        self.assertEqual(self.numeric()._join(self.top_el()), self.top_el())
        self.assertEqual(self.boolean()._join(self.top_el()), self.top_el())
        self.assertEqual(self.bottom_el()._join(self.top_el()), self.top_el())
        self.assertEqual(self.tuple()._join(self.top_el()), self.top_el())
        self.assertEqual(self.dict()._join(self.top_el()), self.top_el())
        self.assertEqual(self.top_el()._join(self.data_frame()), self.top_el())
        self.assertEqual(self.top_el()._join(self.string()), self.top_el())
        self.assertEqual(self.top_el()._join(self.numeric()), self.top_el())
        self.assertEqual(self.top_el()._join(self.boolean()), self.top_el())
        self.assertEqual(self.top_el()._join(self.bottom_el()), self.top_el())
        self.assertEqual(self.top_el()._join(self.dict()), self.top_el())
        self.assertEqual(self.top_el()._join(self.tuple()), self.top_el())

        for string_series_status in StatisticalTypeLattice._string_series_types():
            self.assertEqual(self.top_el()._join(StatisticalTypeLattice(string_series_status)),
                             self.top_el())
            self.assertEqual(StatisticalTypeLattice(string_series_status)._join(self.top_el()),
                             self.top_el())

        for num_series_status in StatisticalTypeLattice._numeric_series_types():
            self.assertEqual(self.top_el()._join(StatisticalTypeLattice(num_series_status)),
                             self.top_el())
            self.assertEqual(StatisticalTypeLattice(num_series_status)._join(self.top_el()),
                             self.top_el())

        for array_status in StatisticalTypeLattice._array_types():
            self.assertEqual(self.top_el()._join(StatisticalTypeLattice(array_status)),
                             self.top_el())
            self.assertEqual(StatisticalTypeLattice(array_status)._join(self.top_el()),
                             self.top_el())

        for list_status in StatisticalTypeLattice._list_types():
            self.assertEqual(self.top_el()._join(StatisticalTypeLattice(list_status)),
                             self.top_el())
            self.assertEqual(StatisticalTypeLattice(list_status)._join(self.top_el()),
                             self.top_el())

        self.assertEqual(self.top_el()._join(self.series()), self.top_el())
        self.assertEqual(self.series()._join(self.top_el()), self.top_el())
        self.assertEqual(self.array()._join(self.top_el()), self.top_el())

    def test_join_bottom(self):
        self.assertEqual(self.data_frame()._join(self.bottom_el()), self.data_frame())
        self.assertEqual(self.string()._join(self.bottom_el()), self.string())
        self.assertEqual(self.numeric()._join(self.bottom_el()), self.numeric())
        self.assertEqual(self.tuple()._join(self.bottom_el()), self.tuple())
        self.assertEqual(self.dict()._join(self.bottom_el()), self.dict())
        self.assertEqual(self.boolean()._join(self.bottom_el()), self.boolean())
        self.assertEqual(self.top_el()._join(self.bottom_el()), self.top_el())
        self.assertEqual(self.bottom_el()._join(self.bottom_el()), self.bottom_el())
        self.assertEqual(self.bottom_el()._join(self.data_frame()), self.data_frame())
        self.assertEqual(self.bottom_el()._join(self.string()), self.string())
        self.assertEqual(self.bottom_el()._join(self.numeric()), self.numeric())
        self.assertEqual(self.bottom_el()._join(self.boolean()), self.boolean())
        self.assertEqual(self.bottom_el()._join(self.top_el()), self.top_el())
        self.assertEqual(self.bottom_el()._join(self.tuple()), self.tuple())
        self.assertEqual(self.bottom_el()._join(self.dict()), self.dict())

        for string_series_status in StatisticalTypeLattice._string_series_types():
            self.assertEqual(self.bottom_el()._join(StatisticalTypeLattice(string_series_status)),
                             StatisticalTypeLattice(string_series_status))
            self.assertEqual(StatisticalTypeLattice(string_series_status)._join(self.bottom_el()),
                             StatisticalTypeLattice(string_series_status))

        for num_series_status in StatisticalTypeLattice._numeric_series_types():
            self.assertEqual(self.bottom_el()._join(StatisticalTypeLattice(num_series_status)),
                             StatisticalTypeLattice(num_series_status))
            self.assertEqual(StatisticalTypeLattice(num_series_status)._join(self.bottom_el()),
                             StatisticalTypeLattice(num_series_status))

        for array_status in StatisticalTypeLattice._array_types():
            self.assertEqual(self.bottom_el()._join(StatisticalTypeLattice(array_status)),
                             StatisticalTypeLattice(array_status))
            self.assertEqual(StatisticalTypeLattice(array_status)._join(self.bottom_el()),
                             StatisticalTypeLattice(array_status))

        for list_status in StatisticalTypeLattice._list_types():
            self.assertEqual(self.bottom_el()._join(StatisticalTypeLattice(list_status)),
                             StatisticalTypeLattice(list_status))
            self.assertEqual(StatisticalTypeLattice(list_status)._join(self.bottom_el()),
                             StatisticalTypeLattice(list_status))

        self.assertEqual(self.bottom_el()._join(self.series()), self.series())
        self.assertEqual(self.series()._join(self.bottom_el()), self.series())
        self.assertEqual(self.array()._join(self.bottom_el()), self.array())

    def test_join(self):
        for string_series_status in StatisticalTypeLattice._string_series_types():
            self.assertEqual(StatisticalTypeLattice(string_series_status)._join(self.series()), self.series())
            self.assertEqual(StatisticalTypeLattice(string_series_status)._join(self.string_series()), self.string_series(), string_series_status)
            self.assertEqual(self.series()._join(StatisticalTypeLattice(string_series_status)), self.series())
            self.assertEqual(self.string_series()._join(StatisticalTypeLattice(string_series_status)), self.string_series())

            self.assertEqual(StatisticalTypeLattice(string_series_status)._join(self.data_frame()), self.top_el())
            self.assertEqual(StatisticalTypeLattice(string_series_status)._join(self.numeric()), self.top_el())
            self.assertEqual(StatisticalTypeLattice(string_series_status)._join(self.string()), self.top_el())
            self.assertEqual(StatisticalTypeLattice(string_series_status)._join(self.boolean()), self.top_el())

        for num_series_status in StatisticalTypeLattice._numeric_series_types():
            self.assertEqual(StatisticalTypeLattice(num_series_status)._join(self.series()), self.series())
            self.assertEqual(StatisticalTypeLattice(num_series_status)._join(self.numeric_series()), self.numeric_series())
            self.assertEqual(self.series()._join(StatisticalTypeLattice(num_series_status)), self.series())
            self.assertEqual(self.numeric_series()._join(StatisticalTypeLattice(num_series_status)), self.numeric_series())

            self.assertEqual(StatisticalTypeLattice(num_series_status)._join(self.data_frame()), self.top_el())
            self.assertEqual(StatisticalTypeLattice(num_series_status)._join(self.numeric()), self.top_el())
            self.assertEqual(StatisticalTypeLattice(num_series_status)._join(self.string()), self.top_el())
            self.assertEqual(StatisticalTypeLattice(num_series_status)._join(self.boolean()), self.top_el())

        for array_status in StatisticalTypeLattice._array_types():
            self.assertEqual(StatisticalTypeLattice(array_status)._join(self.array()), self.array())
            self.assertEqual(StatisticalTypeLattice(array_status)._join(self.array()),
                             self.array())
            self.assertEqual(self.array()._join(StatisticalTypeLattice(array_status)), self.array())

            self.assertEqual(StatisticalTypeLattice(array_status)._join(self.data_frame()), self.top_el())
            self.assertEqual(StatisticalTypeLattice(array_status)._join(self.numeric()), self.top_el())
            self.assertEqual(StatisticalTypeLattice(array_status)._join(self.string()), self.top_el())
            self.assertEqual(StatisticalTypeLattice(array_status)._join(self.boolean()), self.top_el())

        for num_series_status in StatisticalTypeLattice._numeric_series_types():
            for string_series_status in StatisticalTypeLattice._string_series_types():
                self.assertEqual(StatisticalTypeLattice(num_series_status)._join(StatisticalTypeLattice(string_series_status)), self.series())
                self.assertEqual(StatisticalTypeLattice(string_series_status)._join(StatisticalTypeLattice(num_series_status)), self.series())

        self.assertEqual(self.string_series()._join(self.numeric_series()), self.series())
        self.assertEqual(self.numeric_series()._join(self.string_series()), self.series())


    def test_meet_top(self):
        self.assertEqual(self.top_el()._meet(self.top_el()), self.top_el())
        self.assertEqual(self.data_frame()._meet(self.top_el()), self.data_frame())
        self.assertEqual(self.string()._meet(self.top_el()), self.string())
        self.assertEqual(self.numeric()._meet(self.top_el()), self.numeric())
        self.assertEqual(self.tuple()._meet(self.top_el()), self.tuple())
        self.assertEqual(self.dict()._meet(self.top_el()), self.dict())
        self.assertEqual(self.boolean()._meet(self.top_el()), self.boolean())
        self.assertEqual(self.bottom_el()._meet(self.top_el()), self.bottom_el())
        self.assertEqual(self.top_el()._meet(self.string()), self.string())
        self.assertEqual(self.top_el()._meet(self.numeric()), self.numeric())
        self.assertEqual(self.top_el()._meet(self.boolean()), self.boolean())
        self.assertEqual(self.top_el()._meet(self.data_frame()), self.data_frame())
        self.assertEqual(self.top_el()._meet(self.bottom_el()), self.bottom_el())

        for string_series_status in StatisticalTypeLattice._string_series_types():
            self.assertEqual(self.top_el()._meet(StatisticalTypeLattice(string_series_status)), StatisticalTypeLattice(string_series_status))
            self.assertEqual(StatisticalTypeLattice(string_series_status)._meet(self.top_el()), StatisticalTypeLattice(string_series_status))

        for num_series_status in StatisticalTypeLattice._numeric_series_types():
            self.assertEqual(self.top_el()._meet(StatisticalTypeLattice(num_series_status)), StatisticalTypeLattice(num_series_status))
            self.assertEqual(StatisticalTypeLattice(num_series_status)._meet(self.top_el()), StatisticalTypeLattice(num_series_status))

        for array_status in StatisticalTypeLattice._array_types():
            self.assertEqual(self.top_el()._meet(StatisticalTypeLattice(array_status)), StatisticalTypeLattice(array_status))
            self.assertEqual(StatisticalTypeLattice(array_status)._meet(self.top_el()), StatisticalTypeLattice(array_status))

        self.assertEqual(self.top_el()._meet(self.series()), self.series())
        self.assertEqual(self.series()._meet(self.top_el()), self.series())

    def test_meet_bottom(self):
        self.assertEqual(self.data_frame()._meet(self.bottom_el()), self.bottom_el())
        self.assertEqual(self.string()._meet(self.bottom_el()), self.bottom_el())
        self.assertEqual(self.numeric()._meet(self.bottom_el()), self.bottom_el())
        self.assertEqual(self.tuple()._meet(self.bottom_el()), self.bottom_el())
        self.assertEqual(self.dict()._meet(self.bottom_el()), self.bottom_el())
        self.assertEqual(self.boolean()._meet(self.bottom_el()), self.bottom_el())
        self.assertEqual(self.top_el()._meet(self.bottom_el()), self.bottom_el())
        self.assertEqual(self.bottom_el()._meet(self.bottom_el()), self.bottom_el())
        self.assertEqual(self.bottom_el()._meet(self.series()), self.bottom_el())
        self.assertEqual(self.bottom_el()._meet(self.data_frame()), self.bottom_el())
        self.assertEqual(self.bottom_el()._meet(self.string()), self.bottom_el())
        self.assertEqual(self.bottom_el()._meet(self.numeric()), self.bottom_el())
        self.assertEqual(self.bottom_el()._meet(self.boolean()), self.bottom_el())
        self.assertEqual(self.bottom_el()._meet(self.top_el()), self.bottom_el())

        for string_series_status in StatisticalTypeLattice._string_series_types():
            self.assertEqual(self.bottom_el()._meet(StatisticalTypeLattice(string_series_status)), self.bottom_el())
            self.assertEqual(StatisticalTypeLattice(string_series_status)._meet(self.bottom_el()), self.bottom_el())

        for num_series_status in StatisticalTypeLattice._numeric_series_types():
            self.assertEqual(self.bottom_el()._meet(StatisticalTypeLattice(num_series_status)), self.bottom_el())
            self.assertEqual(StatisticalTypeLattice(num_series_status)._meet(self.bottom_el()), self.bottom_el())

        for array_status in StatisticalTypeLattice._array_types():
            self.assertEqual(self.bottom_el()._meet(StatisticalTypeLattice(array_status)), self.bottom_el())
            self.assertEqual(StatisticalTypeLattice(array_status)._meet(self.bottom_el()), self.bottom_el())

        self.assertEqual(self.bottom_el()._meet(self.series()), self.bottom_el())
        self.assertEqual(self.series()._meet(self.bottom_el()), self.bottom_el())

    def test_meet(self):
        for s1 in StatisticalTypeLattice._string_series_types():
            for s2 in StatisticalTypeLattice._string_series_types():
                if s1 == s2:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)),
                                     StatisticalTypeLattice(s2))
                elif s1 == StatisticalTypeLattice.Status.StringSeries:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)),
                                     StatisticalTypeLattice(s2))
                elif s2 == StatisticalTypeLattice.Status.StringSeries:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)),
                                     StatisticalTypeLattice(s1))
                else:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)), self.bottom_el())

        for s1 in StatisticalTypeLattice._numeric_series_types():
            for s2 in StatisticalTypeLattice._numeric_series_types():
                if s1 == s2:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)),
                                     StatisticalTypeLattice(s2))
                elif s1 == StatisticalTypeLattice.Status.NumericSeries:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)),
                                     StatisticalTypeLattice(s2))
                elif s2 == StatisticalTypeLattice.Status.NumericSeries:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)),
                                     StatisticalTypeLattice(s1))
                else:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)), self.bottom_el())

        for s1 in StatisticalTypeLattice._array_types():
            for s2 in StatisticalTypeLattice._array_types():
                if s1 == s2:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)),
                                     StatisticalTypeLattice(s2))
                elif s1 == StatisticalTypeLattice.Status.Array:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)),
                                     StatisticalTypeLattice(s2))
                elif s2 == StatisticalTypeLattice.Status.Array:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)),
                                     StatisticalTypeLattice(s1))
                else:
                    self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)), self.bottom_el())

        for s1 in StatisticalTypeLattice._numeric_series_types():
            for s2 in StatisticalTypeLattice._string_series_types():
                self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)), self.bottom_el())
                self.assertEqual(StatisticalTypeLattice(s2)._meet(StatisticalTypeLattice(s1)), self.bottom_el())

        for s1 in StatisticalTypeLattice._array_types():
            for s2 in StatisticalTypeLattice._string_series_types():
                self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)), self.bottom_el())
                self.assertEqual(StatisticalTypeLattice(s2)._meet(StatisticalTypeLattice(s1)), self.bottom_el())

        for s1 in StatisticalTypeLattice._array_types():
            for s2 in StatisticalTypeLattice._numeric_series_types():
                self.assertEqual(StatisticalTypeLattice(s1)._meet(StatisticalTypeLattice(s2)), self.bottom_el())
                self.assertEqual(StatisticalTypeLattice(s2)._meet(StatisticalTypeLattice(s1)), self.bottom_el())

    def test_widening_top(self):
        # Widening is implemented with join, so they must have the same result
        self.assertEqual(self.top_el()._widening(self.top_el()), self.top_el()._join(self.top_el()))
        self.assertEqual(self.series()._widening(self.top_el()), self.series()._join(self.top_el()))
        self.assertEqual(self.ratio_series()._widening(self.top_el()), self.ratio_series()._join(self.top_el()))
        self.assertEqual(self.data_frame()._widening(self.top_el()), self.data_frame()._join(self.top_el()))
        self.assertEqual(self.string()._widening(self.top_el()), self.string()._join(self.top_el()))
        self.assertEqual(self.numeric()._widening(self.top_el()), self.numeric()._join(self.top_el()))
        self.assertEqual(self.boolean()._widening(self.top_el()), self.boolean()._join(self.top_el()))
        self.assertEqual(self.bottom_el()._widening(self.top_el()), self.bottom_el()._join(self.top_el()))

    def test_top(self):
        self.assertEqual(self.top_el().top(), self.top_el())
        self.assertEqual(self.series().top(), self.top_el())
        self.assertEqual(self.ratio_series().top(), self.top_el())
        self.assertEqual(self.data_frame().top(), self.top_el())
        self.assertEqual(self.string().top(), self.top_el())
        self.assertEqual(self.numeric().top(), self.top_el())
        self.assertEqual(self.boolean().top(), self.top_el())
        self.assertEqual(self.bottom_el().top(), self.top_el())

    def test_bottom(self):
        self.assertEqual(self.top_el().bottom(), self.bottom_el())
        self.assertEqual(self.series().bottom(), self.bottom_el())
        self.assertEqual(self.ratio_series().bottom(), self.bottom_el())
        self.assertEqual(self.data_frame().bottom(), self.bottom_el())
        self.assertEqual(self.string().bottom(), self.bottom_el())
        self.assertEqual(self.numeric().bottom(), self.bottom_el())
        self.assertEqual(self.boolean().bottom(), self.bottom_el())
        self.assertEqual(self.bottom_el().bottom(), self.bottom_el())

if __name__ == '__main__':
    unittest.main()