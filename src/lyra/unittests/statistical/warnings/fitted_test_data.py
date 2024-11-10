import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler

data = {
    'feature1': range(10),
    'feature2': range(10),
}

df = pd.DataFrame(data)
scaler = MinMaxScaler()

X_train, X_test = train_test_split(df, test_size=0.2, random_state=42)
# STATE: X_test -> SplittedTestData; X_train -> SplittedTrainData; data -> Dict; df -> DataFrame; scaler -> MinMaxScaler

scaler.fit(X_test)
# STATE: X_test -> SplittedTestData; X_train -> SplittedTrainData; data -> Dict; df -> DataFrame; scaler -> MinMaxScaler
scaler.fit_transform(X_test)
# FINAL: X_test -> SplittedTestData; X_train -> SplittedTrainData; data -> Dict; df -> DataFrame; scaler -> MinMaxScaler
