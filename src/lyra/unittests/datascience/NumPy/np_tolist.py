import numpy as np
# STATE: arr -> Top; l -> Top; numarr -> Top; numl -> Top; strarr -> Top; strl -> Top
numarr = np.array([1,2])
# STATE: arr -> Top; l -> Top; numarr -> NumericArray; numl -> Top; strarr -> Top; strl -> Top
numl = numarr.tolist()
# STATE: arr -> Top; l -> Top; numarr -> NumericArray; numl -> NumericList; strarr -> Top; strl -> Top
strarr = np.array(['abc','def'])
# STATE: arr -> Top; l -> Top; numarr -> NumericArray; numl -> NumericList; strarr -> StringArray; strl -> Top
strl = strarr.tolist()
# STATE: arr -> Top; l -> Top; numarr -> NumericArray; numl -> NumericList; strarr -> StringArray; strl -> StringList
arr = np.array([1,'abc'])
# STATE: arr -> Array; l -> Top; numarr -> NumericArray; numl -> NumericList; strarr -> StringArray; strl -> StringList
l = arr.tolist()
# FINAL: arr -> Array; l -> List; numarr -> NumericArray; numl -> NumericList; strarr -> StringArray; strl -> StringList
