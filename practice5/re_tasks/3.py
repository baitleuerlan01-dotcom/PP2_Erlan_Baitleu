import re

txt = input()
x = re.match(r"^[a-z]+(_[a-z]+)+$", txt)

print(x)