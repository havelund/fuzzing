import z3

"""
z3.InRe(s, regex) : s |- r
z3.Re(char)       : a
z3.Concat(r1, r2) : 
z3.Union(r1, r2)  : 
z3.Star(r)        : 
z3.Plus(r)        : 
z3.Option(r)      : 
z3.Loop(r, m, n)  : 
z3.Range(m, n)    : 
===
"\d"
"he..o"  any character except newline
"^hello"  starts with
"planet$"  ends with
"he.{2}o"  exactly 2 occurrences
"falls|stays"
\d
\s
\w
[arn]
[a-n]
[^arn]
"""

r1 = z3.Concat(z3.Re("a"), z3.Star(z3.Re("b")))  # ab*
r2 = z3.Loop(z3.Range('0','9'),2,3)  # [0,9][0,9][0,9]?
r3 = z3.Concat(z3.Plus(z3.Re("c")), z3.Option(z3.Re("d")))  # cd?
r4 = z3.Concat([r1, r2, r3])  # ab*[0,9][0,9][0,9]?cd?
r5 = z3.AllChar(z3.ReSort(z3.StringSort()))
r6 = z3.Intersect(r1, r5)
r7 = z3.Empty(z3.ReSort(z3.StringSort()))
r8 = z3.Re("abc.d")
r9 = z3.Concat(z3.Star(r5),z3.Re("ghi"))
s = z3.String('s')
t = z3.String('t')

solver = z3.Solver()

solver.add(z3.InRe(s, z3.Re("abc")))
solver.add(s == z3.StringVal("abc"))


if __name__ == '__main__':
    if solver.check() == z3.sat:
        print("The string matches the regex")
        model = solver.model()
        print(model)
    else:
        print("The string does not match the regex")
