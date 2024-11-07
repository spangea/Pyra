import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

data = {
    'feature1': range(10),
    'feature2': range(10),
}

df = pd.DataFrame(data)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(df)
X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)

arr = np.array([1,2,3,4])
X_train, X_test = train_test_split(arr)
l = [1,2,3,4]
X_train, X_test = train_test_split(l)
X_train, X_test, Y_train, Y_test = train_test_split(l, arr)
l = train_test_split(arr, l)
# FINAL: X_scaled -> NormSeries; X_test -> SplittedTestData; X_train -> SplittedTrainData; Y_test -> SplittedTestData; Y_train -> SplittedTrainData; arr -> NumericArray; data -> Dict; df -> DataFrame; l -> List; scaler -> MinMaxScaler
