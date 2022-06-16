import json
import boto3
from botocore.exceptions import ClientError
import logging
import re
from decimal import Decimal

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
    
    db = boto3.resource('dynamodb')
    process_id = None
    thread_id = None
    date_time = None
    log_level = None
    source_file = None
    line_num = None
    tag = None

    pattern = re.compile('^\[[\w\W]+?\]')

    new_log = open('/tmp/new_log.tsv', 'w+')
    for line in file:
        match = pattern.match(line)
        if match:
            new_line = match.group().strip()[1:-1]
            attrs = new_line.split(':')
            process_id = int(attrs[0])
            thread_id = int(attrs[1])
            date_time = attrs[2].split('/')
            log_level = attrs[3]
            source_file = re.findall(r'^.+\(', attrs[4])[0][:-1]
            line_num = int(re.findall(r'\(\w*\)', attrs[4])[0][1:-1])
            timestamp = "2022-{}-{} {}:{}:{}".format(date_time[0][:2], date_time[0][2:4], date_time[1][0:2], date_time[1][2:4], date_time[1][4:])
            tag = line[match.end():].strip()
            try:
                print('{}\t{}\t{}\t{}\t{}\t{}\t{}\n\n'.format(timestamp,tag,source_file,line_num,process_id,thread_id, log_level))
                new_log.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(timestamp,tag,source_file,line_num,process_id,thread_id, log_level))
            except ClientError as e:
                return logging.error(e)
    new_log.close()
    try:
        s3.upload_file(new_log.name, bucket_name, 'log_data.tsv')
    except ClientError as e:
        return logging.error(e)
    
    return 'Completed'