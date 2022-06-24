from datetime import (datetime)
import random
import boto3
import json

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
        file.write('[{}::ERROR::{}::{}::{}] {}\n'.format(datetime.now(), user, length, words, random.choice(errors)))
    else:
        file.write('[{}::INFO::{}::{}::{}] {}\n'.format(datetime.now(), user, length, words, sentence))

file.close()

s3 = boto3.client('s3')


#change name to correct logbucket generated

bucket_file = open('outputs.txt')
bucket_name = json.load(bucket_file)['CdkAppStack']['Output'].split(':::')[1]
bucket_file.close()

s3.upload_file(file.name, bucket_name, 'word_log.log')