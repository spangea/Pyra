import copy
import warnings
from collections import defaultdict
from copy import deepcopy
from enum import IntEnum
from functools import reduce
from typing import Set, Union

from lyra.abstract_domains.assumption.assumption_domain import InputMixin, JSONMixin
from lyra.abstract_domains.lattice import BottomMixin, ArithmeticMixin, SequenceMixin
from lyra.abstract_domains.state import State, StateWithSummarization
from lyra.abstract_domains.store import Store
from lyra.core.expressions import VariableIdentifier, Expression, ExpressionVisitor, Literal, \
    Input, ListDisplay, Range, AttributeReference, Subscription, Slicing, \
    UnaryArithmeticOperation, BinaryArithmeticOperation, LengthIdentifier, TupleDisplay, \
    SetDisplay, DictDisplay, BinarySequenceOperation, BinaryComparisonOperation, Keys, Values, \
    KeysIdentifier, ValuesIdentifier, CastOperation, Status
from lyra.core.types import LyraType, BooleanLyraType, IntegerLyraType, FloatLyraType, \
    StringLyraType, ListLyraType, SequenceLyraType, SetLyraType, TupleLyraType, DictLyraType, \
    ContainerLyraType, DataFrameLyraType, SeriesLyraType, NoneLyraType, TopLyraType
from lyra.core.utils import copy_docstring
from lyra.core.statements import VariableAccess, AttributeAccess

from lyra.abstract_domains.basis import BasisWithSummarization

from lyra.core.statistical_warnings import InconsistentTypeWarning, NoneRetAssignmentWarning, HighDimensionalityWarning

# TODO: Check correctness and update documentation and operators


