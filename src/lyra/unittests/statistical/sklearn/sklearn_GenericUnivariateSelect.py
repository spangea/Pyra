import pandas as pd
from sklearn.feature_selection import GenericUnivariateSelect
# STATE: df -> Top; featureSelector -> Top; featureSelectorFitted -> Top; x -> Top; y -> Top
x = [1, 2, 3, 4, 5]
# STATE: df -> Top; featureSelector -> Top; featureSelectorFitted -> Top; x -> NumericList; y -> Top
y = [0, 1, 0, 1, 0]
# STATE: df -> Top; featureSelector -> Top; featureSelectorFitted -> Top; x -> NumericList; y -> NumericList
df = pd.DataFrame(x, columns=['x'])
# STATE: df -> DataFrame; featureSelector -> Top; featureSelectorFitted -> Top; x -> NumericList; y -> NumericList
featureSelector = GenericUnivariateSelect(mode='k_best', param=1)
# STATE: df -> DataFrame; featureSelector -> FeatureSelector; featureSelectorFitted -> Top; x -> NumericList; y -> NumericList
featureSelectorFitted = featureSelector.fit_transform(df[['x']], y)
# FINAL: df -> DataFrame; featureSelector -> FeatureSelector; featureSelectorFitted -> FeatureSelected; x -> NumericList; y -> NumericList
