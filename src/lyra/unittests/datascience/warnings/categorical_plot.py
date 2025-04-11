import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# STATE: dati -> Top; df -> Top; x -> Top; y -> Top
dati = {
    'materie': ['Matematica', 'Fisica', 'Informatica'],
    'voti': [28, 30, 29]
}
# STATE: dati -> Dict; df -> Top; x -> Top; y -> Top
plt.plot('materie', 'voti', data=dati)
# STATE: dati -> Dict; df -> Top; x -> Top; y -> Top


x = np.array([" Apple " , " Banana " , " Orange " , " Grape " , " Strawberry "])
# STATE: dati -> Dict; df -> Top; x -> StringArray; y -> Top
y = [10 , 15 , 20 , 12 , 18]
# STATE: dati -> Dict; df -> Top; x -> StringArray; y -> NumericList
plt.plot(x, y)
# STATE: dati -> Dict; df -> Top; x -> StringArray; y -> NumericList


x = [" Apple " , " Banana " , " Orange " , " Grape " , " Strawberry "]
# STATE: dati -> Dict; df -> Top; x -> StringList; y -> NumericList
y = [10 , 15 , 20 , 12 , 18]
# STATE: dati -> Dict; df -> Top; x -> StringList; y -> NumericList
plt.plot(x, y)
# STATE: dati -> Dict; df -> Top; x -> StringList; y -> NumericList


plt.plot([" Apple " , " Banana " , " Orange " , " Grape " , " Strawberry "], y)
# STATE: dati -> Dict; df -> Top; x -> StringList; y -> NumericList

plt.plot(x, [10 , 15 , 20 , 12 , 18])
# STATE: dati -> Dict; df -> Top; x -> StringList; y -> NumericList

plt.plot([" Apple " , " Banana " , " Orange " , " Grape " , " Strawberry "], [10 , 15 , 20 , 12 , 18])
# STATE: dati -> Dict; df -> Top; x -> StringList; y -> NumericList

plt.plot([10 , 15 , 20 , 12 , 18], [10 , 15 , 20 , 12 , 18])
# STATE: dati -> Dict; df -> Top; x -> StringList; y -> NumericList

plt.plot(y)
# STATE: dati -> Dict; df -> Top; x -> StringList; y -> NumericList

df = pd.DataFrame(x, columns=["Fruit"])
# STATE: dati -> Dict; df -> DataFrame; x -> StringList; y -> NumericList
x = df["Fruit"].astype("string")
# STATE: dati -> Dict; df -> DataFrame; x -> StringSeries; y -> NumericList
plt.plot(x, y)
# STATE: dati -> Dict; df -> DataFrame; x -> StringSeries; y -> NumericList


x = [" Apple " , " Banana " , " Orange " , " Grape " , " Strawberry "]
# STATE: dati -> Dict; df -> DataFrame; x -> StringList; y -> NumericList
x = df["Fruit"].astype("category")
# STATE: dati -> Dict; df -> DataFrame; x -> CatSeries; y -> NumericList
plt.plot(x, y)
# STATE: dati -> Dict; df -> DataFrame; x -> CatSeries; y -> NumericList


x = np.array([" Apple " , 0 , " Orange " , " Grape " , " Strawberry "])
# STATE: dati -> Dict; df -> DataFrame; x -> Array; y -> NumericList
plt.plot(x, y)
# STATE: dati -> Dict; df -> DataFrame; x -> Array; y -> NumericList


x = [" Apple " , " Banana " , " Orange " , " Grape " , " Strawberry "]
# STATE: dati -> Dict; df -> DataFrame; x -> StringList; y -> NumericList
df = pd.DataFrame(x, columns=["Fruit"])
# STATE: dati -> Dict; df -> DataFrame; x -> StringList; y -> NumericList
x = df["Fruit"]
# STATE: dati -> Dict; df -> DataFrame; x -> Series; y -> NumericList
plt.plot(x, y)
# FINAL: dati -> Dict; df -> DataFrame; x -> Series; y -> NumericList
