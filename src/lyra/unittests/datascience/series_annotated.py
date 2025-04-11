import pandas as pd
# STATE: df -> DataFrame; s -> Top
df : pd.DataFrame = pd.read_csv("...")
# STATE: df -> DataFrame; s -> Top
s = df["a"]
# FINAL: df -> DataFrame; s -> Series