import json
import boto3
from botocore.exceptions import ClientError
import logging

def handler(event, context):
    s3 = boto3.client('s3')
    
    bucket_name = json.dumps(event['Records'][0]['s3']['bucket']['name'])[1:-1]
    key = json.dumps(event['Records'][0]['s3']['object']['key'])[1:-1]
    
    try:
        log = s3.get_object(Bucket=bucket_name, Key=key)
        print(log)
    except ClientError as e:
        logging.error(e)
    
    return {
        'bucket name': bucket_name,
        'key': key,
        'file name': "/tmp/{}".format(key)
    }