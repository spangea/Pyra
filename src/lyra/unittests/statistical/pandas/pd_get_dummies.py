import pandas as pd
# STATE: df -> Top
df = pd.DataFrame([('Foreign Cinema', 289.0),
                   ('Liho Liho', 224.0),
                   ('500 Club', 80.5),
                   ('Foreign Cinema', 25.30)],
           columns=('name', 'Amount')
                 )
# STATE: df -> DataFrame
df = pd.get_dummies(df, columns=['name'])
# STATE: df -> DataFrame; df["name"] -> CatSeries
