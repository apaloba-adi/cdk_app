import json
import boto3
from botocore.exceptions import ClientError
import logging
import re

def handler(event, context):
    s3 = boto3.client('s3')
    
    bucket_name = json.dumps(event['Records'][0]['s3']['bucket']['arn'])[1:-1].split(':::')[1]
    key = json.dumps(event['Records'][0]['s3']['object']['key'])[1:-1]
    
    try:
        log = s3.get_object(Bucket=bucket_name, Key=key)['Body'].read()
    except ClientError as e:
        logging.error(e)
        
    file = open('/tmp/test.log', 'w')
    file.write(log.decode("utf-8"))
    file.close()
    file = open('/tmp/test.log', 'r')

    pattern = re.compile('^\[[\w\W]+\][ ]')
    for line in file:
        match = pattern.match(line)
        if match:
            print(match.group().strip())
            
    return 'Written!'