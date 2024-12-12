import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, Normalizer, RobustScaler, OneHotEncoder, SplineTransformer
from sklearn.feature_selection import SelectKBest

data = {
    'feature1': range(10),
    'feature2': range(10),
}

df = pd.DataFrame(data)
scaler = MinMaxScaler()

normalized = Normalizer().fit_transform(df)
X_train, X_test = train_test_split(normalized, test_size=0.2, random_state=42)

standardized = RobustScaler().fit_transform(df)
X_train, X_test = train_test_split(standardized, test_size=0.2, random_state=42)

featureSelected = SelectKBest().fit_transform(df)
X_train, X_test = train_test_split(featureSelected, test_size=0.2, random_state=42)

encoder = OneHotEncoder().fit_transform(df)
X_train, X_test = train_test_split(encoder, test_size=0.2, random_state=42)

series = SplineTransformer().fit_transform(df)
X_train, X_test = train_test_split(series, test_size=0.2, random_state=42)

scaler.fit(X_test)
scaler.fit_transform(X_test)