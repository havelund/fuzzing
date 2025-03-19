
import re

txt = "The rain in Spain"
x = re.search("^The.*Spain$", txt)
print(x)

if __name__ == '__main__':
    pass