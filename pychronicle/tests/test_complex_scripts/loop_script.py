# loop_script.py — complex loop test target for PyChronicle

# Simple for loop
total = 0
for i in range(10):
    total += i

# While loop
countdown = 5
while countdown > 0:
    countdown -= 1

# Nested loops
matrix_sum = 0
for row in range(3):
    for col in range(3):
        matrix_sum += row * col

# Loop with list building
squares = []
for n in range(1, 6):
    squares.append(n ** 2)

# Loop with conditionals
evens = []
odds = []
for val in range(20):
    if val % 2 == 0:
        evens.append(val)
    else:
        odds.append(val)
