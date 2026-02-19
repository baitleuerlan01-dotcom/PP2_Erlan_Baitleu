#Create a generator that generates the squares of numbers up to some number N.
def square_generator(N):
    for i in range(1, N + 1):
        yield i * i

N = int(input())
for sq in square_generator(N):
    print(sq, end=" ")
