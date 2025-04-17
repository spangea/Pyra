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

from lyra.core.datascience_warnings import InconsistentTypeWarning, NoneRetAssignmentWarning, HighDimensionalityWarning

# TODO: Check correctness and update documentation and operators


class DatascienceTypeLattice(BottomMixin, ArithmeticMixin, SequenceMixin, JSONMixin):
    from enum import IntEnum

    class Status(IntEnum):
        Top = 55
        NoneType = 54

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

    def __init__(self, datascience_type: Status = Status.Top):
        super().__init__()
        self._element = datascience_type

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

    def _neg(self) -> 'DatascienceTypeLattice':
        if self.is_bottom() :
            return self._replace(self.bottom())
        elif self.element == DatascienceTypeLattice.Status.Series:
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.Series))
        elif self.element == DatascienceTypeLattice.Status.Numeric:
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.Numeric))
        elif self.element == DatascienceTypeLattice.Status.DataFrame:
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.DataFrame))
        return self._replace(self.top())

    def _add(self, other: 'DatascienceTypeLattice') -> 'DatascienceTypeLattice':
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.element == other.element:
            if (self.element == DatascienceTypeLattice.Status.Series
                    or self.element == DatascienceTypeLattice.Status.Numeric
                    or self.element == DatascienceTypeLattice.Status.String
                    or self.element == DatascienceTypeLattice.Status.DataFrame
                    or self.element == DatascienceTypeLattice.Status.Tensor):
                return self

        elif self.element == DatascienceTypeLattice.Status.Series and other.element == DatascienceTypeLattice.Status.Numeric:
            return self
        elif (self.element == DatascienceTypeLattice.Status.DataFrame and
              other.element in {DatascienceTypeLattice.Status.Numeric,
                                DatascienceTypeLattice.Status.Series,
                                DatascienceTypeLattice.Status.Dict,
                                DatascienceTypeLattice.Status.List}):
            return self
        return self._replace(self.top())

    def _sub(self, other: 'DatascienceTypeLattice') -> 'DatascienceTypeLattice':
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.element == other.element:
            if (self.element == DatascienceTypeLattice.Status.Series
                    or self.element == DatascienceTypeLattice.Status.Numeric
                    or self.element == DatascienceTypeLattice.Status.String
                    or self.element == DatascienceTypeLattice.Status.DataFrame
                    or self.element == DatascienceTypeLattice.Status.Tensor):
                return self
        return self._replace(self.top())

    def _mult(self, other: 'DatascienceTypeLattice') -> 'DatascienceTypeLattice':
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.element == other.element and other.element == DatascienceTypeLattice.Status.Series:
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.Series))
        elif self.element == other.element and other.element == DatascienceTypeLattice.Status.Numeric:
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.Numeric))
        elif self.element == other.element and other.element == DatascienceTypeLattice.Status.DataFrame:
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.DataFrame))
        elif {self.element, other.element} == {DatascienceTypeLattice.Status.DataFrame,
                                               DatascienceTypeLattice.Status.Numeric
                                               }:
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.DataFrame))
        return self._replace(self.top())

    def _div(self, other: 'DatascienceTypeLattice') -> 'DatascienceTypeLattice':
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.element == other.element:
            if self.element == DatascienceTypeLattice.Status.Series:
                return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.RatioSeries))
            elif (self.element == DatascienceTypeLattice.Status.Numeric
                    or self.element == DatascienceTypeLattice.Status.DataFrame
                    or self.element == DatascienceTypeLattice.Status.Tensor):
                return self
        return self._replace(self.top())

    def _mod(self, other: 'DatascienceTypeLattice') -> 'DatascienceTypeLattice':
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.element == other.element:
            if (self.element == DatascienceTypeLattice.Status.Series
                    or self.element == DatascienceTypeLattice.Status.Numeric
                    or self.element == DatascienceTypeLattice.Status.DataFrame):
                return self
        return self._replace(self.top())

    def _concat(self, other: 'DatascienceTypeLattice') -> 'DatascienceTypeLattice':
        return self._replace(self.top())

    def to_json(self) -> str:
        return str(self)

    @staticmethod
    def from_json(json: str) -> 'JSONMixin':
        if json == '⊥':
            return DatascienceTypeLattice().bottom()
        if json == 'Boolean':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Boolean)
        elif json == 'Numeric':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Numeric)
        elif json == 'String':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.String)
        elif json == 'RatioSeries':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.RatioSeries)
        elif json == 'DataFrame':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.DataFrame)
        elif json == 'DataFrameFromPCA':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.DataFrameFromPCA)
        elif json == 'Series':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Series)
        elif json == 'StringSeries':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.StringSeries)
        elif json == 'NumericSeries':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.NumericSeries)
        elif json == 'ExpSeries':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.ExpSeries)
        elif json == 'StdSeries':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.StdSeries)
        elif json == 'NormSeries':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.NormSeries)
        elif json == 'CatSeries':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.CatSeries)
        elif json == 'Array':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Array)
        elif json == 'BoolArray':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.BoolArray)
        elif json == 'StringArray':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.StringArray)
        elif json == 'NumericArray':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.NumericArray)
        elif json == 'List':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.List)
        elif json == 'BoolList':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.BoolList)
        elif json == 'StringList':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.StringList)
        elif json == 'NumericList':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.NumericList)
        elif json == 'Tuple':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Tuple)
        elif json == 'Dict':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Dict)
        elif json == 'Set':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Set)
        elif json == 'MaxAbsScaler':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.MaxAbsScaler)
        elif json == 'MinMaxScaler':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.MinMaxScaler)
        elif json == 'StandardScaler':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.StandardScaler)
        elif json == 'KBinsDiscretizer':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.KBinsDiscretizer)
        elif json == 'MultiLabelBinarizer':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.MultiLabelBinarizer)
        elif json == 'TargetEncoder':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.TargetEncoder)
        elif json == 'OrdinalEncoder':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.OrdinalEncoder)
        elif json == 'Binarizer':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Binarizer)
        elif json == 'OneHotEncoder':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.OneHotEncoder)
        elif json == 'LabelEncoder':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.LabelEncoder)
        elif json == 'FunctionTransformer':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.FunctionTransformer)
        elif json == 'KernelCenterer':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.KernelCenterer)
        elif json == 'Normalizer':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Normalizer)
        elif json == 'PolynomialFeatures':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.PolynomialFeatures)
        elif json == 'PowerTransformer':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.PowerTransformer)
        elif json == 'QuantileTransformer':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.QuantileTransformer)
        elif json == 'RobustScaler':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.RobustScaler)
        elif json == 'SplineTransformer':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.SplineTransformer)
        elif json == 'Scaled':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Scaled)
        elif json == 'Tensor':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Tensor)
        elif json == 'SplittedTestData':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.SplittedTestData)
        elif json == 'SplittedTrainData':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.SplittedTrainData)
        elif json == ('FeatureSelector'):
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.FeatureSelector)
        elif json == 'FeatureSelected':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.FeatureSelected)
        elif json == 'Top':
            return DatascienceTypeLattice(DatascienceTypeLattice.Status.Top)
        return DatascienceTypeLattice()

    def top(self):
        return self._replace(DatascienceTypeLattice())

    def is_top(self) -> bool:
        return self.element == DatascienceTypeLattice.Status.Top

    def _less_equal(self, other: 'DatascienceTypeLattice') -> bool:
        if other.is_top():
            return True
        elif self.element == other.element:
            return True
        elif self.is_bottom():
            return True
        elif (self.element in self._numeric_series_types()
              and other.element in {DatascienceTypeLattice.Status.NumericSeries, DatascienceTypeLattice.Status.Series}):
            return True
        elif (self.element in self._string_series_types()
              and other.element in {DatascienceTypeLattice.Status.StringSeries, DatascienceTypeLattice.Status.Series}):
            return True
        elif self.element in self._array_types() and other.element == DatascienceTypeLattice.Status.Array:
            return True
        elif self.element in self._list_types() and other.element == DatascienceTypeLattice.Status.List:
            return True
        elif self.element in self._scalar_types() and other.element == DatascienceTypeLattice.Status.Scalar:
            return True
        elif self.element == DatascienceTypeLattice.Status.DataFrameFromPCA and other.element == DatascienceTypeLattice.Status.DataFrame:
            return True
        elif (self.element in {DatascienceTypeLattice.Status.NumericSeries, DatascienceTypeLattice.Status.StringSeries,
                               DatascienceTypeLattice.Status.BoolSeries}
              and other.element == DatascienceTypeLattice.Status.Series):
            return True
        return False

    @classmethod
    def get_all_types(cls):
        return {cls(t) for t in DatascienceTypeLattice.Status}

    @classmethod
    def _dataframes_types(cls):
        s = (DatascienceTypeLattice.Status.DataFrame,
             DatascienceTypeLattice.Status.DataFrameFromPCA)
        return s

    @classmethod
    def _list_types(cls):
        s = (DatascienceTypeLattice.Status.List,
             DatascienceTypeLattice.Status.BoolList,
             DatascienceTypeLattice.Status.NumericList,
             DatascienceTypeLattice.Status.StringList)
        return s

    @classmethod
    def _scalar_types(cls):
        s = (DatascienceTypeLattice.Status.Boolean,
             DatascienceTypeLattice.Status.Numeric,
             DatascienceTypeLattice.Status.Scalar,
             DatascienceTypeLattice.Status.String)
        return s

    @classmethod
    def _array_types(cls):
        s = (DatascienceTypeLattice.Status.Array,
             DatascienceTypeLattice.Status.BoolArray,
             DatascienceTypeLattice.Status.NumericArray,
             DatascienceTypeLattice.Status.StringArray)
        return s

    @classmethod
    def _series_types(cls):
        s = (DatascienceTypeLattice.Status.Series,
             DatascienceTypeLattice.Status.NumericSeries,
             DatascienceTypeLattice.Status.RatioSeries,
             DatascienceTypeLattice.Status.ExpSeries,
             DatascienceTypeLattice.Status.StdSeries,
             DatascienceTypeLattice.Status.NormSeries,
             DatascienceTypeLattice.Status.StringSeries,
             DatascienceTypeLattice.Status.CatSeries
             )
        return s
    @classmethod
    def _numeric_series_types(cls):
        s = (DatascienceTypeLattice.Status.NumericSeries,
             DatascienceTypeLattice.Status.RatioSeries,
             DatascienceTypeLattice.Status.ExpSeries,
             DatascienceTypeLattice.Status.StdSeries,
             DatascienceTypeLattice.Status.NormSeries)
        return s

    @classmethod
    def _string_series_types(cls):
        s = (DatascienceTypeLattice.Status.StringSeries,
             DatascienceTypeLattice.Status.CatSeries)
        return s

    @classmethod
    def _is_series_type(cls, status):
        return (
                status in cls._string_series_types() or
                status in cls._numeric_series_types() or
                status == DatascienceTypeLattice.Status.BoolSeries
        )

    @classmethod
    def _is_dataframe_type(cls, status):
        return status in cls._dataframes_types()

    @classmethod
    def _atom_types(cls):
        s = (DatascienceTypeLattice.Status.NoneType,
             DatascienceTypeLattice.Status.NoneRet,
             DatascienceTypeLattice.Status.Plot,
             DatascienceTypeLattice.Status.Binarizer,
             DatascienceTypeLattice.Status.LabelBinarizer,
             DatascienceTypeLattice.Status.OrdinalEncoder,
             DatascienceTypeLattice.Status.OneHotEncoder,
             DatascienceTypeLattice.Status.LabelEncoder,
             DatascienceTypeLattice.Status.KBinsDiscretizer,
             DatascienceTypeLattice.Status.MultiLabelBinarizer,
             DatascienceTypeLattice.Status.TargetEncoder,
             DatascienceTypeLattice.Status.MaxAbsScaler,
             DatascienceTypeLattice.Status.MinMaxScaler,
             DatascienceTypeLattice.Status.StandardScaler,
             DatascienceTypeLattice.Status.FunctionTransformer,
             DatascienceTypeLattice.Status.KernelCenterer,
             DatascienceTypeLattice.Status.Normalizer,
             DatascienceTypeLattice.Status.PolynomialFeatures,
             DatascienceTypeLattice.Status.PowerTransformer,
             DatascienceTypeLattice.Status.QuantileTransformer,
             DatascienceTypeLattice.Status.RobustScaler,
             DatascienceTypeLattice.Status.SplineTransformer,
             DatascienceTypeLattice.Status.Scaled,
             DatascienceTypeLattice.Status.Tuple,
             DatascienceTypeLattice.Status.Set,
             DatascienceTypeLattice.Status.Dict,
             DatascienceTypeLattice.Status.Tensor,
             DatascienceTypeLattice.Status.SplittedTrainData,
             DatascienceTypeLattice.Status.SplittedTestData,
             DatascienceTypeLattice.Status.FeatureSelector,
             DatascienceTypeLattice.Status.FeatureSelected
             )
        return s

    def _join(self, other: 'DatascienceTypeLattice') -> 'DatascienceTypeLattice':
        if self.is_top() or other.is_top():
            return self._replace(self.top())
        elif self.is_bottom() and other.is_bottom():
            return self
        elif self.is_bottom():
            return self._replace(DatascienceTypeLattice(other.element))
        elif other.is_bottom():
            return self
        elif self.element == other.element:
            return self
        elif self._less_equal(other):
            return self._replace(DatascienceTypeLattice(other.element))
        elif other._less_equal(self):
            return self
        # Computes the join between types of the same group
        # Numeric series
        elif self.element in self._numeric_series_types() and other.element in self._numeric_series_types():
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.NumericSeries))
        # String series
        elif self.element in self._string_series_types() and other.element in self._string_series_types():
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.StringSeries))
        # Array
        elif self.element in self._array_types() and other.element in self._array_types():
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.Array))
        # List
        elif self.element in self._list_types() and other.element in self._list_types():
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.List))
        # Scalar values
        elif self.element in self._scalar_types() and other.element in self._scalar_types():
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.Scalar))
        # DataFrame
        elif self.element in self._dataframes_types() and other.element in self._dataframes_types():
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.DataFrame))
        # Computes the join between types of different series groups
        elif self._is_series_type(self.element) and self._is_series_type(other.element):
            return self._replace(DatascienceTypeLattice(DatascienceTypeLattice.Status.Series))
        return self._replace(self.top())

    def _meet(self, other: 'DatascienceTypeLattice'):
        if self.is_bottom() or other.is_bottom():
            return self._replace(self.bottom())
        elif self.is_top():
            return self._replace(DatascienceTypeLattice(other.element))
        elif other.is_top():
            return self
        elif self.element == other.element:
            return self
        elif self._less_equal(other):
            return self
        elif other._less_equal(self):
            return self._replace(DatascienceTypeLattice(other.element))
        return self._replace(self.bottom())

    def _widening(self, other: 'DatascienceTypeLattice'):
        return self._join(other)


