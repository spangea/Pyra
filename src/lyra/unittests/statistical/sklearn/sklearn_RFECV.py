import pandas as pd
from sklearn.feature_selection import RFECV
from sklearn.linear_model import LinearRegression

# STATE: df -> Top; featureSelector -> Top; featureSelectorFitted -> Top
df = pd.DataFrame({
    'x1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'x2': [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
})
# STATE: df -> DataFrame; featureSelector -> Top; featureSelectorFitted -> Top
featureSelector = RFECV(LinearRegression())
# STATE: df -> DataFrame; featureSelector -> FeatureSelector; featureSelectorFitted -> Top
featureSelectorFitted = featureSelector.fit_transform(df[['x1','x2']], [0, 1, 1, 0, 1, 0, 1, 1, 0, 1])
# FINAL: df -> DataFrame; featureSelector -> FeatureSelector; featureSelectorFitted -> FeatureSelected
