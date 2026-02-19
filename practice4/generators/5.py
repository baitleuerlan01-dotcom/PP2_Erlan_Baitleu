#Implement a generator that returns all numbers from (n) down to 0.
def down(n):
    for i in range(n, -1, -1):
        yield i

n = int(input())

for x in down(n):
    print(x, end=" ")
