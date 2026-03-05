#map
def square(n):
    return n**n
a=list(map(square, range(1,5)))
print(a)

#filter
def is_even(n):
    return n%2==0
res=filter(is_even, range(11))
print(list(res))

#reduce
from functools import reduce
def summ(x,y):
    return x+y
print(reduce(summ, [1,2,3,4]))