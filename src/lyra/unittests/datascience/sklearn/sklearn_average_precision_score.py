import numpy as np
from sklearn.metrics import average_precision_score

# STATE: average_precision -> Top; y_scores -> Top; y_true -> Top
y_true = np.array([0, 0, 1, 1])
# STATE: average_precision -> Top; y_scores -> Top; y_true -> NumericArray
y_scores = np.array([0.1, 0.4, 0.35, 0.8])
# STATE: average_precision -> Top; y_scores -> NumericArray; y_true -> NumericArray
average_precision = average_precision_score(y_true, y_scores)
# FINAL: average_precision -> Numeric; y_scores -> NumericArray; y_true -> NumericArray