import re

txt = input()
result = re.sub(r"[ ,.]", ":", txt)

print(result)