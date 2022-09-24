import json

import boto3


def lambda_handler(event, context):
    resp = []
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        resp.append(
            {
                "folder_name": bucket.name
            }
        )

    return {'statusCode': 200, 'body': json.dumps(resp)}
