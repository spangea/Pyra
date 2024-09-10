from sklearn.metrics import mean_squared_error
# STATE: m1 -> Top; m2 -> Top; y_pred -> Top; y_true -> Top
y_true = [[0.5, 1],[-1, 1],[7, -6]]
# STATE: m1 -> Top; m2 -> Top; y_pred -> Top; y_true -> List
y_pred = [[0, 2],[-1, 2],[8, -5]]
# STATE: m1 -> Top; m2 -> Top; y_pred -> List; y_true -> List
m1 = mean_squared_error(y_true, y_pred)
# STATE: m1 -> Numeric; m2 -> Top; y_pred -> List; y_true -> List
m2 = mean_squared_error(y_true, y_pred, multioutput='raw_values')
# FINAL: m1 -> Numeric; m2 -> NumericArray; y_pred -> List; y_true -> List
