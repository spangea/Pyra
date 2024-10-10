import numpy as np

# STATE: arr -> Top; boolarr -> Top; numarr -> Top; strarr -> Top
numarr = np.unique([1, 1, 2, 2, 3, 3])
strarr = np.unique(['1', '1', '2', '2'])
boolarr = np.unique([True, True, False])

numarr = np.unique([[1, 1], [2, 3]])
strarr = np.unique([['1', '1'], ['2', '3']])
boolarr = np.unique([[True, True], [False, False]])

arr = np.unique([[1, 0, 0], [1, 0, 0], [2, 3, 4]], axis=0)

strarr, numarr = np.unique(['a', 'b', 'b', 'c', 'a'], return_index=True)

boolarr, numarr = np.unique([True, True, False], return_index=True)

numarr, numarr = np.unique([1, 2, 6, 4, 2, 3, 2], return_inverse=True)

numarr, numarr = np.unique([1, 2, 6, 4, 2, 3, 2], return_counts=True)
# FINAL: arr -> Array; boolarr -> BoolArray; numarr -> NumericArray; strarr -> StringArray
