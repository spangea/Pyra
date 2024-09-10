from numpy import ravel, array
# STATE: A -> Top; B -> Top; C -> Top; ravelA -> Top; ravelB -> Top; ravelC -> Top
A = 1
# STATE: A -> Numeric; B -> Top; C -> Top; ravelA -> Top; ravelB -> Top; ravelC -> Top
B = ["Hello", "World", "String"]
# STATE: A -> Numeric; B -> StringList; C -> Top; ravelA -> Top; ravelB -> Top; ravelC -> Top
C = array([[1, 2, 3], [4, 5, 6]])
# STATE: A -> Numeric; B -> StringList; C -> Array; ravelA -> Top; ravelB -> Top; ravelC -> Top
ravelA = ravel(A)
# STATE: A -> Numeric; B -> StringList; C -> Array; ravelA -> NumericArray; ravelB -> Top; ravelC -> Top
ravelB = ravel(B)
# STATE: A -> Numeric; B -> StringList; C -> Array; ravelA -> NumericArray; ravelB -> StringArray; ravelC -> Top
ravelC = ravel(C)
# FINAL: A -> Numeric; B -> StringList; C -> Array; ravelA -> NumericArray; ravelB -> StringArray; ravelC -> Array