class StatisticalTypeLattice(BottomMixin, ArithmeticMixin, SequenceMixin, JSONMixin):
    from enum import IntEnum

    class Status(IntEnum):
        Top = 54

        # Transformations
        PCA = 53

        # Tensor
        Tensor = 52

        # Split Data
        SplittedTestData = 51
        SplittedTrainData = 50

        # None
        NoneRet = 49

        # Plot
        Plot = 48

        # Feature Selection
        FeatureSelector = 47
        FeatureSelected = 46

        # Encoders
        KBinsDiscretizer = 45
        MultiLabelBinarizer = 44
        TargetEncoder = 43
        Binarizer = 42
        LabelBinarizer = 41
        OrdinalEncoder = 40
        OneHotEncoder = 39
        LabelEncoder = 38

        # Scalers
        FunctionTransformer = 37
        KernelCenterer = 36
        Normalizer = 35
        PolynomialFeatures = 34
        PowerTransformer = 33
        QuantileTransformer = 32
        RobustScaler = 31
        SplineTransformer = 30
        MaxAbsScaler = 29
        MinMaxScaler = 28
        StandardScaler = 27
        Scaled = 26

        # Scalar
        Scalar = 25

        # Series types
        Series = 24
        NumericSeries = 23
        RatioSeries = 22
        ExpSeries = 21
        NormSeries = 20
        StdSeries = 19
        CatSeries = 18
        StringSeries = 17
        BoolSeries = 16

        # DataFrame
        DataFrame = 15
        DataFrameFromPCA = 14

        # Array types
        Array = 13
        NumericArray = 12
        BoolArray = 11
        StringArray = 10

        # List types
        List = 9
        NumericList = 8
        BoolList = 7
        StringList = 6

        # Tuple, Set, and Dict
        Tuple = 5
        Set = 4
        Dict = 3

        # Primitive types
        String = 2
        Numeric = 1
        Boolean = 0

    def __init__(self, statistical_type: Status = Status.Top):
        super().__init__()
        self._element = statistical_type

    @classmethod
    def from_lyra_type(cls, lyra_type: LyraType):
        return cls(resolve(lyra_type))

    @property
    def element(self):
        """Current lattice element.

        :return: the current lattice element if the type is not bottom, ``None`` otherwise
        """
        if self.is_bottom():
            return None
        return self._element

    def __repr__(self):
        if self.is_bottom():
            return "⊥"
        return self.element.name

    def _neg(self) -> 'StatisticalTypeLattice':
        if self.is_bottom() :
            return self._replace(self.bottom())
        elif self.element == StatisticalTypeLattice.Status.Series:
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.Series))
        elif self.element == StatisticalTypeLattice.Status.Numeric:
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.Numeric))
        elif self.element == StatisticalTypeLattice.Status.DataFrame:
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.DataFrame))
        return self._replace(self.top())

    def _add(self, other: 'StatisticalTypeLattice') -> 'StatisticalTypeLattice':
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.element == other.element:
            if (self.element == StatisticalTypeLattice.Status.Series
                    or self.element == StatisticalTypeLattice.Status.Numeric
                    or self.element == StatisticalTypeLattice.Status.String
                    or self.element == StatisticalTypeLattice.Status.DataFrame
                    or self.element == StatisticalTypeLattice.Status.Tensor):
                return self

        elif self.element == StatisticalTypeLattice.Status.Series and other.element == StatisticalTypeLattice.Status.Numeric:
            return self
        elif (self.element == StatisticalTypeLattice.Status.DataFrame and
              other.element in {StatisticalTypeLattice.Status.Numeric,
                                StatisticalTypeLattice.Status.Series,
                                StatisticalTypeLattice.Status.Dict,
                                StatisticalTypeLattice.Status.List}):
            return self
        return self._replace(self.top())

    def _sub(self, other: 'StatisticalTypeLattice') -> 'StatisticalTypeLattice':
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.element == other.element:
            if (self.element == StatisticalTypeLattice.Status.Series
                    or self.element == StatisticalTypeLattice.Status.Numeric
                    or self.element == StatisticalTypeLattice.Status.String
                    or self.element == StatisticalTypeLattice.Status.DataFrame
                    or self.element == StatisticalTypeLattice.Status.Tensor):
                return self
        return self._replace(self.top())

    def _mult(self, other: 'StatisticalTypeLattice') -> 'StatisticalTypeLattice':
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.element == other.element and other.element == StatisticalTypeLattice.Status.Series:
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.Series))
        elif self.element == other.element and other.element == StatisticalTypeLattice.Status.Numeric:
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.Numeric))
        elif self.element == other.element and other.element == StatisticalTypeLattice.Status.DataFrame:
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.DataFrame))
        elif {self.element, other.element} == {StatisticalTypeLattice.Status.DataFrame,
                                               StatisticalTypeLattice.Status.Numeric
                                               }:
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.DataFrame))
        return self._replace(self.top())

    def _div(self, other: 'StatisticalTypeLattice') -> 'StatisticalTypeLattice':
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.element == other.element:
            if self.element == StatisticalTypeLattice.Status.Series:
                return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.RatioSeries))
            elif (self.element == StatisticalTypeLattice.Status.Numeric
                    or self.element == StatisticalTypeLattice.Status.DataFrame
                    or self.element == StatisticalTypeLattice.Status.Tensor):
                return self
        return self._replace(self.top())

    def _mod(self, other: 'StatisticalTypeLattice') -> 'StatisticalTypeLattice':
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.element == other.element:
            if (self.element == StatisticalTypeLattice.Status.Series
                    or self.element == StatisticalTypeLattice.Status.Numeric
                    or self.element == StatisticalTypeLattice.Status.DataFrame):
                return self
        return self._replace(self.top())

    def _concat(self, other: 'StatisticalTypeLattice') -> 'StatisticalTypeLattice':
        return self._replace(self.top())

    def to_json(self) -> str:
        return str(self)

    @staticmethod
    def from_json(json: str) -> 'JSONMixin':
        if json == '⊥':
            return StatisticalTypeLattice().bottom()
        if json == 'Boolean':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Boolean)
        elif json == 'Numeric':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Numeric)
        elif json == 'String':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.String)
        elif json == 'RatioSeries':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.RatioSeries)
        elif json == 'DataFrame':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.DataFrame)
        elif json == 'DataFrameFromPCA':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.DataFrameFromPCA)
        elif json == 'Series':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Series)
        elif json == 'StringSeries':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.StringSeries)
        elif json == 'NumericSeries':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.NumericSeries)
        elif json == 'ExpSeries':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.ExpSeries)
        elif json == 'StdSeries':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.StdSeries)
        elif json == 'NormSeries':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.NormSeries)
        elif json == 'CatSeries':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.CatSeries)
        elif json == 'Array':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Array)
        elif json == 'BoolArray':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.BoolArray)
        elif json == 'StringArray':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.StringArray)
        elif json == 'NumericArray':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.NumericArray)
        elif json == 'List':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.List)
        elif json == 'BoolList':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.BoolList)
        elif json == 'StringList':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.StringList)
        elif json == 'NumericList':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.NumericList)
        elif json == 'Tuple':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Tuple)
        elif json == 'Dict':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Dict)
        elif json == 'Set':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Set)
        elif json == 'MaxAbsScaler':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.MaxAbsScaler)
        elif json == 'MinMaxScaler':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.MinMaxScaler)
        elif json == 'StandardScaler':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.StandardScaler)
        elif json == 'KBinsDiscretizer':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.KBinsDiscretizer)
        elif json == 'MultiLabelBinarizer':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.MultiLabelBinarizer)
        elif json == 'TargetEncoder':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.TargetEncoder)
        elif json == 'OrdinalEncoder':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.OrdinalEncoder)
        elif json == 'Binarizer':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Binarizer)
        elif json == 'OneHotEncoder':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.OneHotEncoder)
        elif json == 'LabelEncoder':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.LabelEncoder)
        elif json == 'FunctionTransformer':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.FunctionTransformer)
        elif json == 'KernelCenterer':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.KernelCenterer)
        elif json == 'Normalizer':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Normalizer)
        elif json == 'PolynomialFeatures':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.PolynomialFeatures)
        elif json == 'PowerTransformer':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.PowerTransformer)
        elif json == 'QuantileTransformer':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.QuantileTransformer)
        elif json == 'RobustScaler':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.RobustScaler)
        elif json == 'SplineTransformer':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.SplineTransformer)
        elif json == 'Scaled':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Scaled)
        elif json == 'Tensor':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Tensor)
        elif json == 'SplittedTestData':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.SplittedTestData)
        elif json == 'SplittedTrainData':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.SplittedTrainData)
        elif json == ('FeatureSelector'):
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.FeatureSelector)
        elif json == 'FeatureSelected':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.FeatureSelected)
        elif json == 'Top':
            return StatisticalTypeLattice(StatisticalTypeLattice.Status.Top)
        return StatisticalTypeLattice()

    def top(self):
        return self._replace(StatisticalTypeLattice())

    def is_top(self) -> bool:
        return self.element == StatisticalTypeLattice.Status.Top

    def _less_equal(self, other: 'StatisticalTypeLattice') -> bool:
        if other.is_top():
            return True
        elif self.element == other.element:
            return True
        elif self.is_bottom():
            return True
        elif (self.element in self._numeric_series_types()
              and other.element in {StatisticalTypeLattice.Status.NumericSeries, StatisticalTypeLattice.Status.Series}):
            return True
        elif (self.element in self._string_series_types()
              and other.element in {StatisticalTypeLattice.Status.StringSeries, StatisticalTypeLattice.Status.Series}):
            return True
        elif self.element in self._array_types() and other.element == StatisticalTypeLattice.Status.Array:
            return True
        elif self.element in self._list_types() and other.element == StatisticalTypeLattice.Status.List:
            return True
        elif self.element in self._scalar_types() and other.element == StatisticalTypeLattice.Status.Scalar:
            return True
        elif self.element == StatisticalTypeLattice.Status.DataFrameFromPCA and other.element == StatisticalTypeLattice.Status.DataFrame:
            return True
        elif (self.element in {StatisticalTypeLattice.Status.NumericSeries, StatisticalTypeLattice.Status.StringSeries,
                               StatisticalTypeLattice.Status.BoolSeries}
              and other.element == StatisticalTypeLattice.Status.Series):
            return True
        return False

    @classmethod
    def get_all_types(cls):
        return {cls(t) for t in StatisticalTypeLattice.Status}

    @classmethod
    def _dataframes_types(cls):
        s = (StatisticalTypeLattice.Status.DataFrame,
             StatisticalTypeLattice.Status.DataFrameFromPCA)
        return s

    @classmethod
    def _list_types(cls):
        s = (StatisticalTypeLattice.Status.List,
             StatisticalTypeLattice.Status.BoolList,
             StatisticalTypeLattice.Status.NumericList,
             StatisticalTypeLattice.Status.StringList)
        return s

    @classmethod
    def _scalar_types(cls):
        s = (StatisticalTypeLattice.Status.Boolean,
             StatisticalTypeLattice.Status.Numeric,
             StatisticalTypeLattice.Status.Scalar,
             StatisticalTypeLattice.Status.String)
        return s

    @classmethod
    def _array_types(cls):
        s = (StatisticalTypeLattice.Status.Array,
             StatisticalTypeLattice.Status.BoolArray,
             StatisticalTypeLattice.Status.NumericArray,
             StatisticalTypeLattice.Status.StringArray)
        return s

    @classmethod
    def _series_types(cls):
        s = (StatisticalTypeLattice.Status.Series,
             StatisticalTypeLattice.Status.NumericSeries,
             StatisticalTypeLattice.Status.RatioSeries,
             StatisticalTypeLattice.Status.ExpSeries,
             StatisticalTypeLattice.Status.StdSeries,
             StatisticalTypeLattice.Status.NormSeries,
             StatisticalTypeLattice.Status.StringSeries,
             StatisticalTypeLattice.Status.CatSeries
             )
        return s
    @classmethod
    def _numeric_series_types(cls):
        s = (StatisticalTypeLattice.Status.NumericSeries,
             StatisticalTypeLattice.Status.RatioSeries,
             StatisticalTypeLattice.Status.ExpSeries,
             StatisticalTypeLattice.Status.StdSeries,
             StatisticalTypeLattice.Status.NormSeries)
        return s

    @classmethod
    def _string_series_types(cls):
        s = (StatisticalTypeLattice.Status.StringSeries,
             StatisticalTypeLattice.Status.CatSeries)
        return s

    @classmethod
    def _is_series_type(cls, status):
        return (
                status in cls._string_series_types() or
                status in cls._numeric_series_types() or
                status == StatisticalTypeLattice.Status.BoolSeries
        )

    @classmethod
    def _is_dataframe_type(cls, status):
        return status in cls._dataframes_types()

    @classmethod
    def _atom_types(cls):
        s = (StatisticalTypeLattice.Status.NoneRet,
             StatisticalTypeLattice.Status.Plot,
             StatisticalTypeLattice.Status.Binarizer,
             StatisticalTypeLattice.Status.LabelBinarizer,
             StatisticalTypeLattice.Status.OrdinalEncoder,
             StatisticalTypeLattice.Status.OneHotEncoder,
             StatisticalTypeLattice.Status.LabelEncoder,
             StatisticalTypeLattice.Status.KBinsDiscretizer,
             StatisticalTypeLattice.Status.MultiLabelBinarizer,
             StatisticalTypeLattice.Status.TargetEncoder,
             StatisticalTypeLattice.Status.MaxAbsScaler,
             StatisticalTypeLattice.Status.MinMaxScaler,
             StatisticalTypeLattice.Status.StandardScaler,
             StatisticalTypeLattice.Status.FunctionTransformer,
             StatisticalTypeLattice.Status.KernelCenterer,
             StatisticalTypeLattice.Status.Normalizer,
             StatisticalTypeLattice.Status.PolynomialFeatures,
             StatisticalTypeLattice.Status.PowerTransformer,
             StatisticalTypeLattice.Status.QuantileTransformer,
             StatisticalTypeLattice.Status.RobustScaler,
             StatisticalTypeLattice.Status.SplineTransformer,
             StatisticalTypeLattice.Status.Scaled,
             StatisticalTypeLattice.Status.Tuple,
             StatisticalTypeLattice.Status.Set,
             StatisticalTypeLattice.Status.Dict,
             StatisticalTypeLattice.Status.Tensor,
             StatisticalTypeLattice.Status.SplittedTrainData,
             StatisticalTypeLattice.Status.SplittedTestData,
             StatisticalTypeLattice.Status.FeatureSelector,
             StatisticalTypeLattice.Status.FeatureSelected
             )
        return s

    def _join(self, other: 'StatisticalTypeLattice') -> 'StatisticalTypeLattice':
        if self.is_top() or other.is_top():
            return self._replace(self.top())
        elif self.is_bottom() and other.is_bottom():
            return self
        elif self.is_bottom():
            return self._replace(StatisticalTypeLattice(other.element))
        elif other.is_bottom():
            return self
        elif self.element == other.element:
            return self
        elif self._less_equal(other):
            return self._replace(StatisticalTypeLattice(other.element))
        elif other._less_equal(self):
            return self
        # Computes the join between types of the same group
        # Numeric series
        elif self.element in self._numeric_series_types() and other.element in self._numeric_series_types():
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.NumericSeries))
        # String series
        elif self.element in self._string_series_types() and other.element in self._string_series_types():
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.StringSeries))
        # Array
        elif self.element in self._array_types() and other.element in self._array_types():
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.Array))
        # List
        elif self.element in self._list_types() and other.element in self._list_types():
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.List))
        # Scalar values
        elif self.element in self._scalar_types() and other.element in self._scalar_types():
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.Scalar))
        # DataFrame
        elif self.element in self._dataframes_types() and other.element in self._dataframes_types():
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.DataFrame))
        # Computes the join between types of different series groups
        elif self._is_series_type(self.element) and self._is_series_type(other.element):
            return self._replace(StatisticalTypeLattice(StatisticalTypeLattice.Status.Series))
        return self._replace(self.top())

    def _meet(self, other: 'StatisticalTypeLattice'):
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.is_top():
            return self._replace(StatisticalTypeLattice(other.element))
        elif other.is_top():
            return self
        elif self.element == other.element:
            return self
        elif self._less_equal(other):
            return self
        elif other._less_equal(self):
            return self._replace(StatisticalTypeLattice(other.element))
        return self._replace(self.bottom())

    def _widening(self, other: 'StatisticalTypeLattice'):
        return self._join(other)


