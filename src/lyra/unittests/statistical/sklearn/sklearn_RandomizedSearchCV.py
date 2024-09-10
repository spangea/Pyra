from sklearn.svm import SVC
from sklearn.model_selection import RandomizedSearchCV
# STATE: model -> Top; param_dist -> Top; random_search -> Top
model = SVC()
# STATE: model -> Top; param_dist -> Top; random_search -> Top
param_dist = {
    'C': [1, 10],
    'kernel': ['linear', 'rbf']
}
# STATE: model -> Top; param_dist -> Dict; random_search -> Top
random_search = RandomizedSearchCV(model, param_distributions=param_dist, n_iter=2)
# FINAL: model -> Top; param_dist -> Dict; random_search -> Top