import json

import boto3


def lambda_handler(event, context):
    resp = []
    s3 = boto3.resource('s3')
    for bucket in s3.buckets.all():
        strings = bucket.name.split('-')
        if len(strings) > 0 and strings[0] == 'ishinomakihackathon2022':
            resp.append(
                {
                    "folder_name": bucket.name
                }
            )

    return {
        'statusCode': 200,
        'headers': {"Access-Control-Allow-Origin": "*"},
        'body': json.dumps(resp)
    }
