# edge_cases_script.py — edge cases for the tracer

# Variable reassignment many times
x = 0
x = 1
x = 2
x = "now a string"
x = [1, 2, 3]
x = None

# Large loop (stress test)
big_total = 0
for i in range(500):
    big_total += i

# Nested list comprehension equivalent (manual, so tracer catches it)
flat = []
nested = [[1, 2], [3, 4], [5, 6]]
for sublist in nested:
    for item in sublist:
        flat.append(item)

# Boolean toggling
flag = True
for _ in range(6):
    flag = not flag
