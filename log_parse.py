import re

file = open("chrome_debug.log", 'r')
pattern = re.compile('^\[[\w\W]+\][ ]')
for line in file:
    match = pattern.match(line)
    if match:
        print(match.group().strip())