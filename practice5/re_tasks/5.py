import re

txt = input()
x = re.match(r"^a.*b$", txt)

if x:
    print("True")
else:
    print("False")