import pandas as pd
# STATE: df -> Top; mean -> Top; median -> Top; x -> Top
x = ["Apple", "Orange", "Apple", "Apple", "Orange", "Orange", "Apple", "Apple"]
# STATE: df -> Top; mean -> Top; median -> Top; x -> StringList
df = pd.DataFrame(x, columns=["Fruit"])
# STATE: df -> DataFrame; mean -> Top; median -> Top; x -> StringList
df["Fruit"] = df["Fruit"].astype("category")
# STATE: df -> DataFrame; df["Fruit"] -> CatSeries; mean -> Top; median -> Top; x -> StringList
df["Fruit"]=df["Fruit"].cat.codes
# STATE: df -> DataFrame; df["Fruit"] -> CatSeries; mean -> Top; median -> Top; x -> StringList
mean = df["Fruit"].mean()
# STATE: df -> DataFrame; df["Fruit"] -> CatSeries; mean -> Numeric; median -> Top; x -> StringList
median = df["Fruit"].median()
# STATE: df -> DataFrame; df["Fruit"] -> CatSeries; mean -> Numeric; median -> Numeric; x -> StringList
