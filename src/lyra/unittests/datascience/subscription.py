import pandas as pd
import numpy as np

# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Top; df -> Top; l -> Top; lb -> Top; ln -> Top; ls -> Top; s -> Top; str1 -> Top; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Top; z2 -> Top; z3 -> Top
df = pd.read_csv("...")
# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Top; df -> DataFrame; l -> Top; lb -> Top; ln -> Top; ls -> Top; s -> Top; str1 -> Top; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Top; z2 -> Top; z3 -> Top
s = df["a"]
# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Top; df -> DataFrame; l -> Top; lb -> Top; ln -> Top; ls -> Top; s -> Series; str1 -> Top; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Top; z2 -> Top; z3 -> Top
z1 = s[0]
# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Top; df -> DataFrame; l -> Top; lb -> Top; ln -> Top; ls -> Top; s -> Series; str1 -> Top; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Top; z3 -> Top

ln = [1,2,3]
# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Top; df -> DataFrame; l -> Top; lb -> Top; ln -> NumericList; ls -> Top; s -> Series; str1 -> Top; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Top; z3 -> Top
z2 = ln[1]
# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Top; df -> DataFrame; l -> Top; lb -> Top; ln -> NumericList; ls -> Top; s -> Series; str1 -> Top; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Top
ls = ["1","2","3"]
# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Top; df -> DataFrame; l -> Top; lb -> Top; ln -> NumericList; ls -> StringList; s -> Series; str1 -> Top; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Top
str1 = ls[1]
# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Top; df -> DataFrame; l -> Top; lb -> Top; ln -> NumericList; ls -> StringList; s -> Series; str1 -> String; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Top
lb = [True,True,False]
# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Top; df -> DataFrame; l -> Top; lb -> BoolList; ln -> NumericList; ls -> StringList; s -> Series; str1 -> String; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Top
b1 = lb[1]
# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Boolean; df -> DataFrame; l -> Top; lb -> BoolList; ln -> NumericList; ls -> StringList; s -> Series; str1 -> String; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Top
l = [1, "2"]
# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Boolean; df -> DataFrame; l -> List; lb -> BoolList; ln -> NumericList; ls -> StringList; s -> Series; str1 -> String; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Top
top1 = l[0]
# STATE: arr -> Top; arrn -> Top; arrs -> Top; b1 -> Boolean; df -> DataFrame; l -> List; lb -> BoolList; ln -> NumericList; ls -> StringList; s -> Series; str1 -> String; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Top

arrn = np.array([1,2,3])
# STATE: arr -> Top; arrn -> NumericArray; arrs -> Top; b1 -> Boolean; df -> DataFrame; l -> List; lb -> BoolList; ln -> NumericList; ls -> StringList; s -> Series; str1 -> String; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Top
z3 = arrn[1]
# STATE: arr -> Top; arrn -> NumericArray; arrs -> Top; b1 -> Boolean; df -> DataFrame; l -> List; lb -> BoolList; ln -> NumericList; ls -> StringList; s -> Series; str1 -> String; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Numeric
arrs = np.array(["a","b","c"])
# STATE: arr -> Top; arrn -> NumericArray; arrs -> StringArray; b1 -> Boolean; df -> DataFrame; l -> List; lb -> BoolList; ln -> NumericList; ls -> StringList; s -> Series; str1 -> String; str2 -> Top; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Numeric
str2 = arrs[1]
# STATE: arr -> Top; arrn -> NumericArray; arrs -> StringArray; b1 -> Boolean; df -> DataFrame; l -> List; lb -> BoolList; ln -> NumericList; ls -> StringList; s -> Series; str1 -> String; str2 -> String; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Numeric
arr = np.array([1,"2"])
# STATE: arr -> Array; arrn -> NumericArray; arrs -> StringArray; b1 -> Boolean; df -> DataFrame; l -> List; lb -> BoolList; ln -> NumericList; ls -> StringList; s -> Series; str1 -> String; str2 -> String; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Numeric
top2 = arr[0]
# FINAL: arr -> Array; arrn -> NumericArray; arrs -> StringArray; b1 -> Boolean; df -> DataFrame; l -> List; lb -> BoolList; ln -> NumericList; ls -> StringList; s -> Series; str1 -> String; str2 -> String; top1 -> Top; top2 -> Top; z1 -> Scalar; z2 -> Numeric; z3 -> Numeric
