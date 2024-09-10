import pandas as pd
# STATE: df -> Top; df1 -> Top; list -> Top; listCopy -> Top; series -> Top; series1 -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; df1 -> Top; list -> Top; listCopy -> Top; series -> Top; series1 -> Top
list = [1, 2, 3]
# STATE: df -> DataFrame; df1 -> Top; list -> NumericList; listCopy -> Top; series -> Top; series1 -> Top
df1 = df.copy()
# STATE: df -> DataFrame; df1 -> DataFrame; list -> NumericList; listCopy -> Top; series -> Top; series1 -> Top
listCopy = list.copy()
# STATE: df -> DataFrame; df1 -> DataFrame; list -> NumericList; listCopy -> NumericList; series -> Top; series1 -> Top
series = df["Test"]
# STATE: df -> DataFrame; df1 -> DataFrame; list -> NumericList; listCopy -> NumericList; series -> Series; series1 -> Top
series1 = series.copy()
# FINAL: df -> DataFrame; df1 -> DataFrame; list -> NumericList; listCopy -> NumericList; series -> Series; series1 -> Series