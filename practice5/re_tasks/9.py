import re

s = input("Enter string: ")
result = re.sub(r'(?<=[a-z])([A-Z])', r' \1', s)

print(result)