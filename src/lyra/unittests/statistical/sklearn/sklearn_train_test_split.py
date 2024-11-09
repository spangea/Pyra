import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler

data = {
    'feature1': range(10),
    'feature2': range(10),
}

df = pd.DataFrame(data, columns=['x'])
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(df)
Y = df

X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)
# STATE: X_scaled -> NormSeries; X_test -> SplittedTestData; X_train -> SplittedTrainData; Y -> DataFrame; Y_test -> Top; Y_train -> Top; data -> Dict; df -> DataFrame; scaler -> MinMaxScaler
X_train, X_test, Y_train, Y_test = train_test_split(X_scaled, Y, test_size=0.2, random_state=42)
# STATE: X_scaled -> NormSeries; X_test -> SplittedTestData; X_train -> SplittedTrainData; Y -> DataFrame; Y_test -> SplittedTestData; Y_train -> SplittedTrainData; data -> Dict; df -> DataFrame; scaler -> MinMaxScaler


scaler = StandardScaler()
scaler.fit(df[['x']])
# STATE: X_scaled -> NormSeries; X_test -> SplittedTestData; X_train -> SplittedTrainData; Y -> DataFrame; Y_test -> SplittedTestData; Y_train -> SplittedTrainData; data -> Dict; df -> DataFrame; scaler -> StandardScaler

Y = scaler.transform(df[['x']])
# STATE: X_scaled -> NormSeries; X_test -> SplittedTestData; X_train -> SplittedTrainData; Y -> StdSeries; Y_test -> SplittedTestData; Y_train -> SplittedTrainData; data -> Dict; df -> DataFrame; scaler -> StandardScaler
X_train, X_test, Y_train, Y_test = train_test_split(X_scaled, Y, test_size=0.2, random_state=42)
# FINAL: X_scaled -> NormSeries; X_test -> SplittedTestData; X_train -> SplittedTrainData; Y -> StdSeries; Y_test -> SplittedTestData; Y_train -> SplittedTrainData; data -> Dict; df -> DataFrame; scaler -> StandardScaler
