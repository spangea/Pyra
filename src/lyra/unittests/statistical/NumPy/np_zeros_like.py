import numpy as np
# STATE: a -> Top; array -> Top; b -> Top; c -> Top; d -> Top; e -> Top; f -> Top; list -> Top
list = [[1,2,3],[1,2,3]]
# STATE: a -> Top; array -> Top; b -> Top; c -> Top; d -> Top; e -> Top; f -> Top; list -> List
array = np.array([1,2,3,4,5])
# STATE: a -> Top; array -> NumericArray; b -> Top; c -> Top; d -> Top; e -> Top; f -> Top; list -> List
a = np.zeros_like(["a", "b", "c"])
# STATE: a -> StringArray; array -> NumericArray; b -> Top; c -> Top; d -> Top; e -> Top; f -> Top; list -> List
b = np.zeros_like([1,2,3,4,5], dtype=np.str_)
# STATE: a -> StringArray; array -> NumericArray; b -> StringArray; c -> Top; d -> Top; e -> Top; f -> Top; list -> List
c = np.zeros_like(array)
# STATE: a -> StringArray; array -> NumericArray; b -> StringArray; c -> NumericArray; d -> Top; e -> Top; f -> Top; list -> List
d = np.zeros_like([1,2,3,4,5], dtype=bool)
# STATE: a -> StringArray; array -> NumericArray; b -> StringArray; c -> NumericArray; d -> BoolArray; e -> Top; f -> Top; list -> List
e = np.zeros_like(list)
# STATE: a -> StringArray; array -> NumericArray; b -> StringArray; c -> NumericArray; d -> BoolArray; e -> Array; f -> Top; list -> List
f = np.zeros_like([True, False, False], dtype=int)
# FINAL: a -> StringArray; array -> NumericArray; b -> StringArray; c -> NumericArray; d -> BoolArray; e -> Array; f -> NumericArray; list -> List