def resolve(typ: LyraType) -> StatisticalTypeLattice.Status:
    _typ = typ
    # FIXME: this part is useless for our domain
    """
    while isinstance(_typ, (ListLyraType, TupleLyraType, SetLyraType, DictLyraType)):
        if isinstance(_typ, (ListLyraType, SetLyraType)):
            _typ = _typ.typ
        elif isinstance(_typ, TupleLyraType):
            _typ = reduce(max, map(resolve, _typ.typs), StatisticalTypeLattice.Status.Boolean)
        elif isinstance(_typ, DictLyraType):
            _typ = max(resolve(_typ.key_typ), resolve(_typ.val_typ))
    """
    if isinstance(_typ, StatisticalTypeLattice.Status):
        return _typ
    elif isinstance(_typ, BooleanLyraType):
        return StatisticalTypeLattice.Status.Boolean
    elif isinstance(_typ, IntegerLyraType) or isinstance(_typ, FloatLyraType):
        return StatisticalTypeLattice.Status.Numeric
    elif isinstance(_typ, DataFrameLyraType):
        return StatisticalTypeLattice.Status.DataFrame
    elif isinstance(_typ, SeriesLyraType):
        return StatisticalTypeLattice.Status.Series
    elif isinstance(_typ, StringLyraType):
        return StatisticalTypeLattice.Status.String
    elif isinstance(_typ, ListLyraType):
        return StatisticalTypeLattice.Status.List
    elif isinstance(_typ, DictLyraType):
        return StatisticalTypeLattice.Status.Dict
    elif isinstance(_typ, TupleLyraType):
        return StatisticalTypeLattice.Status.Tuple
    elif isinstance(_typ, SetLyraType):
        return StatisticalTypeLattice.Status.Set
    elif isinstance(_typ, NoneLyraType):
        return StatisticalTypeLattice.Status.NoneRet
    return StatisticalTypeLattice.Status.Top