def resolve(typ: LyraType) -> DatascienceTypeLattice.Status:
    _typ = typ
    # FIXME: this part is useless for our domain
    """
    while isinstance(_typ, (ListLyraType, TupleLyraType, SetLyraType, DictLyraType)):
        if isinstance(_typ, (ListLyraType, SetLyraType)):
            _typ = _typ.typ
        elif isinstance(_typ, TupleLyraType):
            _typ = reduce(max, map(resolve, _typ.typs), DatascienceTypeLattice.Status.Boolean)
        elif isinstance(_typ, DictLyraType):
            _typ = max(resolve(_typ.key_typ), resolve(_typ.val_typ))
    """
    if isinstance(_typ, DatascienceTypeLattice.Status):
        return _typ
    elif isinstance(_typ, BooleanLyraType):
        return DatascienceTypeLattice.Status.Boolean
    elif isinstance(_typ, IntegerLyraType) or isinstance(_typ, FloatLyraType):
        return DatascienceTypeLattice.Status.Numeric
    elif isinstance(_typ, DataFrameLyraType):
        return DatascienceTypeLattice.Status.DataFrame
    elif isinstance(_typ, SeriesLyraType):
        return DatascienceTypeLattice.Status.Series
    elif isinstance(_typ, StringLyraType):
        return DatascienceTypeLattice.Status.String
    elif isinstance(_typ, ListLyraType):
        return DatascienceTypeLattice.Status.List
    elif isinstance(_typ, DictLyraType):
        return DatascienceTypeLattice.Status.Dict
    elif isinstance(_typ, TupleLyraType):
        return DatascienceTypeLattice.Status.Tuple
    elif isinstance(_typ, SetLyraType):
        return DatascienceTypeLattice.Status.Set
    elif isinstance(_typ, NoneLyraType):
        return DatascienceTypeLattice.Status.NoneType
    return DatascienceTypeLattice.Status.Top


