where = input("Go left or right?")
sum=1
while where =="right":
    where = input("Go left or right?")
    sum+=1
    if sum==2:
        print (":(")
        break
print("You got out!")
