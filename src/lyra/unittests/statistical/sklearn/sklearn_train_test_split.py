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
# STATE: X_scaled -> NormSeries; X_test -> Series; X_train -> Series; Y_test -> Top; Y_train -> Top; arr -> Top; data -> Dict; df -> DataFrame; l -> Top; scaler -> MinMaxScaler

arr = np.array([1,2,3,4])
# STATE: X_scaled -> NormSeries; X_test -> Series; X_train -> Series; Y_test -> Top; Y_train -> Top; arr -> NumericArray; data -> Dict; df -> DataFrame; l -> Top; scaler -> MinMaxScaler
X_train, X_test = train_test_split(arr)
# STATE: X_scaled -> NormSeries; X_test -> Array; X_train -> Array; Y_test -> Top; Y_train -> Top; arr -> NumericArray; data -> Dict; df -> DataFrame; l -> Top; scaler -> MinMaxScaler

l = [1,2,3,4]
# STATE: X_scaled -> NormSeries; X_test -> Array; X_train -> Array; Y_test -> Top; Y_train -> Top; arr -> NumericArray; data -> Dict; df -> DataFrame; l -> NumericList; scaler -> MinMaxScaler
X_train, X_test = train_test_split(l)
# STATE: X_scaled -> NormSeries; X_test -> List; X_train -> List; Y_test -> Top; Y_train -> Top; arr -> NumericArray; data -> Dict; df -> DataFrame; l -> NumericList; scaler -> MinMaxScaler

X_train, X_test, Y_train, Y_test = train_test_split(l, arr)
# STATE: X_scaled -> NormSeries; X_test -> List; X_train -> List; Y_test -> Array; Y_train -> Array; arr -> NumericArray; data -> Dict; df -> DataFrame; l -> NumericList; scaler -> MinMaxScaler

l = train_test_split(arr, l)
# FINAL: X_scaled -> NormSeries; X_test -> List; X_train -> List; Y_test -> Array; Y_train -> Array; arr -> NumericArray; data -> Dict; df -> DataFrame; l -> List; scaler -> MinMaxScaler
