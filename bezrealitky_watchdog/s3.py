import json

import boto3


def upload_dict_to_s3(dict_, bucket_name, object_key):
    s3 = boto3.resource('s3')
    s3_object = s3.Object(bucket_name, object_key)
    s3_object.put(Body=json.dumps(dict_))


def download_dict_from_s3(bucket_name, object_key):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        dict_ = json.loads(response['Body'].read().decode('utf-8'))
        return dict_
    except s3.exceptions.NoSuchKey:
        return None
