import re

file = open("chrome_debug.log", 'r')
pattern = re.compile('^\[[\w\W]+?\]')
for line in file:
    match = pattern.match(line)
    if match:
        new_line = match.group().strip()[1:-1]
        attrs = line.split(':')
        process_id = attrs[0]
        thread_id = attrs[1]
        date_time = attrs[2].split('/')
        log_level = attrs[3]
        source_file = re.findall(r"^.+\(", attrs[4])[0][:-1]
        line_num = int(re.findall(r"\(\w*\)", attrs[4])[0][1:-1])
        tag = match.end()
        print(line[tag:])