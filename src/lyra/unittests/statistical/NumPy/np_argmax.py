import numpy as np
# STATE: A -> Top; B -> Top; C -> Top; IndexA -> Top; IndexB -> Top; IndexC -> Top
A = [[[1,2,3,4],[5,6,7,8],[9,10,11,12]],[[1,2,3,4],[5,6,7,8],[9,10,11,12]]]
# STATE: A -> List; B -> Top; C -> Top; IndexA -> Top; IndexB -> Top; IndexC -> Top
B = 10
# STATE: A -> List; B -> Numeric; C -> Top; IndexA -> Top; IndexB -> Top; IndexC -> Top
C = [1,2,3]
# STATE: A -> List; B -> Numeric; C -> NumericList; IndexA -> Top; IndexB -> Top; IndexC -> Top
IndexA = np.argmax(A, 2)
# STATE: A -> List; B -> Numeric; C -> NumericList; IndexA -> Array; IndexB -> Top; IndexC -> Top
IndexB = np.argmax(B)
# STATE: A -> List; B -> Numeric; C -> NumericList; IndexA -> Array; IndexB -> Numeric; IndexC -> Top
IndexC = np.argmax(C, 0)
# FINAL: A -> List; B -> Numeric; C -> NumericList; IndexA -> Array; IndexB -> Numeric; IndexC -> Numeric