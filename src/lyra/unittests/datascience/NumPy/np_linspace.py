import numpy as np
import pandas as pd

# STATE: arr -> Top; boolarr -> Top; n -> Top; numarr -> Top; strarr -> Top
numarr = np.linspace(1,10)
# STATE: arr -> Top; boolarr -> Top; n -> Top; numarr -> NumericArray; strarr -> Top
arr = np.linspace(1, [10])
# STATE: arr -> Array; boolarr -> Top; n -> Top; numarr -> NumericArray; strarr -> Top
arr = np.linspace([1],10)
# STATE: arr -> Array; boolarr -> Top; n -> Top; numarr -> NumericArray; strarr -> Top
arr = np.linspace([1],[10])
# STATE: arr -> Array; boolarr -> Top; n -> Top; numarr -> NumericArray; strarr -> Top

arr = np.linspace(1, pd.Series(10))
# STATE: arr -> Array; boolarr -> Top; n -> Top; numarr -> NumericArray; strarr -> Top

arr = np.linspace(1, numarr)
# STATE: arr -> Array; boolarr -> Top; n -> Top; numarr -> NumericArray; strarr -> Top

numarr = np.linspace(1,10, retstep=False)
# STATE: arr -> Array; boolarr -> Top; n -> Top; numarr -> NumericArray; strarr -> Top
boolarr, n = np.linspace(1,10, retstep=True, dtype=np.bool_)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> Top
strarr, n = np.linspace(1,10, retstep=True, dtype=np.string_)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr, n = np.linspace(1,10, retstep=True, dtype=np.float_)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr, n = np.linspace(1,10, retstep=True)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
arr, numarr = np.linspace([1],10, retstep=True)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray

boolarr = np.linspace(1, 10, dtype=np.bool_)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
boolarr = np.linspace(1, 10, dtype=bool)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray

strarr = np.linspace(1, 10, dtype=np.string_)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
strarr = np.linspace(1, 10, dtype=np.str_)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
strarr = np.linspace(1, 10, dtype=np.bytes_)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
strarr = np.linspace(1, 10, dtype=np.character)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
strarr = np.linspace(1, 10, dtype=np.unicode_)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
strarr = np.linspace(1, 10, dtype=str)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
strarr = np.linspace(1, 10, dtype=bytes)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
strarr = np.linspace(1, 10, dtype=memoryview)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray

numarr = np.linspace(1, 10, dtype=np.float_)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.float16)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.float32)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.float64)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.float128)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.floating)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.longfloat)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.double)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.single)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=float)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.complex_)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.complex64)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.complex128)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.complex256)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.csingle)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.cfloat)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.clongfloat)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=complex)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.int_)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.int8)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.int16)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.int32)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.int64)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.intc)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.intp)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.longlong)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.short)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=int)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.uint)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.unsignedinteger)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.ubyte)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.uint8)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.uint16)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.uint32)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.uint64)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.uintc)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.uintp)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.ulonglong)
# STATE: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray
numarr = np.linspace(1, 10, dtype=np.ushort)
# FINAL: arr -> Array; boolarr -> BoolArray; n -> Numeric; numarr -> NumericArray; strarr -> StringArray