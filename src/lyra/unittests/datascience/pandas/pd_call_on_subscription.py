import  pandas as pd
# STATE: df -> Top; time1 -> Top; time2 -> Top; wrong_avg_speedup1 -> Top; wrong_avg_speedup2 -> Top
time1 = [1.2, 3.5, 2.1, 4.5, 2.3]
# STATE: df -> Top; time1 -> NumericList; time2 -> Top; wrong_avg_speedup1 -> Top; wrong_avg_speedup2 -> Top
time2 = [1.1, 3.2, 2.0, 4.3, 2.2]
# STATE: df -> Top; time1 -> NumericList; time2 -> NumericList; wrong_avg_speedup1 -> Top; wrong_avg_speedup2 -> Top
df = pd.DataFrame({'time1': time1, 'time2': time2})
# STATE: df -> DataFrame; time1 -> NumericList; time2 -> NumericList; wrong_avg_speedup1 -> Top; wrong_avg_speedup2 -> Top
df['speedup'] = df['time1'] / df['time2']
# STATE: df -> DataFrame; df["speedup"] -> RatioSeries; time1 -> NumericList; time2 -> NumericList; wrong_avg_speedup1 -> Top; wrong_avg_speedup2 -> Top
wrong_avg_speedup1 = df['speedup'].mean()   # Should raise plausible warning
# STATE: df -> DataFrame; df["speedup"] -> RatioSeries; time1 -> NumericList; time2 -> NumericList; wrong_avg_speedup1 -> Numeric; wrong_avg_speedup2 -> Top
wrong_avg_speedup2= df['a'].mean()          # Should raise possible warning
# FINAL: df -> DataFrame; df["speedup"] -> RatioSeries; time1 -> NumericList; time2 -> NumericList; wrong_avg_speedup1 -> Numeric; wrong_avg_speedup2 -> Numeric