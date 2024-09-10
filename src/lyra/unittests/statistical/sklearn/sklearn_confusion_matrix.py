from sklearn.metrics import confusion_matrix

# STATE: x_confusion_matrix -> Top; x_pred -> Top; x_true -> Top; y_confusion_matrix -> Top; y_pred -> Top; y_true -> Top
y_true = ["cat", "ant", "cat", "cat", "ant", "bird"]
# STATE: x_confusion_matrix -> Top; x_pred -> Top; x_true -> Top; y_confusion_matrix -> Top; y_pred -> Top; y_true -> StringList
y_pred = ["ant", "ant", "cat", "cat", "ant", "cat"]
# STATE: x_confusion_matrix -> Top; x_pred -> Top; x_true -> Top; y_confusion_matrix -> Top; y_pred -> StringList; y_true -> StringList
y_confusion_matrix = confusion_matrix(y_true, y_pred, labels=["ant", "bird", "cat"])
# STATE: x_confusion_matrix -> Top; x_pred -> Top; x_true -> Top; y_confusion_matrix -> Array; y_pred -> StringList; y_true -> StringList
x_true = [2, 0, 2, 2, 0, 1]
# STATE: x_confusion_matrix -> Top; x_pred -> Top; x_true -> NumericList; y_confusion_matrix -> Array; y_pred -> StringList; y_true -> StringList
x_pred = [0, 0, 2, 2, 0, 2]
# STATE: x_confusion_matrix -> Top; x_pred -> NumericList; x_true -> NumericList; y_confusion_matrix -> Array; y_pred -> StringList; y_true -> StringList
x_confusion_matrix = confusion_matrix(x_true, x_pred)
# FINAL: x_confusion_matrix -> Array; x_pred -> NumericList; x_true -> NumericList; y_confusion_matrix -> Array; y_pred -> StringList; y_true -> StringList
