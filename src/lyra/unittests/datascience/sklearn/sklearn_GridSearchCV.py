from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
# STATE: grid_search -> Top; model -> Top; param_grid -> Top
model = SVC()
# STATE: grid_search -> Top; model -> Top; param_grid -> Top
param_grid = {
    'C': [1, 10],
    'kernel': ['linear', 'rbf']
}
# STATE: grid_search -> Top; model -> Top; param_grid -> Dict
grid_search = GridSearchCV(model, param_grid=param_grid)
# FINAL: grid_search -> Top; model -> Top; param_grid -> Dict