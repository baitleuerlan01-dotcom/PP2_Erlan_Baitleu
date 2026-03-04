import re

txt = input()
x = re.match("^ab*$", txt)

print(x)