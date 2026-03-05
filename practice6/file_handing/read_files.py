#1 example
f = open("demofile.txt")
print(f.read())

#2 example
f = open("D:\\myfiles\welcome.txt")
print(f.read())

#3 example
with open("demofile.txt") as f:
  print(f.read())

#4 example
f = open("demofile.txt")
print(f.readline())
f.close()

#5 example
with open("demofile.txt") as f:
  print(f.read(5))

#6 example
with open("demofile.txt") as f:
  print(f.readline())

#7 example
with open("demofile.txt") as f:
  print(f.readline())
  print(f.readline())

#8 example
with open("demofile.txt") as f:
  for x in f:
    print(x)