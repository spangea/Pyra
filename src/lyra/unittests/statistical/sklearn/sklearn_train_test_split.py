import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

data = {
    'feature1': range(10),
    'feature2': range(20),
}

df = pd.DataFrame(data)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(df)
X_train, X_test = train_test_split(X_scaled, test_size=0.2, random_state=42)
# FINAL: X_scaled -> NormSeries; X_test -> NormSeries; X_train -> NormSeries; data -> Dict; df -> DataFrame; scaler -> MinMaxScaler