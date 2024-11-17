import pandas as pd
from sklearn.preprocessing import PolynomialFeatures
# STATE: deanormalized_mean -> Top; df -> Top; scaler -> Top; wrong_normalized_mean -> Top; x -> Top
x = [1, 2, 3, 4, 5]
# STATE: deanormalized_mean -> Top; df -> Top; scaler -> Top; wrong_normalized_mean -> Top; x -> NumericList
df = pd.DataFrame(x, columns=['x'])
# STATE: deanormalized_mean -> Top; df -> DataFrame; scaler -> Top; wrong_normalized_mean -> Top; x -> NumericList
scaler = PolynomialFeatures()
# STATE: deanormalized_mean -> Top; df -> DataFrame; scaler -> PolynomialFeatures; wrong_normalized_mean -> Top; x -> NumericList
scaler.fit(df[['x']])
# STATE: deanormalized_mean -> Top; df -> DataFrame; scaler -> PolynomialFeatures; wrong_normalized_mean -> Top; x -> NumericList
df['x_normalized'] = scaler.transform(df[['x']])
# STATE: deanormalized_mean -> Top; df -> DataFrame; df["x_normalized"] -> NormSeries; scaler -> PolynomialFeatures; wrong_normalized_mean -> Top; x -> NumericList
wrong_normalized_mean = df['x_normalized'].mean()
# STATE: deanormalized_mean -> Top; df -> DataFrame; df["x_normalized"] -> NormSeries; scaler -> PolynomialFeatures; wrong_normalized_mean -> Numeric; x -> NumericList
deanormalized_mean = scaler.inverse_transform(df[['x_normalized']]).mean()
# FINAL: deanormalized_mean -> Numeric; df -> DataFrame; df["x_normalized"] -> NormSeries; scaler -> PolynomialFeatures; wrong_normalized_mean -> Numeric; x -> NumericList

# FIXME: check if transform and fit can be called like this