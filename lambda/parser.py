import json
from urllib import response
import boto3
from botocore.exceptions import ClientError
import logging

def handler(event, context):
    s3 = boto3.client('s3')
    
    bucket_name = json.dumps(event['Records'][0]['s3']['bucket']['name'])[1:-1]
    key = json.dumps(event['Records'][0]['s3']['object']['key'])[1:-1]
    
    bucket = s3.Bucket(bucket_name)

    for object in bucket.objects.all():
        print(object)

    try:
        response = s3.get_object(Bucket=bucket_name, Key=key)
        print("response")
    except ClientError as e:
        logging.error(e)
    
    return {
        'bucket name': bucket_name,
        'key': key,
        'file name': "/tmp/{}".format(key)
    }