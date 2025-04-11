import pandas as pd
df = pd.read_csv('...')
x = df['a']
x_array = x.to_numpy()
y_array = df.to_numpy()
# FINAL: df -> DataFrame; x -> Series; x_array -> Array; y_array -> Array