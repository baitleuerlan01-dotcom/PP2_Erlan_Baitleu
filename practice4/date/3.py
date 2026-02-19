from datetime import datetime
today = datetime.now()
new = today.replace(microsecond=0)
print(new)