class DatascienceTypeState(Store, StateWithSummarization, InputMixin):
    class Status(defaultdict):

        def __missing__(self, key):
            return {'datascience_type': resolve(key)}

    def __init__(self, variables: Set[VariableIdentifier], precursory: State = None):
        """Map each program variable to the type representing its value.

        :param variables: set of program variables
        """
        lattices = defaultdict(lambda: DatascienceTypeLattice)
        arguments = DatascienceTypeState.Status()
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

    def replace(self, variable: VariableIdentifier, expression: Expression) -> 'DatascienceTypeState':
        pass

    def _add_series_with_dtypes(self, caller, df_info_dtypes, df_info_sorting):
        df_info_dtypes = dict(df_info_dtypes)
        df_info_sorting = dict(df_info_sorting)
        for col, dtype in df_info_dtypes.items():
            if str(dtype) in ['int64', 'float64']:
                if col in df_info_sorting:
                    if df_info_sorting[col] == "constant":
                        sub = Subscription(TopLyraType, caller, Literal(StringLyraType(), col),Status.YES, Status.YES)
                        self._assign(sub, DatascienceTypeLattice.Status.NumericSeries)
                    elif df_info_sorting[col] == "increasing":
                        sub = Subscription(TopLyraType, caller, Literal(StringLyraType(), col),Status.YES, Status.NO)
                        self._assign(sub, DatascienceTypeLattice.Status.NumericSeries)
                    elif df_info_sorting[col] == "decreasing":
                        sub = Subscription(TopLyraType, caller, Literal(StringLyraType(), col), Status.NO, Status.YES)
                        self._assign(sub, DatascienceTypeLattice.Status.NumericSeries)
                    elif df_info_sorting[col] == "not_sorted":
                        sub = Subscription(TopLyraType, caller, Literal(StringLyraType(), col), Status.NO, Status.NO)
                        self._assign(sub, DatascienceTypeLattice.Status.NumericSeries)
                else:
                    sub = Subscription(TopLyraType, caller, Literal(StringLyraType(), col))
                    self._assign(sub, DatascienceTypeLattice.Status.NumericSeries)
            elif str(dtype) == 'object':
                sub = Subscription(TopLyraType, caller, Literal(StringLyraType(), col))
                self._assign(sub, DatascienceTypeLattice.Status.CatSeries)
            else:
                raise ValueError(f"Unexpected dtype: {dtype}")

    def _assign_variable(self, left: VariableIdentifier, right: Expression) -> 'DatascienceTypeState':
        right_copy_ = None
        if type(right) == tuple:    # Only used to gather concrete information about DataFrames when read_csv is called
            assert len(right) == 7 or len(right) == 2
            right_copy_ = deepcopy(right)    # This is necessary because we need left information before adding the Series
            right = right[0]
        # Continue with the actual assignment as usual
        evaluation = self._evaluation.visit(right, self, dict())
        typ = DatascienceTypeLattice.from_lyra_type(left.typ)
        # Deep copy are needed because meet has side effects
        if left in self.store:
            left_copy = copy.deepcopy(self.store[left])
            right_copy = copy.deepcopy(evaluation[right])
            if right_copy.meet(typ).is_bottom() and not typ.is_top():
                warnings.warn(f"Warning [potential]: inferred type is different wrt annotated type for variable {left.name}. {typ} -> {evaluation[right]} @ line {self.pp}",
                              category=InconsistentTypeWarning, stacklevel=2)
        # Assignment is destructive
        self.store[left] = evaluation[right]
        if evaluation[right].element == DatascienceTypeLattice.Status.NoneRet:
            warnings.warn(f"Warning [plausible]: Assignment to None type for variable {left.name} @ line {self.pp}",
                          category=NoneRetAssignmentWarning,
                          stacklevel=2)
        if left.is_dictionary:
            _typ = DatascienceTypeLattice.from_lyra_type(left.typ.key_typ)
            typ_ = DatascienceTypeLattice.from_lyra_type(left.typ.val_typ)
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
                # {(DatascienceTypeLattice.Status.DataFrame, frozenset(dtype_info.items()), is_high_dim, has_duplicates, has_na_values, is_small, frozenset(sorting_info.items()))}
                self._add_series_with_dtypes(left, right[1], right[6])  # No return, just side effect
                # If there is at least one ordered Series, the DataFrame is not shuffled
                if any([v == "increasing" or v == "decreasing" for v in dict(right[6]).values()]):
                    left.is_shuffled = Status.NO
                else:
                    left.is_shuffled = Status.YES
                if right[2] == True:
                    left.is_high_dimensionality = Status.YES
                    warnings.warn(
                        f"Warning [plausible]: {left.name} is high dimensional. Feature selection/engineering or dimensionality reduction may be necessary.",
                        category=HighDimensionalityWarning, stacklevel=2)
                else:
                    left.is_high_dimensionality = Status.NO
                if right[3] == True:
                    left.has_duplicates = Status.YES
                else:
                    left.has_duplicates = Status.NO
                if right[4] == True:
                    left.has_na_values = Status.YES
                else:
                    left.has_na_values = Status.NO
                if right[5] == True:
                    left.is_small = Status.YES
                else:
                    left.is_small = Status.NO
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

    def _assign_subscription(self, left: Subscription, right: Expression) -> 'DatascienceTypeState':
        evaluation = self._evaluation.visit(right, self, dict())
        typ = DatascienceTypeLattice.from_lyra_type(left.typ)
        self.store[left] = evaluation[right].meet(typ)
        if evaluation[right].element == DatascienceTypeLattice.Status.NoneRet:
                        warnings.warn(f"Warning [plausible]: Assignment to None type for variable {left.name} @ line {self.pp}",
                        NoneRetAssignmentWarning,
                        stacklevel=2)
        target = left.target
        if isinstance(target, VariableAccess):
            target = target.variable
        if target in self.variables and target in self.store and self.store[target].element == DatascienceTypeLattice.Status.DataFrame:
            if target not in self._subscriptions:
                self._subscriptions[target] = set()
            self._subscriptions[target].add(left)
        return self

    def _assign_attributeaccess(self, left: Subscription, right: Expression) -> 'DatascienceTypeState':
        evaluation = self._evaluation.visit(right, self, dict())
        typ = DatascienceTypeLattice.from_lyra_type(left.typ)
        if left.target.variable in self.store and self.store[left.target.variable].element == DatascienceTypeLattice.Status.DataFrame \
            and left.attr.name == "columns" and evaluation[right]._less_equal(DatascienceTypeLattice(DatascienceTypeLattice.Status.List)):
            for c in right.items:
                # Create subscription for each column and save them as Series in the abstract state
                sub = Subscription(TopLyraType, left.target, c)
                if sub not in self.store:
                    self.store[sub] = DatascienceTypeLattice(DatascienceTypeLattice.Status.Series)
                    if left.target not in self._subscriptions:
                        self._subscriptions[left.target] = set()
                    self.subscriptions[left.target].add(sub)
        else:
            self.store[left] = evaluation[right].meet(typ)
        if evaluation[right].element == DatascienceTypeLattice.Status.NoneRet:
            warnings.warn(f"Warning [plausible]: Assignment to None type for variable {left.name} @ line {self.pp}",
                          NoneRetAssignmentWarning,
                          stacklevel=2)
        return self

    def _assign_slicing(self, left: Slicing, right: Expression) -> 'DatascienceTypeState':
        pass

    def _assign_tuple(self, left: TupleDisplay, right: Expression) -> 'DatascienceTypeState':
        if hasattr(right, "items") and len(left.items) == len(right.items):
            for l, r in zip(left.items, right.items):
                self._assign(l,r)
        elif hasattr(right, "__len__") and len(left.items) == len(right):
            for l, r in zip(left.items, right):
                self._assign(l,r)
        else:
           for l in left.items:
               self._assign(l, DatascienceTypeLattice.Status.Top)
        return self

    def _assume_variable(self, condition: VariableIdentifier, neg: bool = False) -> 'DatascienceTypeState':
        # Datascience type domain cannot assume any information in state
        return self

    def _assume_subscription(self, condition: Subscription, neg: bool = False) -> 'DatascienceTypeState':
        # Datascience type domain cannot assume any information in state
        return self

    def _assume_eq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Datascience type domain cannot assume any information in state
        return self

    def _assume_noteq_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Datascience type domain cannot assume any information in state
        return self

    def _assume_lt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Datascience type domain cannot assume any information in state
        return self

    def _assume_lte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Datascience type domain cannot assume any information in state
        return self

    def _assume_gt_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Datascience type domain cannot assume any information in state
        return self

    def _assume_gte_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Datascience type domain cannot assume any information in state
        return self

    def _assume_is_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Datascience type domain cannot assume any information in state
        return self

    def _assume_isnot_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Datascience type domain cannot assume any information in state
        return self

    def _assume_in_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Datascience type domain cannot assume any information in state
        return self

    def _assume_notin_comparison(self, condition: BinaryComparisonOperation, bwd: bool = False):
        # Datascience type domain cannot assume any information in state
        return self

    def enter_if(self) -> 'DatascienceTypeState':
        return self

    def exit_if(self) -> 'DatascienceTypeState':
        return self

    def enter_loop(self) -> 'DatascienceTypeState':
        return self

    def exit_loop(self) -> 'DatascienceTypeState':
        return self

    def forget_variable(self, variable: VariableIdentifier) -> 'DatascienceTypeState':
        # Puts the variable type to top
        self.store[variable].top()
        return self

    def delete_var(self, variable: VariableIdentifier) -> 'DatascienceTypeState':
        # Deletes the variable from the store if they are present
        if variable in self.store:
            del self.store[variable]
        return self

    def _output(self, output: Expression) -> 'DatascienceTypeState':
        pass

    def _substitute_variable(self, left: VariableIdentifier, right: Expression) -> 'DatascienceTypeState':
        pass

    def _substitute_subscription(self, left: Subscription, right: Expression) -> 'DatascienceTypeState':
        pass

    def _substitute_slicing(self, left: Slicing, right: Expression) -> 'DatascienceTypeState':
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
        if isinstance(id, DatascienceTypeLattice.Status):
            return id
        #raise KeyError(f"{id} not tracked by abstract state")
        # If not tracked, return Top
        return DatascienceTypeLattice.Status.Top

    # expression evaluation

    class ExpressionEvaluation(BasisWithSummarization.ExpressionEvaluation):
        """Visitor that performs the evaluation of an expression in the datascience type lattice."""

        @copy_docstring(ExpressionVisitor.visit_Literal)
        def visit_Literal(self, expr: Literal, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = DatascienceTypeLattice.from_lyra_type(expr.typ)
            return evaluation

        """
        Using BasisWithSummarization.ExpressionEvaluation
        per non essere forzato ad implementare i metodi che seguono
        (altrimenti estendere ExpressionVisitor)

        """

        @copy_docstring(ExpressionVisitor.visit_VariableIdentifier)
        def visit_VariableIdentifier(self, expr: DatascienceTypeLattice, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            value: DatascienceTypeLattice = deepcopy(state.store[expr])
            evaluation[expr] = value.meet(DatascienceTypeLattice.from_lyra_type(expr.typ))
            if expr.is_dictionary:
                _value = deepcopy(state.keys[expr.keys])
                evaluation[expr.keys] = _value.meet(DatascienceTypeLattice.from_lyra_type(expr.typ.key_typ))
                value_ = deepcopy(state.values[expr.values])
                evaluation[expr.values] = value_.meet(DatascienceTypeLattice.from_lyra_type(expr.typ.val_typ))
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
            value: DatascienceTypeLattice = DatascienceTypeLattice().bottom()
            if isinstance(expr, tuple):
                evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.List)
            else:
                for item in expr.items:
                    evaluated = self.visit(item, state, evaluated)
                    value = value.join(evaluated[item])
                if value.element == DatascienceTypeLattice.Status.String:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.StringList)
                elif value.element == DatascienceTypeLattice.Status.Numeric:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.NumericList)
                elif value.element == DatascienceTypeLattice.Status.Boolean:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.BoolList)
                else:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.List)
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_TupleDisplay)
        def visit_TupleDisplay(self, expr: TupleDisplay, state=None, evaluation=None):
            if len(state.variables) == 1:
                evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.List)
            else:
                evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.Tuple)
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_DictDisplay)
        def visit_DictDisplay(self, expr: DictDisplay, state=None, evaluation=None):
            evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.Dict)
            return evaluation


        @copy_docstring(ExpressionVisitor.visit_SetDisplay)
        def visit_SetDisplay(self, expr: SetDisplay, state=None, evaluation=None):
            evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.Set)
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
                    DatascienceTypeLattice.from_lyra_type(target.typ.val_typ))
            elif isinstance(target.typ, DataFrameLyraType) or state.get_type(target) == DatascienceTypeLattice.Status.DataFrame:
                if isinstance(expr.key, ListDisplay):
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.DataFrame)
                else:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.Series)
            elif state.get_type(target) in DatascienceTypeLattice._series_types():
                typ = state.get_type(target)
                if typ in DatascienceTypeLattice._string_series_types():
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.String)
                elif typ in DatascienceTypeLattice._numeric_series_types():
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.Numeric)
                else:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.Scalar)
            elif state.get_type(target) in DatascienceTypeLattice._list_types():
                typ = state.get_type(target)
                if typ == DatascienceTypeLattice.Status.BoolList:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.Boolean)
                elif typ == DatascienceTypeLattice.Status.StringList:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.String)
                elif typ == DatascienceTypeLattice.Status.NumericList:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.Numeric)
                else:
                    evaluation[expr] = DatascienceTypeLattice()
            elif state.get_type(target) in DatascienceTypeLattice._array_types():
                typ = state.get_type(target)
                if typ == DatascienceTypeLattice.Status.StringArray:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.String)
                elif typ == DatascienceTypeLattice.Status.NumericArray:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.Numeric)
                else:
                    evaluation[expr] = DatascienceTypeLattice()
            else:
                try:
                    evaluation[expr] = evaluated[target].meet(DatascienceTypeLattice.from_lyra_type(target.typ.typ))
                except Exception as e:
                    print(e)
                    evaluation[expr] = DatascienceTypeLattice()
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
                    target) == DatascienceTypeLattice.Status.DataFrame:
                    evaluation[expr] = DatascienceTypeLattice(DatascienceTypeLattice.Status.DataFrame)
            elif state.get_type(target) in DatascienceTypeLattice._series_types():
                typ = state.get_type(target)
                evaluation[expr] = DatascienceTypeLattice(typ)
            elif state.get_type(target) in DatascienceTypeLattice._list_types():
                typ = state.get_type(target)
                evaluation[expr] = DatascienceTypeLattice(typ)
            else:
                evaluation[expr] = DatascienceTypeLattice()
            return evaluation

        @copy_docstring(ExpressionVisitor.visit_Input)
        def visit_Input(self, expr: Input, state=None, evaluation=None):
            if expr in evaluation:
                return evaluation  # nothing to be done
            evaluation[expr] = DatascienceTypeLattice.from_lyra_type(expr.typ)
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

        def visit_Status(self, status: DatascienceTypeLattice.Status, state=None, evaluation=None):
            if status in evaluation:
                return evaluation  # nothing to be done
            evaluation[status] = DatascienceTypeLattice(status)
            return evaluation

    _evaluation = ExpressionEvaluation()  # static class member shared between all instances
