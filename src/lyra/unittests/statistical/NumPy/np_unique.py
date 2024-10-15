import numpy as np

# STATE: arr -> Top; boolarr -> Top; numarr -> Top; numarr1 -> Top; numarr2 -> Top; numarr3 -> Top; strarr -> Top
numarr = np.unique(1)
# STATE: arr -> Top; boolarr -> Top; numarr -> NumericArray; numarr1 -> Top; numarr2 -> Top; numarr3 -> Top; strarr -> Top
strarr = np.unique('1')
# STATE: arr -> Top; boolarr -> Top; numarr -> NumericArray; numarr1 -> Top; numarr2 -> Top; numarr3 -> Top; strarr -> StringArray
boolarr = np.unique(True)
# STATE: arr -> Top; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> Top; numarr2 -> Top; numarr3 -> Top; strarr -> StringArray

numarr = np.unique([1, 1, 2, 2, 3, 3])
# STATE: arr -> Top; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> Top; numarr2 -> Top; numarr3 -> Top; strarr -> StringArray
strarr = np.unique(['1', '1', '2', '2'])
# STATE: arr -> Top; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> Top; numarr2 -> Top; numarr3 -> Top; strarr -> StringArray
boolarr = np.unique([True, True, False])
# STATE: arr -> Top; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> Top; numarr2 -> Top; numarr3 -> Top; strarr -> StringArray
arr = np.unique([True, 'uno', 1])
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> Top; numarr2 -> Top; numarr3 -> Top; strarr -> StringArray

numarr, numarr1 = np.unique([1, 2, 6, 4, 2, 3, 2], return_index=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> Top; numarr3 -> Top; strarr -> StringArray
numarr, numarr2 = np.unique([1, 2, 6, 4, 2, 3, 2], return_inverse=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> Top; strarr -> StringArray
numarr, numarr3 = np.unique([1, 2, 6, 4, 2, 3, 2], return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
numarr, numarr1, numarr2 = np.unique([1, 2, 6, 4, 2, 3, 2], return_index=True, return_inverse=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
numarr, numarr1, numarr3 = np.unique([1, 2, 6, 4, 2, 3, 2], return_index=True, return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
numarr, numarr2, numarr3 = np.unique([1, 2, 6, 4, 2, 3, 2], return_inverse=True, return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
numarr, numarr1, numarr2, numarr3 = np.unique([1, 2, 6, 4, 2, 3, 2], return_index=True, return_inverse=True, return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray

strarr, numarr1 = np.unique(['a', 'b', 'b', 'c', 'a'], return_index=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
strarr, numarr2 = np.unique(['a', 'b', 'b', 'c', 'a'], return_inverse=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
strarr, numarr3 = np.unique(['a', 'b', 'b', 'c', 'a'], return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
strarr, numarr1, numarr2 = np.unique(['a', 'b', 'b', 'c', 'a'], return_index=True, return_inverse=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
strarr, numarr1, numarr3 = np.unique(['a', 'b', 'b', 'c', 'a'], return_index=True, return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
strarr, numarr2, numarr3 = np.unique(['a', 'b', 'b', 'c', 'a'], return_inverse=True, return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
strarr, numarr1, numarr2, numarr3 = np.unique(['a', 'b', 'b', 'c', 'a'], return_index=True, return_inverse=True, return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray

boolarr, numarr1 = np.unique([True, True, False], return_index=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
boolarr, numarr2 = np.unique([True, True, False], return_inverse=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
boolarr, numarr3 = np.unique([True, True, False], return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
boolarr, numarr1, numarr2 = np.unique([True, True, False], return_index=True, return_inverse=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
boolarr, numarr1, numarr3 = np.unique([True, True, False], return_index=True, return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
boolarr, numarr2, numarr3 = np.unique([True, True, False], return_inverse=True, return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
boolarr, numarr1, numarr2, numarr3 = np.unique([True, True, False], return_index=True, return_inverse=True, return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray

arr, numarr1 = np.unique([True, 'uno', 1], return_index=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
arr, numarr2 = np.unique([True, 'uno', 1], return_inverse=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
arr, numarr3 = np.unique([True, 'uno', 1], return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
arr, numarr1, numarr2 = np.unique([True, 'uno', 1], return_index=True, return_inverse=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
arr, numarr1, numarr3 = np.unique([True, 'uno', 1], return_index=True, return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
arr, numarr2, numarr3 = np.unique([True, 'uno', 1], return_inverse=True, return_counts=True)
# STATE: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
arr, numarr1, numarr2, numarr3 = np.unique([True, 'uno', 1], return_index=True, return_inverse=True, return_counts=True)
# FINAL: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; numarr1 -> NumericArray; numarr2 -> NumericArray; numarr3 -> NumericArray; strarr -> StringArray
