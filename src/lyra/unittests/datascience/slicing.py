import pandas as pd
# STATE: df -> Top; df1 -> Top; l -> Top; l1 -> Top; ln -> Top; ln1 -> Top; ls -> Top; ls1 -> Top; s1 -> Top; s2 -> Top
df = pd.read_csv("...")
# STATE: df -> DataFrame; df1 -> Top; l -> Top; l1 -> Top; ln -> Top; ln1 -> Top; ls -> Top; ls1 -> Top; s1 -> Top; s2 -> Top
df1 = df[0:2]
# STATE: df -> DataFrame; df1 -> DataFrame; l -> Top; l1 -> Top; ln -> Top; ln1 -> Top; ls -> Top; ls1 -> Top; s1 -> Top; s2 -> Top
s1 = df["a"]
# STATE: df -> DataFrame; df1 -> DataFrame; l -> Top; l1 -> Top; ln -> Top; ln1 -> Top; ls -> Top; ls1 -> Top; s1 -> Series; s2 -> Top
s2 = s1[0:2]
# STATE: df -> DataFrame; df1 -> DataFrame; l -> Top; l1 -> Top; ln -> Top; ln1 -> Top; ls -> Top; ls1 -> Top; s1 -> Series; s2 -> Series
ln = [1,2,3]
# STATE: df -> DataFrame; df1 -> DataFrame; l -> Top; l1 -> Top; ln -> NumericList; ln1 -> Top; ls -> Top; ls1 -> Top; s1 -> Series; s2 -> Series
ln1 = ln[0:2]
# STATE: df -> DataFrame; df1 -> DataFrame; l -> Top; l1 -> Top; ln -> NumericList; ln1 -> NumericList; ls -> Top; ls1 -> Top; s1 -> Series; s2 -> Series
ls = ["1","2","3"]
# STATE: df -> DataFrame; df1 -> DataFrame; l -> Top; l1 -> Top; ln -> NumericList; ln1 -> NumericList; ls -> StringList; ls1 -> Top; s1 -> Series; s2 -> Series
ls1 = ls[0:2]
# STATE: df -> DataFrame; df1 -> DataFrame; l -> Top; l1 -> Top; ln -> NumericList; ln1 -> NumericList; ls -> StringList; ls1 -> StringList; s1 -> Series; s2 -> Series
l = [1, "2"]
# STATE: df -> DataFrame; df1 -> DataFrame; l -> List; l1 -> Top; ln -> NumericList; ln1 -> NumericList; ls -> StringList; ls1 -> StringList; s1 -> Series; s2 -> Series
l1 = l[0:2]
# FINAL: df -> DataFrame; df1 -> DataFrame; l -> List; l1 -> List; ln -> NumericList; ln1 -> NumericList; ls -> StringList; ls1 -> StringList; s1 -> Series; s2 -> Series
