import pandas as pd
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LinearRegression

# STATE: df -> Top; featureSelector -> Top; featureSelectorFitted -> Top; x -> Top
x = [1, 2, 3, 4, 5]
# STATE: df -> Top; featureSelector -> Top; featureSelectorFitted -> Top; x -> NumericList
df = pd.DataFrame(x, columns=['x'])
# STATE: df -> DataFrame; featureSelector -> Top; featureSelectorFitted -> Top; x -> NumericList
featureSelector = SelectFromModel(LinearRegression(), threshold=0.1)
# STATE: df -> DataFrame; featureSelector -> FeatureSelector; featureSelectorFitted -> Top; x -> NumericList
featureSelectorFitted = featureSelector.fit_transform(df[['x']], [0, 1, 1, 0, 1])
# FINAL: df -> DataFrame; featureSelector -> FeatureSelector; featureSelectorFitted -> FeatureSelected; x -> NumericList
