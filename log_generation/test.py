import re

pattern = re.compile('^\[[\w\W]+?\]')

file = open('log_generation/word_log.log', 'r')

for line in file:
    match = pattern.match(line)
    if match:
        new_line = match.group().strip()[1:-1]
        attrs = new_line.split('::')
        date_time = attrs[0]
        err_stat = attrs[1]
        user = attrs[2]
        char_count = int(attrs[3])
        word_count = int(attrs[4])
        tag = line[match.end():].strip()
        print('{}\t{}\t{}\t{}\t{}\t{}\n'.format(date_time, err_stat, user, char_count, word_count, tag))