import pandas as pd
# STATE: df -> Top; time1 -> Top; time2 -> Top
time1 = [1.2, 3.5, 2.1, 4.5, 2.3]
# STATE: df -> Top; time1 -> NumericList; time2 -> Top
time2 = [1.1, 3.2, 2.0, 4.3, 2.2]
# STATE: df -> Top; time1 -> NumericList; time2 -> NumericList
df = pd.DataFrame({'time1': time1, 'time2': time2})
# STATE: df -> DataFrame; time1 -> NumericList; time2 -> NumericList
df['speedup'] = df['time1'] / df['time2']
# FINAL: df -> DataFrame; df["speedup"] -> RatioSeries; time1 -> NumericList; time2 -> NumericList

