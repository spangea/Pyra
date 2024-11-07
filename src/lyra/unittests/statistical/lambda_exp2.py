foo = lambda x: x.replace('a', 'b') if 'c' in x else x
x = foo(5)
# FINAL: foo -> Top; x -> Top