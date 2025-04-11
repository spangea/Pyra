import unittest
from lyra.datascience.datascience_type_domain import DatascienceTypeLattice


class TestDatascienceTypeLattice(unittest.TestCase):

    @staticmethod
    def bottom_el() -> DatascienceTypeLattice:
        return DatascienceTypeLattice().bottom()

    @staticmethod
    def top_el() -> DatascienceTypeLattice:
        return DatascienceTypeLattice()

    @staticmethod
    def series() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.Series)

    @staticmethod
    def ratio_series() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.RatioSeries)

    @staticmethod
    def exp_series() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.ExpSeries)

    @staticmethod
    def std_series() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.StdSeries)

    @staticmethod
    def norm_series() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.NormSeries)

    @staticmethod
    def cat_series() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.CatSeries)

    @staticmethod
    def numeric_series() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.NumericSeries)

    @staticmethod
    def string_series() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.StringSeries)

    @staticmethod
    def data_frame() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.DataFrame)

    @staticmethod
    def string() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.String)

    @staticmethod
    def numeric() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.Numeric)

    @staticmethod
    def array() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.Array)

    @staticmethod
    def list() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.List)

    @staticmethod
    def tuple() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.Tuple)

    @staticmethod
    def dict() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.Dict)

    @staticmethod
    def boolean() -> DatascienceTypeLattice:
        return DatascienceTypeLattice(DatascienceTypeLattice.Status.Boolean)

    @staticmethod
    def clone(t) -> DatascienceTypeLattice:
        return DatascienceTypeLattice(t.element)

    def test_is_top(self):
        """
        Test the `is_top` method for all types in `DatascienceTypeLattice`.

        Asserts that `is_top()` returns True for the top element and False for all other types.
        """
        for t in DatascienceTypeLattice.get_all_types():
            if t == self.top_el():
                self.assertTrue(t.is_top())
            else:
                self.assertFalse(t.is_top())

    def test_is_bottom(self):
        """
         Test the `is_bottom` method for all types in `DatascienceTypeLattice`.

         Asserts that `is_bottom()` returns True for the bottom element and False for all other types.
         """
        for t in DatascienceTypeLattice.get_all_types():
            if t == self.bottom_el():
                self.assertTrue(t.is_bottom())
            else:
                self.assertFalse(t.is_bottom())

    def test_less_equal_top(self):
        """
        Test `_less_equal` method for all types in `DatascienceTypeLattice` against the top element.

        Asserts that:
        - Each type is less than or equal to the top element.
        - The top element is not less than any type except itself.
        """
        for t in DatascienceTypeLattice.get_all_types():
            self.assertTrue(t._less_equal(self.top_el()))
            if t != self.top_el():
                self.assertFalse(self.top_el()._less_equal(t))

    def test_less_equal_bottom(self):
        """
        Test `_less_equal` method for all types in `DatascienceTypeLattice` against the bottom element.

        Asserts that:
        - The bottom element is less than or equal to every type.
        - No type (except itself) is less than or equal to the bottom element.
        """
        for t in DatascienceTypeLattice.get_all_types():
            self.assertTrue(self.bottom_el()._less_equal(t))
            if t != self.bottom_el():
                self.assertFalse(t._less_equal(self.bottom_el()))

    def test_less_equal_same(self):
        """
        Test `_less_equal` method for each type in `DatascienceTypeLattice` against itself.

        Asserts that each type is less than or equal to itself, ensuring reflexivity of the `_less_equal` method.
        """
        for t in DatascienceTypeLattice.get_all_types():
            self.assertTrue(t._less_equal(t))

    def test_less_equal(self):
        self.assertTrue(self.numeric_series()._less_equal(self.series()))
        self.assertFalse(self.series()._less_equal(self.numeric_series()))
        self.assertTrue(self.string_series()._less_equal(self.series()))
        self.assertFalse(self.series()._less_equal(self.string_series()))

        for num_series_status in DatascienceTypeLattice._numeric_series_types():
            self.assertTrue(DatascienceTypeLattice(num_series_status)._less_equal(self.numeric_series()))
            if num_series_status != DatascienceTypeLattice.Status.NumericSeries:
                self.assertFalse(self.numeric_series()._less_equal(DatascienceTypeLattice(num_series_status)))

        for string_series_status in DatascienceTypeLattice._string_series_types():
            self.assertTrue(DatascienceTypeLattice(string_series_status)._less_equal(self.string_series()))
            if string_series_status != DatascienceTypeLattice.Status.StringSeries:
                self.assertFalse(self.string_series()._less_equal(DatascienceTypeLattice(string_series_status)))

        for array_status in DatascienceTypeLattice._array_types():
            self.assertTrue(DatascienceTypeLattice(array_status)._less_equal(self.array()))
            if array_status != DatascienceTypeLattice.Status.Array:
                self.assertFalse(self.array()._less_equal(DatascienceTypeLattice(array_status)))

        for list_status in DatascienceTypeLattice._list_types():
            self.assertTrue(DatascienceTypeLattice(list_status)._less_equal(self.list()))
            if list_status != DatascienceTypeLattice.Status.List:
                self.assertFalse(self.list()._less_equal(DatascienceTypeLattice(list_status)))

    def test_join_top(self):
        """
        Test `_join` method when joining any type with the top element.

        This test asserts that joining any type `t` with the top element results in the top element itself.
        """
        for t in DatascienceTypeLattice.get_all_types():
            self.assertEqual(self.top_el()._join(t), self.top_el())
            self.assertEqual(t._join(self.top_el()), self.top_el())

    def test_join_bottom(self):
        """
        Test `_join` method when joining any type with the bottom element.

        This test asserts that joining any type `t` with the bottom element results in `t`.
        """
        for t in DatascienceTypeLattice.get_all_types():
            t_c = self.clone(t)
            self.assertEqual(self.bottom_el()._join(t), t_c)
            self.assertEqual(t._join(self.bottom_el()), t_c)

    def test_meet_top(self):
        """
         Test `_meet` method when meeting any type with the top element.

         This test asserts that meeting any type `t` with the top element results in `t`.
         """
        for t in DatascienceTypeLattice.get_all_types():
            t_c = self.clone(t)
            self.assertEqual(self.top_el()._meet(t), t_c)
            self.assertEqual(t._meet(self.top_el()), t_c)

    def test_meet_bottom(self):
        """
         Test `_meet` method when meeting any type with the bottom element.

         This test asserts that meeting any type `t` with the bottom element results in the bottom element itself.
         """
        for t in DatascienceTypeLattice.get_all_types():
            self.assertEqual(self.bottom_el()._meet(t), self.bottom_el())
            self.assertEqual(t._meet(self.bottom_el()), self.bottom_el())

    def _assert_operation(self, s1, s2, op, expected):
        """Tests the op operation of two types s1 and s2 (e.g., tests s1 op s2 and s2 op s1).

          :param s1: the first element
          :param s2: the second element
          :param op: the operation to apply
          :param expected: the expected result of s1 op s2
        """
        self.assertEqual(op(DatascienceTypeLattice(s1), DatascienceTypeLattice(s2)), expected)
        self.assertEqual(op(DatascienceTypeLattice(s2), DatascienceTypeLattice(s1)), expected)

    def _test_meet_same_type(self, group_types, sub_top):
        """Assert the meet operation of a group of types.

          :param group_types: the group of types
          :param sub_top: the highest element of group_types
        """
        for s1 in group_types:
            for s2 in group_types:
                if s1 == s2 or s1 == sub_top:
                    self._assert_operation(s1, s2, lambda x, y: x._meet(y), DatascienceTypeLattice(s2))
                elif s2 == sub_top:
                    self._assert_operation(s1, s2, lambda x, y: x._meet(y), DatascienceTypeLattice(s1))
                else:
                    self._assert_operation(s1, s2, lambda x, y: x._meet(y), self.bottom_el())

    def _test_join_same_type(self, group_types, sub_top):
        """Tests the join operation of a group of types.

          :param group_types: the group of types
          :param sub_top: the highest element of group_types
        """
        for s1 in group_types:
            for s2 in group_types:
                if s1 == s2:
                    self._assert_operation(s1, s2, lambda x, y: x._join(y), DatascienceTypeLattice(s1))
                elif s1 == sub_top or s2 == sub_top:
                    self._assert_operation(s1, s2, lambda x, y: x._join(y), DatascienceTypeLattice(sub_top))
                else:
                    self._assert_operation(s1, s2, lambda x, y: x._join(y), DatascienceTypeLattice(sub_top))

    def _test_operation_different_groups(self, groups, op, expected):
        """Tests the operation op of groups of different types. Taken two elements from two different groups of types
        should return expected.

        :param groups: the groups of types
        :param op: the operation
        :param expected: the highest element of group_types
        """
        for i, group1 in enumerate(groups):
            for j, group2 in enumerate(groups):
                # Test operation for all pairs of types between group1 and group2
                for s1 in group1:
                    for s2 in group2:
                        if i != j:
                            self._assert_operation(s1, s2, op, expected)

    def test_meet(self):
        """Test the meet operator for types that are neither the bottom type nor the top type."""
        operation = lambda x, y: x._meet(y)

        # Testing meet within string series types
        self._test_meet_same_type(DatascienceTypeLattice._string_series_types(),
                                       DatascienceTypeLattice.Status.StringSeries)

        # Test meet within numeric series types
        self._test_meet_same_type(DatascienceTypeLattice._numeric_series_types(),
                                       DatascienceTypeLattice.Status.NumericSeries)

        # Test meet within array types
        self._test_meet_same_type(DatascienceTypeLattice._array_types(),
                                       DatascienceTypeLattice.Status.Array)

        # Test meet within primitive types
        self._test_meet_same_type(DatascienceTypeLattice._scalar_types(),
                                  DatascienceTypeLattice.Status.Scalar)

        # Test meet within list types
        self._test_meet_same_type(DatascienceTypeLattice._list_types(),
                                       DatascienceTypeLattice.Status.List)

        # Test meet within atom types
        self._test_meet_same_type(DatascienceTypeLattice._atom_types(),
                                       self.bottom_el())

        # Test meet across different type groups
        groups = [
            DatascienceTypeLattice._numeric_series_types(),
            DatascienceTypeLattice._string_series_types(),
            DatascienceTypeLattice._array_types(),
            DatascienceTypeLattice._list_types(),
            DatascienceTypeLattice._atom_types(),
            DatascienceTypeLattice._scalar_types(),
            {DatascienceTypeLattice.Status.BoolSeries}
        ]

        self._test_operation_different_groups(groups, operation, self.bottom_el())

    def test_join(self):
        """Test the join operator for types that are neither the bottom type nor the top type."""
        operation = lambda x, y: x._join(y)

        # Testing join within string series types
        self._test_join_same_type(DatascienceTypeLattice._string_series_types(),
                                       DatascienceTypeLattice.Status.StringSeries)

        # Test join within numeric series types
        self._test_join_same_type(DatascienceTypeLattice._numeric_series_types(),
                                       DatascienceTypeLattice.Status.NumericSeries)

        # Test join within array types
        self._test_join_same_type(DatascienceTypeLattice._array_types(),
                                       DatascienceTypeLattice.Status.Array)

        # Test join within primitive types
        self._test_join_same_type(DatascienceTypeLattice._scalar_types(),
                                  DatascienceTypeLattice.Status.Scalar)

        # Test join within atom types
        self._test_join_same_type(DatascienceTypeLattice._atom_types(),
                                  DatascienceTypeLattice.Status.Top)

        # Test join across different type groups
        groups = [
            DatascienceTypeLattice._string_series_types(),
            DatascienceTypeLattice._array_types(),
            DatascienceTypeLattice._list_types(),
            DatascienceTypeLattice._scalar_types(),
            DatascienceTypeLattice._atom_types()
        ]

        self._test_operation_different_groups(groups, operation, self.top_el())

        groups = [
            DatascienceTypeLattice._numeric_series_types(),
            DatascienceTypeLattice._array_types(),
            DatascienceTypeLattice._list_types(),
            DatascienceTypeLattice._scalar_types(),
            DatascienceTypeLattice._atom_types()
        ]

        self._test_operation_different_groups(groups, operation, self.top_el())

        groups = [
            DatascienceTypeLattice._numeric_series_types(),
            DatascienceTypeLattice._string_series_types(),
            {DatascienceTypeLattice.Status.BoolSeries}
        ]

        self._test_operation_different_groups(groups, operation, self.series())

    def test_widening(self):
        """
        Test the `widening` method.

        Since the widening operator relies on the join,
        this test verifies that `t1.join(t2)` is equal to `t1.widening(t2)` for all t1 and t2 types.
        """
        for t1 in DatascienceTypeLattice.get_all_types():
            for t2 in DatascienceTypeLattice.get_all_types():
                t1_c = self.clone(t1)
                t2_c = self.clone(t2)
                self.assertEqual(t1.join(t2), t1_c.widening(t2_c))


if __name__ == '__main__':
    unittest.main()