import numpy as np
# STATE: firstArray -> Top; secondArray -> Top; thirdArray -> Top
firstArray = np.array([1, 2, 3, 4, 5, 6])
# STATE: firstArray -> NumericArray; secondArray -> Top; thirdArray -> Top
secondArray = np.array("string")
# STATE: firstArray -> NumericArray; secondArray -> StringArray; thirdArray -> Top
thirdArray = np.array([1, 2, "Hello"])
# FINAL: firstArray -> NumericArray; secondArray -> StringArray; thirdArray -> Array

