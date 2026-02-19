from datetime import datetime , timedelta  
today = datetime.now()
yesterday = today - timedelta(days=1)
tomorrow = today + timedelta(days=1)
print("Today:", today)
print("Yesterday:", yesterday)
print("Tomorrow:", tomorrow)