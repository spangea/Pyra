import numpy as np
import pandas as pd

# STATE: arrarr -> Top; arrarrarr -> Top; b -> Top; n -> Top; numarr -> Top
numarr = np.array([1, 2, 3, 4])
# STATE: arrarr -> Top; arrarrarr -> Top; b -> Top; n -> Top; numarr -> NumericArray
n = np.std(numarr)
# STATE: arrarr -> Top; arrarrarr -> Top; b -> Top; n -> Numeric; numarr -> NumericArray
n = np.std(numarr,axis=0)
# STATE: arrarr -> Top; arrarrarr -> Top; b -> Top; n -> Numeric; numarr -> NumericArray
n = np.std([1,2])
# STATE: arrarr -> Top; arrarrarr -> Top; b -> Top; n -> Numeric; numarr -> NumericArray
n = np.std(pd.Series([1,2]))
# STATE: arrarr -> Top; arrarrarr -> Top; b -> Top; n -> Numeric; numarr -> NumericArray
n = numarr.std()
# STATE: arrarr -> Top; arrarrarr -> Top; b -> Top; n -> Numeric; numarr -> NumericArray

b = np.std(numarr, dtype=bool)
# STATE: arrarr -> Top; arrarrarr -> Top; b -> Boolean; n -> Numeric; numarr -> NumericArray
b = np.std(numarr, dtype=np.bool_)
# STATE: arrarr -> Top; arrarrarr -> Top; b -> Boolean; n -> Numeric; numarr -> NumericArray

arrarr = np.array([[1, 2], [3, 4]])
# STATE: arrarr -> Array; arrarrarr -> Top; b -> Boolean; n -> Numeric; numarr -> NumericArray
n = np.std(arrarr)
# STATE: arrarr -> Array; arrarrarr -> Top; b -> Boolean; n -> Numeric; numarr -> NumericArray
numarr = np.std(arrarr, axis=0)
# STATE: arrarr -> Array; arrarrarr -> Top; b -> Boolean; n -> Numeric; numarr -> NumericArray
numarr = np.std(arrarr, axis=1)
# STATE: arrarr -> Array; arrarrarr -> Top; b -> Boolean; n -> Numeric; numarr -> NumericArray

arrarrarr = np.array([[[1, 2], [3, 4]],[[1, 2], [3, 4]]])
# STATE: arrarr -> Array; arrarrarr -> Array; b -> Boolean; n -> Numeric; numarr -> NumericArray
arrarr = np.std(arrarrarr, axis=2)
# STATE: arrarr -> Array; arrarrarr -> Array; b -> Boolean; n -> Numeric; numarr -> NumericArray

numarr = np.array([0.2,0.1])
# STATE: arrarr -> Array; arrarrarr -> Array; b -> Boolean; n -> Numeric; numarr -> NumericArray
numarr = np.std(arrarr, axis=0, out=numarr)
# FINAL: arrarr -> Array; arrarrarr -> Array; b -> Boolean; n -> Numeric; numarr -> NumericArray
