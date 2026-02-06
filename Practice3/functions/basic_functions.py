#1 example
def my_function():
  print("Hello from a function")

#2 example
def my_function():
  print("Hello from a function")

my_function()

#3 example
def my_function():
  print("Hello from a function")

my_function()
my_function()
my_function()

#4 example 
Valid function names:
calculate_sum()
private_function()
myFunction2()

#5 example Without functions - repetitive code:
temp1 = 77
celsius1 = (temp1 - 32) * 5 / 9
print(celsius1)

temp2 = 95
celsius2 = (temp2 - 32) * 5 / 9
print(celsius2)

temp3 = 50
celsius3 = (temp3 - 32) * 5 / 9
print(celsius3)

#6 example With functions - reusable code:
def fahrenheit_to_celsius(fahrenheit):
  return (fahrenheit - 32) * 5 / 9

print(fahrenheit_to_celsius(77))
print(fahrenheit_to_celsius(95))
print(fahrenheit_to_celsius(50))