class StatisticalTypeState(Store, StateWithSummarization, InputMixin):
    class Status(defaultdict):

        def __missing__(self, key):
            return {'statistical_type': resolve(key)}

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        """Map each program variable to the type representing its value.

        :param variables: set of program variables
        """
        lattices = defaultdict(lambda: StatisticalTypeLattice)
        arguments = StatisticalTypeState.Status()
        super().__init__(variables, lattices, arguments)
        InputMixin.__init__(self, precursory)
        self._subscriptions = dict() # Initialize _subscriptions as a dictionary

    @property
    def subscriptions(self):
        return self._subscriptions

    def _weak_update(self, variables: Set[VariableIdentifier], previous: 'StateWithSummarization'):
        for var in variables:
            self.store[var].join(previous.store[var])
            if var.has_length:
                self.lengths[var.length].join(previous.lengths[var.length])
                if var.is_dictionary:
                    self.keys[var.keys].join(previous.keys[var.keys])
                    self.values[var.values].join(previous.values[var.values])
        for var, subs in self.subscriptions.items():
            if var in previous.subscriptions:
                self.subscriptions[var].update(previous.subscriptions[var])
        return self

    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'StatisticalTypeState':
        pass

    def _add_series_with_dtypes(self, caller, df_info_dtypes, df_info_sorting):
        df_info_dtypes = dict(df_info_dtypes)
        df_info_sorting = dict(df_info_sorting)
        for col, dtype in df_info_dtypes.items():
            if str(dtype) in ['int64', 'float64']:
                if col in df_info_sorting:
                    if df_info_sorting[col] == "constant":
                        sub = Subscription(None, caller, Literal(StringLyraType(), col),Status.YES, Status.YES)
                        self._assign(sub, StatisticalTypeLattice.Status.NumericSeries)
                    elif df_info_sorting[col] == "increasing":
                        sub = Subscription(None, caller, Literal(StringLyraType(), col),Status.YES, Status.NO)
                        self._assign(sub, StatisticalTypeLattice.Status.NumericSeries)
                    elif df_info_sorting[col] == "decreasing":
                        sub = Subscription(None, caller, Literal(StringLyraType(), col), Status.NO, Status.YES)
                        self._assign(sub, StatisticalTypeLattice.Status.NumericSeries)
                    elif df_info_sorting[col] == "not_sorted":
                        sub = Subscription(None, caller, Literal(StringLyraType(), col), Status.NO, Status.NO)
                        self._assign(sub, StatisticalTypeLattice.Status.NumericSeries)
                else:
                    sub = Subscription(None, caller, Literal(StringLyraType(), col))
                    self._assign(sub, StatisticalTypeLattice.Status.NumericSeries)
            elif str(dtype) == 'object':
                sub = Subscription(None, caller, Literal(StringLyraType(), col))
                self._assign(sub, StatisticalTypeLattice.Status.CatSeries)
            else:
                raise ValueError(f"Unexpected dtype: {dtype}")

    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'StatisticalTypeState':
        right_copy_ = None
        if type(right) == tuple:    # Only used to gather concrete information about DataFrames when read_csv is called
            assert len(right) == 7 or len(right) == 2
            right_copy_ = deepcopy(right)    # This is necessary because we need left information before adding the Series
            right = right[0]
        # Continue with the actual assignment as usual
        evaluation = self._evaluation.visit(right, self, dict())
        typ = StatisticalTypeLattice.from_lyra_type(left.typ)
        # Deep copy are needed because meet has side effects
        if left in self.store:
            left_copy = copy.deepcopy(self.store[left])
            right_copy = copy.deepcopy(evaluation[right])
            if right_copy.meet(typ).is_bottom() and not typ.is_top():
                warnings.warn(f"Warning [possible]: inferred type is different wrt annotated type for variable {left.name}. {typ} -> {evaluation[right]} @ line {self.pp}",
                              category=InconsistentTypeWarning, stacklevel=2)
        # Assignment is destructive
        self.store[left] = evaluation[right]
        if evaluation[right].element == StatisticalTypeLattice.Status.NoneRet:
            warnings.warn(f"Warning [definite]: Assignment to None type for variable {left.name} @ line {self.pp}",
                          category=NoneRetAssignmentWarning,
                          stacklevel=2)
        if left.is_dictionary:
            _typ = StatisticalTypeLattice.from_lyra_type(left.typ.key_typ)
            typ_ = StatisticalTypeLattice.from_lyra_type(left.typ.val_typ)
            if isinstance(right.typ, DictLyraType):
                _keys = evaluation.get(KeysIdentifier(right), deepcopy(evaluation[right]))
                self.keys[left.keys] = _keys.meet(_typ)
                _values = evaluation.get(ValuesIdentifier(right), deepcopy(evaluation[right]))
                self.values[left.values] = _values.meet(typ_)
            else:
                self.keys[left.keys] = deepcopy(evaluation[right]).meet(deepcopy(typ))
                self.values[left.values] = deepcopy(evaluation[right]).meet(deepcopy(typ))
        if isinstance(right, VariableIdentifier):
            if right in self.variables and left in self.variables:
                right_tmp = None
                for v in self._variables:
                    if v == right:
                        right_tmp = v
                if right_tmp:
                    left.is_shuffled = right_tmp.is_shuffled
                    left.is_high_dimensionality = right_tmp.is_high_dimensionality
                    left.has_duplicates = right_tmp.has_duplicates
                    left.is_small = right_tmp.is_small
                    left.has_na_values = right_tmp.has_na_values
                    if left in self.variables:
                        self.variables.remove(left)
                    self.variables.add(left)
        if right_copy_:
            if len(right_copy_) == 7:
                right = right_copy_
                # It tuple has the following structure
                # {(StatisticalTypeLattice.Status.DataFrame, frozenset(dtype_info.items()), is_high_dim, has_duplicates, has_na_values, is_small, frozenset(sorting_info.items()))}
                self._add_series_with_dtypes(left, right[1], right[6])  # No return, just side effect
                # If there is at least one ordered Series, the DataFrame is not shuffled
                if any([v == "increasing" or v == "decreasing" for v in dict(right[6]).values()]):
                    left.is_shuffled = Status.NO
                if right[2] == True:
                    left.is_high_dimensionality = Status.YES
                    warnings.warn(
                        f"Warning [definite]: {left.name} is high dimensional. Feature selection/engineering or dimensionality reduction may be necessary.",
                        category=HighDimensionalityWarning, stacklevel=2)
                else:
                    left.is_high_dimensionality = Status.NO
                if right[3] == True:
                    left.has_duplicates = Status.YES
                else:
                    left.has_duplicates = Status.NO
                if right[4] == True:
                    left.is_small = Status.YES
                else:
                    left.is_small = Status.NO
                if right[5] == True:
                    left.has_na_values = Status.YES
                else:
                    left.has_na_values = Status.NO
                if left in self.variables:
                    self.variables.remove(left)
                self.variables.add(left)
            elif len(right_copy_) == 2:
                right_tmp = right_copy_[1]
                if right_tmp in self.variables:
                    left.is_shuffled = right_tmp.is_shuffled
                    left.is_high_dimensionality = right_tmp.is_high_dimensionality
                    left.has_duplicates = right_tmp.has_duplicates
                    left.is_small = right_tmp.is_small
                    left.has_na_values = right_tmp.has_na_values
                    if left in self.variables:
                        self.variables.remove(left)
                    self.variables.add(left)
                self.variables.remove(right_tmp)
        return self

    def _assign_subscription(self, left: Subscription, right: Expression) -> 'StatisticalTypeState':
        evaluation = self._evaluation.visit(right, self, dict())
        typ = StatisticalTypeLattice.from_lyra_type(left.typ)
        self.store[left] = evaluation[right].meet(typ)
        if evaluation[right].element == StatisticalTypeLattice.Status.NoneRet:
                        warnings.warn(f"Warning [definite]: Assignment to None type for variable {left.name} @ line {self.pp}",
                        NoneRetAssignmentWarning,
                        stacklevel=2)
        target = left.target
        if isinstance(target, VariableAccess):
            target = target.variable
        if target in self.variables and target in self.store and self.store[target].element == StatisticalTypeLattice.Status.DataFrame:
            if target not in self._subscriptions:
                self._subscriptions[target] = set()
            self._subscriptions[target].add(left)
        return self

    def _assign_attributeaccess(self, left: Subscription, right: Expression) -> 'StatisticalTypeState':
        evaluation = self._evaluation.visit(right, self, dict())
        typ = StatisticalTypeLattice.from_lyra_type(left.typ)
        if left.target.variable in self.store and self.store[left.target.variable].element == StatisticalTypeLattice.Status.DataFrame \
            and left.attr.name == "columns" and evaluation[right]._less_equal(StatisticalTypeLattice(StatisticalTypeLattice.Status.List)):
            for c in right.items:
                # Create subscription for each column and save them as Series in the abstract state
                sub = Subscription(TopLyraType, left.target, c)
                if sub not in self.store:
                    self.store[sub] = StatisticalTypeLattice(StatisticalTypeLattice.Status.Series)
                    if left.target not in self._subscriptions:
                        self._subscriptions[left.target] = set()
                    self.subscriptions[left.target].add(sub)
        else:
            self.store[left] = evaluation[right].meet(typ)
        if evaluation[right].element == StatisticalTypeLattice.Status.NoneRet:
            warnings.warn(f"Warning [definite]: Assignment to None type for variable {left.name} @ line {self.pp}",
                          NoneRetAssignmentWarning,
                          stacklevel=2)
        return self

    def _assign_slicing(self, left: Slicing, right: Expression) -> 'StatisticalTypeState':
        pass

    def _assign_tuple(self, left: TupleDisplay, right: Expression) -> 'StatisticalTypeState':
        if hasattr(right, "items") and len(left.items) == len(right.items):
            for l, r in zip(left.items, right.items):
                self._assign(l,r)
        elif hasattr(right, "__len__") and len(left.items) == len(right):
            for l, r in zip(left.items, right):
                self._assign(l,r)
        else:
           for l in left.items:
               self._assign(l, StatisticalTypeLattice.Status.Top)
        return self

    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'StatisticalTypeState':
        # Statistical type domain cannot assume any information in state
        return self

    def _assume_subscription(self, condition: Subscription, neg: bool = False) -> 'StatisticalTypeState':
        # Statistical type domain cannot assume any information in state
        return self

    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Statistical type domain cannot assume any information in state
        return self

    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Statistical type domain cannot assume any information in state
        return self

    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Statistical type domain cannot assume any information in state
        return self

    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Statistical type domain cannot assume any information in state
        return self

    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Statistical type domain cannot assume any information in state
        return self

    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Statistical type domain cannot assume any information in state
        return self

    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Statistical type domain cannot assume any information in state
        return self

    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Statistical type domain cannot assume any information in state
        return self

    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Statistical type domain cannot assume any information in state
        return self

    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Statistical type domain cannot assume any information in state
        return self

    def enter_if(self) -> 'StatisticalTypeState':
        return self

    def exit_if(self) -> 'StatisticalTypeState':
        return self

    def enter_loop(self) -> 'StatisticalTypeState':
        return self

    def exit_loop(self) -> 'StatisticalTypeState':
        return self

    def forget_variable(self, variable: VariableIdentifier) -> 'StatisticalTypeState':
        # Puts the variable type to top
        self.store[variable].top()
        return self

    def delete_var(self, variable: VariableIdentifier) -> 'StatisticalTypeState':
        # Deletes the variable from the store if they are present
        if variable in self.store:
            del self.store[variable]
        return self

    def _output(self, output: Expression) -> 'StatisticalTypeState':
        pass

    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'StatisticalTypeState':
        pass

    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'StatisticalTypeState':
        pass

    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'StatisticalTypeState':
        pass

    def remove_variable(self, variable: VariableIdentifier):
        try:
            self.variables.remove(variable)
            del self.store[variable]
            if variable.has_length:
                del self.lengths[variable.length]
                if variable.is_dictionary:
                    del self.keys[variable.keys]
                    del self.values[variable.values]
            if variable in self.subscriptions:
                del self.subscriptions[variable]
            return self
        except:
            print("Could not remove variable", variable)
            return self

    def get_type(self, id: Expression):
        if id in self.store:
            return self.store[id].element
        if isinstance(id, StatisticalTypeLattice.Status):
            return id
        #raise KeyError(f"{id} not tracked by abstract state")
        # If not tracked, return Top
        return StatisticalTypeLattice.Status.Top

    # expression evaluation

    class ExpressionEvaluation(BasisWithSummarization.ExpressionEvaluation):
        """Visitor that performs the evaluation of an expression in the statistical type lattice."""

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = StatisticalTypeLattice.from_lyra_type(expr.typ)
            return evaluation

        """
        Using BasisWithSummarization.ExpressionEvaluation
        per non essere forzato ad implementare i metodi che seguono
        (altrimenti estendere ExpressionVisitor)

        """

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: StatisticalTypeLattice, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            value: StatisticalTypeLattice = deepcopy(state.store[expr])
            evaluation[expr] = value.meet(StatisticalTypeLattice.from_lyra_type(expr.typ))
            if expr.is_dictionary:
                _value = deepcopy(state.keys[expr.keys])
                evaluation[expr.keys] = _value.meet(StatisticalTypeLattice.from_lyra_type(expr.typ.key_typ))
                value_ = deepcopy(state.values[expr.values])
                evaluation[expr.values] = value_.meet(StatisticalTypeLattice.from_lyra_type(expr.typ.val_typ))
            return evaluation

        """

        @copy_docstring(ExpressionVisitor.visit_LengthIdentifier)
        def visit_LengthIdentifier(self, expr: LengthIdentifier, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = deepcopy(state.lengths[expr])
            return evaluation
        """

        @copy_docstring(ExpressionVisitor.visit_ListDisplay)
        def visit_ListDisplay(self, expr: ListDisplay, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = evaluation
            value: StatisticalTypeLattice = StatisticalTypeLattice().bottom()
            if isinstance(expr, tuple):
                evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.List)
            else:
                for item in expr.items:
                    evaluated = self.visit(item, state, evaluated)
                    value = value.join(evaluated[item])
                if value.element == StatisticalTypeLattice.Status.String:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.StringList)
                elif value.element == StatisticalTypeLattice.Status.Numeric:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.NumericList)
                elif value.element == StatisticalTypeLattice.Status.Boolean:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.BoolList)
                else:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.List)
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
        def visit_TupleDisplay(self, expr: TupleDisplay, state=None, evaluation=None):
            if len(state.variables) == 1:
                evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.List)
            else:
                evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.Tuple)
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_DictDisplay)
        def visit_DictDisplay(self, expr: DictDisplay, state=None, evaluation=None):
            evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.Dict)
            return evaluation


        @copy_docstring(ExpressionVisitor.visit_SetDisplay)
        def visit_SetDisplay(self, expr: SetDisplay, state=None, evaluation=None):
            evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.Set)
            return evaluation

        """
        @copy_docstring(ExpressionVisitor.visit_AttributeReference)
        def visit_AttributeReference(self, expr: AttributeReference, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)
         """

        @copy_docstring(ExpressionVisitor.visit_Subscription)
        def visit_Subscription(self, expr: Subscription, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            target = expr
            while isinstance(target, (Subscription, Slicing)):
                target = target.target
            evaluated = self.visit(target, state, evaluation)
            if isinstance(target.typ, DictLyraType):
                evaluation[expr] = evaluated[target.values].meet(
                    StatisticalTypeLattice.from_lyra_type(target.typ.val_typ))
            elif isinstance(target.typ, DataFrameLyraType) or state.get_type(target) == StatisticalTypeLattice.Status.DataFrame:
                if isinstance(expr.key, ListDisplay):
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.DataFrame)
                else:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.Series)
            elif state.get_type(target) in StatisticalTypeLattice._series_types():
                typ = state.get_type(target)
                if typ in StatisticalTypeLattice._string_series_types():
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.String)
                elif typ in StatisticalTypeLattice._numeric_series_types():
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.Numeric)
                else:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.Scalar)
            elif state.get_type(target) in StatisticalTypeLattice._list_types():
                typ = state.get_type(target)
                if typ == StatisticalTypeLattice.Status.BoolList:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.Boolean)
                elif typ == StatisticalTypeLattice.Status.StringList:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.String)
                elif typ == StatisticalTypeLattice.Status.NumericList:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.Numeric)
                else:
                    evaluation[expr] = StatisticalTypeLattice()
            elif state.get_type(target) in StatisticalTypeLattice._array_types():
                typ = state.get_type(target)
                if typ == StatisticalTypeLattice.Status.StringArray:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.String)
                elif typ == StatisticalTypeLattice.Status.NumericArray:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.Numeric)
                else:
                    evaluation[expr] = StatisticalTypeLattice()
            else:
                try:
                    evaluation[expr] = evaluated[target].meet(StatisticalTypeLattice.from_lyra_type(target.typ.typ))
                except Exception as e:
                    print(e)
                    evaluation[expr] = StatisticalTypeLattice()
            return evaluation
        
        def visit_AttributeAccess(self, expr: AttributeAccess, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation

        @copy_docstring(ExpressionVisitor.visit_Slicing)
        def visit_Slicing(self, expr: Slicing, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            target = expr
            while isinstance(target, (Subscription, Slicing)):
                target = target.target
            evaluated = self.visit(target, state, evaluation)
            if state.get_type(
                    target) == StatisticalTypeLattice.Status.DataFrame:
                    evaluation[expr] = StatisticalTypeLattice(StatisticalTypeLattice.Status.DataFrame)
            elif state.get_type(target) in StatisticalTypeLattice._series_types():
                typ = state.get_type(target)
                evaluation[expr] = StatisticalTypeLattice(typ)
            elif state.get_type(target) in StatisticalTypeLattice._list_types():
                typ = state.get_type(target)
                evaluation[expr] = StatisticalTypeLattice(typ)
            else:
                evaluation[expr] = StatisticalTypeLattice()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = StatisticalTypeLattice.from_lyra_type(expr.typ)
            return evaluation

        """
        @copy_docstring(ExpressionVisitor.visit_Range)
        def visit_Range(self, expr: Range, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Keys)
        def visit_Keys(self, expr: Keys, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_Values)
        def visit_Values(self, expr: Values, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_CastOperation)
        def visit_CastOperation(self, expr: CastOperation, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)[expr.expression]
            evaluation[expr] = evaluated.meet(TypeLattice.from_lyra_type(expr.typ))
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_UnaryArithmeticOperation)
        def visit_UnaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated = self.visit(expr.expression, state, evaluation)
            if expr.operator == UnaryArithmeticOperation.Operator.Add:
                # same as for UnaryArithmeticOperation.Operator.Sub
                # + Boolean = Integer
                # + Integer = Integer
                # + Float = Float
                # + String = ⊥
                value: TypeLattice = deepcopy(evaluated[expr.expression]).neg()
                evaluated[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated
            elif expr.operator == UnaryArithmeticOperation.Operator.Sub:
                value: TypeLattice = deepcopy(evaluated[expr.expression]).neg()
                evaluated[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated
            raise ValueError(f"Unary operator '{expr.operator}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_UnaryBooleanOperation)
        def visit_UnaryBooleanOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryArithmeticOperation)
        def visit_BinaryArithmeticOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if expr.operator == BinaryArithmeticOperation.Operator.Add:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).add(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Sub:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).sub(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Mult:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).mult(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            elif expr.operator == BinaryArithmeticOperation.Operator.Div:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).div(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            raise ValueError(f"Binary operator '{str(expr.operator)}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinarySequenceOperation)
        def visit_BinarySequenceOperation(self, expr, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluated1 = self.visit(expr.left, state, evaluation)
            evaluated2 = self.visit(expr.right, state, evaluated1)
            if expr.operator == BinarySequenceOperation.Operator.Concat:
                value: TypeLattice = deepcopy(evaluated2[expr.left]).concat(evaluated2[expr.right])
                evaluated2[expr] = value.meet(TypeLattice.from_lyra_type(expr.typ))
                return evaluated2
            raise ValueError(f"Binary operator '{str(expr.operator)}' is unsupported!")

        @copy_docstring(ExpressionVisitor.visit_BinaryBooleanOperation)
        def visit_BinaryBooleanOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)

        @copy_docstring(ExpressionVisitor.visit_BinaryComparisonOperation)
        def visit_BinaryComparisonOperation(self, expr, state=None, evaluation=None):
            error = f"Evaluation for a {expr.__class__.__name__} expression is not yet supported!"
            raise ValueError(error)
        """

        def visit_Status(self, status: StatisticalTypeLattice.Status, state=None, evaluation=None):
            if status in evaluation:
                return evaluation  # nothing to be done
            evaluation[status] = StatisticalTypeLattice(status)
            return evaluation

    _evaluation = ExpressionEvaluation()  # static class member shared between all instances
