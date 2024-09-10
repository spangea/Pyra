import pandas as pd
# STATE: ser -> Top; x -> Top
ser = pd.Series([1, 2], dtype='int32')
# STATE: ser -> Series; x -> Top
x = ser.astype('category')
# STATE: ser -> Series; x -> CatSeries
