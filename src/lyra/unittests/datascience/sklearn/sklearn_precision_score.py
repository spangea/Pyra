import numpy as np
from sklearn.metrics import precision_score

# STATE: arr -> Top; n -> Top; numarr -> Top; top -> Top; y_pred -> Top; y_true -> Top
y_true = np.array([0, 0, 1, 1])
# STATE: arr -> Top; n -> Top; numarr -> Top; top -> Top; y_pred -> Top; y_true -> NumericArray
y_pred = np.array([0, 0, 1, 0])
# STATE: arr -> Top; n -> Top; numarr -> Top; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
n = precision_score(y_true, y_pred)
# STATE: arr -> Top; n -> Numeric; numarr -> Top; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
n = precision_score(y_true, y_pred, average='binary')
# STATE: arr -> Top; n -> Numeric; numarr -> Top; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
y_true = np.array([0, 1, 2, 0])
# STATE: arr -> Top; n -> Numeric; numarr -> Top; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
y_pred = np.array([0, 2, 1, 0])
# STATE: arr -> Top; n -> Numeric; numarr -> Top; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
n = precision_score(y_true, y_pred, average='micro')
# STATE: arr -> Top; n -> Numeric; numarr -> Top; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
n = precision_score(y_true, y_pred, average='macro')
# STATE: arr -> Top; n -> Numeric; numarr -> Top; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
n = precision_score(y_true, y_pred, average='weighted')
# STATE: arr -> Top; n -> Numeric; numarr -> Top; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
y_pred = np.array([0, 0, 0, 0])
# STATE: arr -> Top; n -> Numeric; numarr -> Top; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
numarr = precision_score(y_true, y_pred, average=None, labels=[2], zero_division=1)
# STATE: arr -> Top; n -> Numeric; numarr -> NumericArray; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
numarr = precision_score(y_true, y_pred, average=None, zero_division=1)
# STATE: arr -> Top; n -> Numeric; numarr -> NumericArray; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
arr = precision_score(y_true, y_pred, average=None, zero_division=np.nan)
# STATE: arr -> Array; n -> Numeric; numarr -> NumericArray; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
arr = precision_score(y_true, y_pred, average=None, zero_division=np.NaN)
# STATE: arr -> Array; n -> Numeric; numarr -> NumericArray; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
arr = precision_score(y_true, y_pred, average=None, zero_division=np.NAN)
# STATE: arr -> Array; n -> Numeric; numarr -> NumericArray; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
y_true = np.array([0, 0, 0, 0])
# STATE: arr -> Array; n -> Numeric; numarr -> NumericArray; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
top = precision_score(y_true, y_pred, pos_label=1, zero_division=np.nan)
# STATE: arr -> Array; n -> Numeric; numarr -> NumericArray; top -> Top; y_pred -> NumericArray; y_true -> NumericArray
y_true = np.array([[0, 0, 0], [1, 1, 1], [0, 1, 1]])
# STATE: arr -> Array; n -> Numeric; numarr -> NumericArray; top -> Top; y_pred -> NumericArray; y_true -> Array
y_pred = np.array([[0, 0, 0], [1, 1, 1], [1, 1, 0]])
# STATE: arr -> Array; n -> Numeric; numarr -> NumericArray; top -> Top; y_pred -> Array; y_true -> Array
n = precision_score(y_true, y_pred, average='samples', sample_weight=[6,6,3], zero_division=1)
# STATE: arr -> Array; n -> Numeric; numarr -> NumericArray; top -> Top; y_pred -> Array; y_true -> Array
numarr = precision_score(y_true, y_pred, average=None)
# FINAL: arr -> Array; n -> Numeric; numarr -> NumericArray; top -> Top; y_pred -> Array; y_true -> Array
