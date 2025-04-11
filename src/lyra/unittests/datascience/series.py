import pandas as pd
# STATE: df -> Top; s -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; s -> Top
s = df["a"]
# FINAL: df -> DataFrame; s -> Series