import pandas as pd
from sklearn.feature_selection import SelectPercentile
# STATE: df -> Top; featureSelector -> Top; featureSelectorFitted -> Top; x -> Top
x = [1, 2, 3, 4, 5]
# STATE: df -> Top; featureSelector -> Top; featureSelectorFitted -> Top; x -> NumericList
df = pd.DataFrame(x, columns=['x'])
# STATE: df -> DataFrame; featureSelector -> Top; featureSelectorFitted -> Top; x -> NumericList
featureSelector = SelectPercentile()
# STATE: df -> DataFrame; featureSelector -> FeatureSelector; featureSelectorFitted -> Top; x -> NumericList
featureSelectorFitted = featureSelector.fit_transform(df[['x']])
# FINAL: df -> DataFrame; featureSelector -> FeatureSelector; featureSelectorFitted -> FeatureSelected; x -> NumericList
