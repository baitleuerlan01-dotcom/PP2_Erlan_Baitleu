import re

txt = input()
x = re.match("^[A-Z][a-z]+$", txt)

print(x)