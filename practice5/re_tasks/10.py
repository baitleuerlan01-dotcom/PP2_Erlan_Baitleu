import re

s = input("Enter camelCase string: ")
snake = re.sub(r'([A-Z])', r'_\1', s).lower()
snake = snake.lstrip('_')

print(snake)