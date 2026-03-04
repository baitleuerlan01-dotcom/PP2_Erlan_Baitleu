import re

s = input()

camel = re.sub(r'_([a-z])', lambda m: m.group(1).upper(), s)

print(camel)