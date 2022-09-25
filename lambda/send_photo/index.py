import os
import json
import uuid
import base64

import boto3

dynamodb = boto3.resource('dynamodb')
connections = dynamodb.Table(os.environ['table'])


def lambda_handler(event, context):
    image = json.loads(event.get('body', '{}')).get('base_64_image')
    folder_name = json.loads(event.get('body', '{}')).get('folder_name')

    if image is None:
        return {'statusCode': 500, 'body': 'image not specified'}

    if folder_name is None:
        return {'statusCode': 500, 'body': 'folder_name not specified'}

    # 画像を保存
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(folder_name)
    bucket_policy = {
        'Version': '2012-10-17',
        'Statement': [{
            'Sid': 'AddPerm',
            'Effect': 'Allow',
            'Principal': '*',
            'Action': ['s3:GetObject'],
            'Resource': f'arn:aws:s3:::{folder_name}/*'
        }]
    }
    bucket_policy = json.dumps(bucket_policy)
    try:
        bucket.create(
            CreateBucketConfiguration={
                'LocationConstraint': 'ap-northeast-1'
                },
        )
        s3.put_bucket_policy(Bucket=folder_name, Policy=bucket_policy)
    except s3.meta.client.exceptions.BucketAlreadyExists:
        pass

    bucket.put_object(
        Key=f'{uuid.uuid4()}.jpeg',
        Body=convert_b64_string_to_bynary(image),
        ContentType='image/jpeg'
    )

    # 画像を送信
    domain_name = event.get('requestContext', {}).get('domainName')
    stage = event.get('requestContext', {}).get('stage')

    items = connections.scan(ProjectionExpression='connectionId').get('Items')
    if items is None:
        return {'statusCode': 500, 'body': 'something went wrong'}

    apigw_management = boto3.client('apigatewaymanagementapi',
                                    endpoint_url=F"https://{domain_name}/{stage}")
    for item in items:
        if item["connectionId"] != event.get('requestContext', {}).get('connectionId'):
            try:
                _ = apigw_management.post_to_connection(ConnectionId=item["connectionId"], Data=image)
            except:
                pass

    return {'statusCode': 200, 'body': 'ok'}


def convert_b64_string_to_bynary(s):
    return base64.b64decode(s)
