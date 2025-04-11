import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve

# STATE: prec -> Top; rec -> Top; thresh -> Top; y_scores -> Top; y_true -> Top
y_true = np.array([0, 0, 1, 1])
# STATE: prec -> Top; rec -> Top; thresh -> Top; y_scores -> Top; y_true -> NumericArray
y_scores = pd.Series([0.1, 0.4, 0.35, 0.8])
# STATE: prec -> Top; rec -> Top; thresh -> Top; y_scores -> Series; y_true -> NumericArray
prec, rec, thresh = precision_recall_curve(y_true, y_scores)
# FINAL: prec -> NumericArray; rec -> NumericArray; thresh -> NumericArray; y_scores -> Series; y_true -> NumericArray