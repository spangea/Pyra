import pandas as pd
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
df.columns = ["C", "D"]
# FINAL: df -> DataFrame; df["C"] -> Series; df["D"] -> Series