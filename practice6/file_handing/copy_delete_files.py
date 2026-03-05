#1 example
import os
os.remove("demofile.txt")

#2 example
import os
if os.path.exists("demofile.txt"):
  os.remove("demofile.txt")
else:
  print("The file does not exist")

#3 example
import os
os.rmdir("myfolder")

