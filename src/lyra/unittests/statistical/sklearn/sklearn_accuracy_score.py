from sklearn.metrics import accuracy_score

# STATE: accuracy_score -> Top; y_pred -> Top; y_true -> Top
y_pred = [0, 2, 1, 3]
# STATE: accuracy_score -> Top; y_pred -> NumericList; y_true -> Top
y_true = [0, 1, 2, 3]
# STATE: accuracy_score -> Top; y_pred -> NumericList; y_true -> NumericList
accuracy_score = accuracy_score(y_true, y_pred)
# FINAL: accuracy_score -> Numeric; y_pred -> NumericList; y_true -> NumericList
