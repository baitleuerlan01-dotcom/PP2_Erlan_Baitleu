import re

s = input("Enter a string: ")
parts = re.findall(r'[A-Z][a-z]*', s)

print(parts)