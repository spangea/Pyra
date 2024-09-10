import numpy as np
import pandas as pd

# STATE: n -> Top; numarr -> Top
n = np.interp(2.5, [1, 2, 3], [3, 2, 0])
# STATE: n -> Numeric; numarr -> Top
numarr = np.interp([0, 1, 1.5, 2.72, 3.14], [1, 2, 3], [3, 2, 0])
# STATE: n -> Numeric; numarr -> NumericArray
numarr = np.interp(numarr, [1, 2, 3], [3, 2, 0])
# STATE: n -> Numeric; numarr -> NumericArray
numarr = np.interp(pd.Series([0, 1, 1.5, 2.72, 3.14]), [1, 2, 3], [3, 2, 0])
# FINAL: n -> Numeric; numarr -> NumericArray
