#Write a program using generator to print the even nu
# mbers between 0 and n in comma separated form where n is input from console.
def even_gen(n):
    for i in range(0, n + 1):
        if i % 2 == 0:
            yield i
            
n = int(input())
print(",".join(map(str, even_gen(n))))
