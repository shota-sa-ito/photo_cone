import json
import base64

import boto3


def get_img_objs_in_bucket(bucket_name):
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket_name)
    img_keys = bucket.objects.all()
    return img_keys


def get_img_from_s3(bucket_name, obj):
    s3 = boto3.client('s3')
    responce = s3.get_object(Bucket=bucket_name, Key=obj.key)
    body = responce['Body'].read()
    body = base64.b64encode(body).decode('utf-8')
    return body


def lambda_handler(event, context):
    bucket_name = event.get('pathParameters').get('fordername')
    img_objs = get_img_objs_in_bucket(bucket_name)
    resp = []
    for obj in img_objs:
        img = get_img_from_s3(bucket_name, obj)
        resp.append(
            {
                "bucket": bucket_name,
                "key": obj.key,
                "img": img,
            }
        )

    print(resp)
    print(json.dumps(resp))

    return {'statusCode': 200, 'body': json.dumps(resp)}
