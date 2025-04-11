import numpy as np
# STATE: array -> Top; dict -> Top; numbers -> Top; string -> Top
numbers = [4, 2, 9, 1, 5, 6]
# STATE: array -> Top; dict -> Top; numbers -> NumericList; string -> Top
string = "python"
# STATE: array -> Top; dict -> Top; numbers -> NumericList; string -> String
array = np.array(["Hello", "World", "!"])
# STATE: array -> StringArray; dict -> Top; numbers -> NumericList; string -> String
dict = {"a": 3, "c": 1, "b": 2}
# STATE: array -> StringArray; dict -> Dict; numbers -> NumericList; string -> String
numbers = sorted(numbers)
# STATE: array -> StringArray; dict -> Dict; numbers -> NumericList; string -> String
string = sorted(string)
# STATE: array -> StringArray; dict -> Dict; numbers -> NumericList; string -> List
array = sorted(array)
# STATE: array -> StringList; dict -> Dict; numbers -> NumericList; string -> List
dict = sorted(dict)
# FINAL: array -> StringList; dict -> List; numbers -> NumericList; string -> List