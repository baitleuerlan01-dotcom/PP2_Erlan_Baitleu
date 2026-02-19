from datetime import datetime, timedelta
today = datetime.now()
new_date = today - timedelta(days=5)
print(new_date)