l = [1,"a"]
ln = [1, 2]
ls = ["1", "2", "3"]
d = {'a': 1, 'b': 2, 'c': 3}
s = {"a", "b"}

l.pop()
ln.pop()
ls.pop()
d.pop("a")
s.pop()

l_ = l.pop()
ln_ = ln.pop()
ls_ = ls.pop()
d_ = d.pop("a")
s_ = s.pop()

# FINAL: d -> Dict; d_ -> Top; l -> List; l_ -> Top; ln -> NumericList; ln_ -> Numeric; ls -> StringList; ls_ -> String; s -> Set; s_ -> Top