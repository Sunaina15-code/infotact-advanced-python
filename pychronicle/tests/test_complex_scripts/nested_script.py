# nested_script.py — nested structures test target

# Nested loop with accumulator
result = {}
for letter in ['a', 'b', 'c']:
    count = 0
    for num in range(1, 4):
        count += num
    result[letter] = count

# Function-style logic (no def, just inline)
data = [3, 1, 4, 1, 5, 9, 2, 6]
max_val = data[0]
for item in data:
    if item > max_val:
        max_val = item

# String building loop
word = ""
for char in "PyChronicle":
    word += char

# Fibonacci
fib = [0, 1]
for _ in range(8):
    fib.append(fib[-1] + fib[-2])
