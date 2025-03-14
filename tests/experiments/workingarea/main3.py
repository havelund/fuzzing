import z3

"""
[x] z3.InRe(s, regex) : This function checks if a string s matches a regular expression regex.
[x] z3.Re(char)       : Represents a single character.
[x] z3.Concat(r1, r2) : Concatenates two regular expressions.
[x] z3.Union(r1, r2)  : Represents the union of two regular expressions.
[x] z3.Star(r)        : Represents zero or more occurrences of r.
[x] z3.Plus(r)        : Represents one or more occurrences of r.
[x] z3.Option(r)      : Represents zero or one occurrences of r.
[x] z3.Loop(r, m, n)  : Represents m to n occurrences of r.
[x] z3.Range(m, n)    : Represents a range of characters.
"""

r1 = z3.Concat(z3.Re("a"), z3.Star(z3.Re("b")))  # ab*
r2 = z3.Loop(z3.Range('0','9'),2,3)  # [0,9][0,9][0,9]?
r3 = z3.Concat(z3.Plus(z3.Re("c")), z3.Option(z3.Re("d")))  # cd?

regex = z3.Concat([r1, r2, r3])  # ab*[0,9][0,9][0,9]?cd?

s1 = z3.StringVal("abb")
s2 = z3.StringVal("25")
s3 = z3.StringVal("cde")
s4 = z3.StringVal("abbb234cd")

s = s4

solver = z3.Solver()
solver.add(z3.InRe(s, regex))
if solver.check() == z3.sat:
  print("The string matches the regex")
  model = solver.model()
  print(model)
else:
  print("The string does not match the regex")