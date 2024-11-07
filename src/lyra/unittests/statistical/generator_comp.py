import pandas as pd

df = pd.read_csv('...')
text = " ".join(review for review in df["Text"])
# FINAL: df -> DataFrame; text -> String