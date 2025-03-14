
from z3 import *


s = String('s')
const = StringVal("hello")

s_concat = Concat(s, StringVal(" world"))
s_concat2 = Concat(s, "b", "c", "d")

len_s = Length(s)

sub = SubString(s, 0, 3)

idx = IndexOf(s, StringVal("abc"), 0)

new_s = Replace(s, StringVal("foo"), StringVal("bar"))

i = StrToInt(s)
s_num = IntToStr(i)

c = Contains(s, StringVal("test"))
p = PrefixOf(StringVal("start"), s)
suf = SuffixOf(StringVal("end"), s)

solver = Solver()
#solver.add(s == Concat(const, StringVal(" world")))
#solver.add(Length(s) == 11)
#solver.add(Contains(s, StringVal("lo w")))

r = Re("abc")

c1 = InRe(s, r)

# solver.add(s == "hello " + "hello")
# solver.add(s.__le__(s))

ascii_re = Re(r'[\x00-\x7F]*')


i = Int('i')

# List all ASCII characters (code points 0 to 127) as one-character strings.
ascii_chars = [StringVal(chr(c)) for c in range(128)]

solver = Solver()

# For every index i in the string s, if i is a valid position (i.e. 0 <= i < Length(s)),
# then the character at that position (SubString(s, i, 1)) must be equal to one of the ASCII characters.
solver.add(ForAll(i, Implies(And(i >= 0, i < Length(s)),
                              Or([SubString(s, i, 1) == a for a in ascii_chars]))))

if __name__ == '__main__':
    #ascii = Re(r'[\x00-\x7F]*')
    #constraint = InRe(s, ascii)
    i = Int('i')
    ascii_chars = [StringVal(chr(c)) for c in range(128)]
    ascii = constraint = ForAll([Int('i')],
                    Implies(And(Int('i') >= 0, Int('i') < Length(s)),
                            Or([SubString(s, Int('i'), 1) == ch for ch in ascii_chars])))
    less = s < StringVal("a")
    constraint = And([ascii, less])

    solver = Solver()
    solver.add(constraint)
    if solver.check() == sat:
        model = solver.model()
        print("Solution found:")
        print(model)
    else:
        print("No solution")


"""
Expressions:
  Strings:
    Concat(s, "b", "c", "d") :                      s1 + s2             s1 + s2 
    SubString(s, 0, 3) :                            substring(s,0,3)    s[i:j]
    Replace(s, StringVal("foo"), StringVal("bar")): replace(s,s1,s2)    s[r->t]
    IntToStr(i) :                                   int_to_str(i)       str(n)
  Integers:   
    Length(s) :                                     length(s)           |s|
    IndexOf(s, StringVal("abc"), 0) :               index_of(s,s1,0)    index(s,s1,0)  
    StrToInt(s) :                                   str_to_int(s)       int(s)
Formulas:
  Contains(s, StringVal("test")) :                  contains(s,t)       t in s
  PrefixOf(StringVal("start"), s) :                 prefix_of(s,t)      s << t
  SuffixOf(StringVal("end"), s) :                   suffix_of(s,t)      s >> t
  __lt__ :                                          s1 < s2             s1 < s2
  __le__ :                                          s1 <= s2            s1 <= s2
  __gt__ :                                          s1 > s2             s1 > s2 
  __ge__ :                                          s1 >= s2            s1 >= s2
  __eq__ :                                          s1 == s2            s1 == s2
"""