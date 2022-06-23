import json
import boto3
from botocore.exceptions import ClientError
import logging
import re
from decimal import Decimal
from datetime import (datetime, date, time)

def handler(event, context):
    s3 = boto3.client('s3')
    
    log = None

    bucket_name = json.dumps(event['Records'][0]['s3']['bucket']['arn'])[1:-1].split(':::')[1]
    key = json.dumps(event['Records'][0]['s3']['object']['key'])[1:-1]
    
    try:
        log = s3.get_object(Bucket=bucket_name, Key=key)['Body'].read()
    except ClientError as e:
        logging.error(e)
        
    file = open('/tmp/test.log', 'w')
    file.write(log.decode('utf-8'))
    file.close()
    file = open('/tmp/test.log', 'r')

    pattern = re.compile('^\[[\w\W]+?\]')

    new_log = open('/tmp/new_log.tsv', 'w+')
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
            try:
                print('{}\t{}\t{}\t{}\t{}\t{}\n'.format(date_time, err_stat, user, char_count, word_count, tag))
                new_log.write('{}\t{}\t{}\t{}\t{}\t{}\n'.format(date_time, err_stat, user, char_count, word_count, tag))
            except ClientError as e:
                return logging.error(e)
    new_log.close()
    try:
        s3.upload_file(new_log.name, bucket_name, 'log_data_{}_{}.tsv'.format(date.today(), datetime.now().strftime('%H:%M:%S')))
    except ClientError as e:
        return logging.error(e)
    
    return 'Completed'