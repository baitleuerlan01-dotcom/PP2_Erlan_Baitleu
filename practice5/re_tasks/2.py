import re

txt = input()
x = re.match("^ab{2,3}$", txt)

print(x)