import pandas as pd

df = pd.DataFrame([["ABC", "XYZ"]], columns=["Foo", "Bar"])
with pd.ExcelWriter("path_to_file.xlsx") as writer:
    df.to_excel(writer)

with open('file_path', 'w') as file:
    file.write('hello world !')
#FINAL: df -> DataFrame; file -> Top; writer -> Top