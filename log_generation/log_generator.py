from datetime import datetime
import random
import boto3

file = open('log_generation/word_log.log', 'w+')

error_num = random.randint(1, 5)

errors = [
    'FALSE ALARM',
    'BADLY FORMATTED',
    'TIMEOUT, RECONNECTING',
    'MALFORMED REQUEST',
    'INVALID ENCODING'
]

users = [
    'Bobby',
    'James',
    'Jean',
    'Ororo',
    'Hank',
    'Charles',
    'Kurt',
    'Scott',
    'Warren'
]

while True:
    num = random.randint(1,5)
    sentence = None
    sentence = input('Give me a sentence: ')
    if sentence == '':
        break
    length = len(sentence)
    words = len(sentence.split(' '))
    user = random.choice(users)
    if error_num == num:
        file.write('\n[{}::ERROR::{}::{}::{}] {}\n'.format(datetime.now(), user, length, words, random.choice(errors)))
    else:
        file.write('\n[{}::INFO::{}::{}::{}] {}\n'.format(datetime.now(), user, length, words, sentence))

file.close()

s3 = boto3.client('s3')

s3.upload_file(file.name, 'cdkappstack-logbucketcc3b17e8-1ms8j0ohr6djo', 'word_log.log')