from sklearn.metrics import f1_score
import numpy as np
# STATE: f1_scores -> Top; f2_scores -> Top; f3_scores -> Top; f4_scores -> Top; w_pred -> Top; w_true -> Top; x_pred -> Top; x_true -> Top; y_pred -> Top; y_true -> Top; z_pred -> Top; z_true -> Top
y_true = [0, 0, 0, 0, 0, 0, 0, 0, 0]
# STATE: f1_scores -> Top; f2_scores -> Top; f3_scores -> Top; f4_scores -> Top; w_pred -> Top; w_true -> Top; x_pred -> Top; x_true -> Top; y_pred -> Top; y_true -> NumericList; z_pred -> Top; z_true -> Top
y_pred = [0, 0, 0, 0, 0, 0, 0, 0, 0]
# STATE: f1_scores -> Top; f2_scores -> Top; f3_scores -> Top; f4_scores -> Top; w_pred -> Top; w_true -> Top; x_pred -> Top; x_true -> Top; y_pred -> NumericList; y_true -> NumericList; z_pred -> Top; z_true -> Top
f1_scores = f1_score(y_true, y_pred, zero_division=np.nan)
# STATE: f1_scores -> Top; f2_scores -> Top; f3_scores -> Top; f4_scores -> Top; w_pred -> Top; w_true -> Top; x_pred -> Top; x_true -> Top; y_pred -> NumericList; y_true -> NumericList; z_pred -> Top; z_true -> Top
x_true = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
# STATE: f1_scores -> Top; f2_scores -> Top; f3_scores -> Top; f4_scores -> Top; w_pred -> Top; w_true -> Top; x_pred -> Top; x_true -> List; y_pred -> NumericList; y_true -> NumericList; z_pred -> Top; z_true -> Top
x_pred = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
# STATE: f1_scores -> Top; f2_scores -> Top; f3_scores -> Top; f4_scores -> Top; w_pred -> Top; w_true -> Top; x_pred -> List; x_true -> List; y_pred -> NumericList; y_true -> NumericList; z_pred -> Top; z_true -> Top
f2_scores = f1_score(x_true, x_pred, average=None, zero_division=np.nan)
# STATE: f1_scores -> Top; f2_scores -> Array; f3_scores -> Top; f4_scores -> Top; w_pred -> Top; w_true -> Top; x_pred -> List; x_true -> List; y_pred -> NumericList; y_true -> NumericList; z_pred -> Top; z_true -> Top
z_true = [0, 1, 2, 0, 1, 2]
# STATE: f1_scores -> Top; f2_scores -> Array; f3_scores -> Top; f4_scores -> Top; w_pred -> Top; w_true -> Top; x_pred -> List; x_true -> List; y_pred -> NumericList; y_true -> NumericList; z_pred -> Top; z_true -> NumericList
z_pred = [0, 2, 1, 0, 0, 1]
# STATE: f1_scores -> Top; f2_scores -> Array; f3_scores -> Top; f4_scores -> Top; w_pred -> Top; w_true -> Top; x_pred -> List; x_true -> List; y_pred -> NumericList; y_true -> NumericList; z_pred -> NumericList; z_true -> NumericList
f3_scores = f1_score(z_true, z_pred, average=None)
# STATE: f1_scores -> Top; f2_scores -> Array; f3_scores -> NumericArray; f4_scores -> Top; w_pred -> Top; w_true -> Top; x_pred -> List; x_true -> List; y_pred -> NumericList; y_true -> NumericList; z_pred -> NumericList; z_true -> NumericList
w_true = [0, 1, 1, 0, 1, 1]
# STATE: f1_scores -> Top; f2_scores -> Array; f3_scores -> NumericArray; f4_scores -> Top; w_pred -> Top; w_true -> NumericList; x_pred -> List; x_true -> List; y_pred -> NumericList; y_true -> NumericList; z_pred -> NumericList; z_true -> NumericList
w_pred = [0, 1, 1, 0, 0, 1]
# STATE: f1_scores -> Top; f2_scores -> Array; f3_scores -> NumericArray; f4_scores -> Top; w_pred -> NumericList; w_true -> NumericList; x_pred -> List; x_true -> List; y_pred -> NumericList; y_true -> NumericList; z_pred -> NumericList; z_true -> NumericList
f4_scores = f1_score(w_true, w_pred)
# STATE: f1_scores -> Top; f2_scores -> Array; f3_scores -> NumericArray; f4_scores -> Numeric; w_pred -> NumericList; w_true -> NumericList; x_pred -> List; x_true -> List; y_pred -> NumericList; y_true -> NumericList; z_pred -> NumericList; z_true -> NumericList
